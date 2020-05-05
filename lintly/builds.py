import collections
import logging

from .constants import (
    FAIL_ON_ANY,
    ACTION_REVIEW_APPROVE,
    ACTION_REVIEW_COMMENT,
    ACTION_REVIEW_DO_NOTHING,
    ACTION_REVIEW_REQUEST_CHANGES,
    ACTION_REVIEW_USE_CHECKS
)

from .exceptions import NotPullRequestException
from .backends.github import GitHubBackend
from .backends.errors import GitClientError
from .formatters import build_pr_comment
from .parsers import PARSERS
from .patch import Patch
from .projects import Project


logger = logging.getLogger(__name__)


class LintlyBuild(object):

    def __init__(self, config, linter_output):
        self.config = config
        self.linter_output = linter_output

        self.project = Project(config.repo)

        context = config.context or "Lintly/{0}".format(config.format)
        self.git_client = GitHubBackend(token=config.api_key, project=self.project, context=context)

        # All violations found from the linting output
        self._all_violations = {}

        # Violations that are only caused by changes to the current PR
        self._diff_violations = {}

    @property
    def violations(self):
        """
        Returns either the diff violations or all violations depending on configuration.
        """
        return self._all_violations if self.config.fail_on == FAIL_ON_ANY else self._diff_violations

    @property
    def has_violations(self):
        return bool(self.violations)

    @property
    def introduced_issues_count(self):
        if self.violations is None:
            return 0
        return sum(len(item[1]) for item in self.violations.items())

    def execute(self):
        """
        Executes a new build on a project.
        """
        if not self.config.pr:
            raise NotPullRequestException

        logger.debug('Using the following configuration:')
        for name, value in self.config.as_dict().items():
            logger.debug('  - {}={}'.format(name, repr(value)))

        logger.info('Running Lintly against PR #{} for repo {}'.format(self.config.pr, self.project))

        parser = PARSERS.get(self.config.format)
        self._all_violations = parser.parse_violations(self.linter_output)
        logger.info('Lintly found violations in {} files'.format(len(self._all_violations)))

        diff = self.get_pr_diff()
        patch = self.get_pr_patch(diff)
        self._diff_violations = self.find_diff_violations(patch)
        logger.info('Lintly found diff violations in {} files'.format(len(self._diff_violations)))

        self.cleanup_previous_comments()
        self.submit_to_pr(patch)
        self.post_commit_status()

    def get_pr_diff(self):
        return self.git_client.get_pr_diff(self.config.pr)

    def get_pr_patch(self, diff):
        return Patch(diff)

    def cleanup_previous_comments(self):
        logger.info('Deleting old PR review comments')
        self.git_client.delete_pull_request_review_comments(self.config.pr)

        logger.info('Deleting old PR comment')
        self.git_client.delete_pull_request_comments(self.config.pr)

    def find_diff_violations(self, patch):
        """
        Uses the diff for this build to find changed lines that also have violations.
        """
        violations = collections.defaultdict(list)
        for line in patch.changed_lines:
            file_violations = self._all_violations.get(line['file_name'])
            if not file_violations:
                continue

            line_violations = [v for v in file_violations if v.line == line['line_number']]

            for v in line_violations:
                violations[line['file_name']].append(v)

        return violations

    def _get_pr_review_action(self):
        """
        Maps the expected action to be taken on this PR for the review step
        """
        action = ACTION_REVIEW_COMMENT

        if self.config.github_check_run_id and self.config.use_checks:
            action = ACTION_REVIEW_USE_CHECKS
        elif self.config.request_changes:
            # Use PR reviews
            if self.has_violations:
                action = ACTION_REVIEW_REQUEST_CHANGES
            else:
                action = ACTION_REVIEW_APPROVE

        return action

    def submit_to_pr(self, patch):
        """
        Submits violations to a PR. The submission may be a PR review (approve,
        request changes, or comment) or it may be a updates to a Check Run.
        """
        pr_review_action = self._get_pr_review_action()
        if pr_review_action == ACTION_REVIEW_DO_NOTHING:
            logger.info('No PR review action required on this Pull Request')
            return

        if pr_review_action == ACTION_REVIEW_USE_CHECKS:
            logger.info('Updating GitHub check run')
            description = self.get_result_description()
            self.git_client.create_check_run(
                self.config.commit_sha,
                description,
                self._diff_violations
            )
        else:
            self.submit_pr_review(patch, pr_review_action)

    def submit_pr_review(self, patch, pr_review_action):
        """
        Attempts to post a PR review. If posting the PR review fails because
        the bot account does not have permission to review the PR then
        simply revert to posting a regular PR comment.
        """

        post_pr_comment = True
        try:
            logger.info('Creating PR review')
            self.git_client.create_pull_request_review(
                self.config.pr,
                patch,
                self._diff_violations,
                pr_review_action
            )
            post_pr_comment = False
        except GitClientError as e:
            # TODO: Make `create_pull_request_review` raise an `UnauthorizedError`
            # so that we don't have to check for a specific message in the exception
            if 'Viewer does not have permission to review this pull request' in str(e):
                logger.warning("Could not post PR review (the account didn't have permission)")
                pass
            else:
                raise

        if post_pr_comment and pr_review_action in (ACTION_REVIEW_COMMENT, ACTION_REVIEW_REQUEST_CHANGES):
            logger.info('Creating PR comment')
            comment = build_pr_comment(self.config, self.violations)
            self.git_client.create_pull_request_comment(self.config.pr, comment)

    def get_result_description(self):
        plural = '' if self.introduced_issues_count == 1 else 's'
        return 'Pull Request introduced {} linting violation{}'.format(
            self.introduced_issues_count, plural)

    def post_commit_status(self):
        """
        Posts results to a commit status in GitHub if this build is for a pull request.
        """
        if self.violations:
            self._post_status('failure', self.get_result_description())
        else:
            self._post_status('success', 'Linting detected no new issues.')

    def _post_status(self, state, description):
        """
        Creates a GitHub status for this build's commit if enabled for the project.
        :param state: The state of the status (pending, error, failure, success)
        :param description: The description for the status
        """
        if self.config.post_status:
            logger.info('Commit statuses enabled')
            if self.config.commit_sha:
                logger.info('Posting {} status to commit SHA {}'.format(state, self.config.commit_sha))
                self.git_client.post_status(
                    state,
                    description,
                    sha=self.config.commit_sha
                )
            else:
                logger.warning('Cannot post commit status because no commit SHA has been '
                               'specified. Either use the --commit-sha CLI argument or '
                               'set the LINTLY_COMMIT_SHA environment variable.')
        else:
            logger.info('Commit statuses disabled')

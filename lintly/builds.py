import logging
import sys

from .exceptions import NotPullRequestException
from .git.github import GitHubBackend
from .git.errors import GitClientError, NotFoundError
from .formatters import build_pr_comment
from .parsers import PARSERS
from .projects import Project


logger = logging.getLogger(__name__)


class LintlyBuild(object):

    def __init__(self, config, linter_output):
        self.config = config
        self.linter_output = linter_output

        self.project = Project(config.repo)
        self.git_client = GitHubBackend(token=config.api_key, project=self.project)

        self.all_violations = {}

    @property
    def introduced_issues_count(self):
        if self.all_violations is None:
            return 0
        return sum(len(item[1]) for item in self.all_violations.items())

    def execute(self):
        """
        Executes a new build on a project.
        """
        if not self.config.pr:
            raise NotPullRequestException

        parser = PARSERS.get(self.config.format)
        self.all_violations = parser.parse_violations(self.linter_output)

        self.post_pr_comment()
        self.post_commit_status()

    def post_pr_comment(self):
        """
        Posts a comment to the GitHub PR if the diff results have issues.
        """
        post_pr_comment = True

        # Attempt to post a PR review. If posting the PR review fails because the bot account
        # does not have permission to review the PR then simply revert to posting a regular PR
        # comment.
        try:
            logger.info('Deleting old PR review comments')
            self.git_client.delete_pull_request_review_comments(self.config.pr)

            logger.info('Creating PR review')
            self.git_client.create_pull_request_review(self.config.pr, self.all_violations)
            post_pr_comment = False
        except GitClientError as e:
            # TODO: Make `create_pull_request_review` raise an `UnauthorizedError`
            # so that we don't have to check for a specific message in the exception
            if 'Viewer does not have permission to review this pull request' in str(e):
                logger.info("Could not post PR review (the bot account didn't have permission)")
                pass
            else:
                raise

        if post_pr_comment:
            # logger.info('Deleting old PR comment')
            # self.git_client.delete_pull_request_comments(self.config.pr, bot=self.bot.username)

            logger.info('Creating PR comment for')
            comment = build_pr_comment(self.config, self.all_violations)
            self.git_client.create_pull_request_comment(self.config.pr, comment)

    def post_commit_status(self):
        """
        Posts results to a commit status in GitHub if this build is for a pull request.
        """
        if self.all_violations:
            issue_word = 'issue' if self.introduced_issues_count == 1 else 'issues'
            description = 'Pull Request introduced {} quality {}'.format(
                self.introduced_issues_count, issue_word)
            self._post_status('failure', description)
        else:
            self._post_status('success', 'Linting introduced no new issues.')

    def _post_status(self, state, description):
        """
        Creates a GitHub status for this build's commit if enabled for the project.
        :param state: The state of the status (pending, error, failure, success)
        :param description: The description for the status
        """
        if self.config.post_status:
            logger.info('Commit statuses enabled')
            try:
                logger.info('Posting status to commit SHA {}'.format(self.config.commit_sha))
                self.git_client.post_status(
                    state,
                    description,
                    sha=self.config.commit_sha
                )
                logger.info('Posted commit status')
            except NotFoundError:
                # Silently fail if commit statuses can't be created
                logger.warning('Could not create status because project could not be found')
        else:
            logger.info('Commit statuses disabled')

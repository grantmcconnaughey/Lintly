from __future__ import absolute_import

import functools
import json
import logging
import requests

from github import GithubException, UnknownObjectException, Github

from lintly.constants import LINTLY_IDENTIFIER
from lintly.formatters import (
    build_pr_review_line_comment,
    build_pr_review_body,
    build_check_line_comment
)
from lintly.constants import (
    ACTION_REVIEW_REQUEST_CHANGES,
    ACTION_REVIEW_COMMENT,
    ACTION_REVIEW_APPROVE
)

from .base import BaseGitBackend
from .errors import NotFoundError, GitClientError
from .objects import PullRequest


logger = logging.getLogger(__name__)

# Get 100 items at a time so that we can make fewer API requests
DEFAULT_PER_PAGE = 100

GITHUB_API_HEADER = 'application/vnd.github.v3+json'
GITHUB_API_PR_REVIEW_HEADER = 'application/vnd.github.black-cat-preview+json'
GITHUB_DIFF_HEADER = 'application/vnd.github.3.diff'
GITHUB_CHECKS_HEADER = 'application/vnd.github.antiope-preview+json'
GITHUB_USER_AGENT = 'Lintly'

ANNOTATION_LEVEL_WARNING = 'warning'
ANNOTATION_LEVEL_FAILURE = 'failure'


def translate_github_exception(func):
    """
    Decorator to catch GitHub-specific exceptions and raise them as GitClientError exceptions.
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnknownObjectException as e:
            logger.exception('GitHub API 404 Exception')
            raise NotFoundError(str(e))
        except GithubException as e:
            logger.exception('GitHub API Exception')
            raise GitClientError(str(e))

    return _wrapper


class GitHubAPIClient:
    """
    A wrapper class for making calls directly to the GitHub API and returning the results
    as JSON or a string (depending on the Content-Type header).
    """

    base_url = 'https://api.github.com'

    def __init__(self, token=None):
        self.token = token

    def get_headers(self):
        headers = {
            'Accept': GITHUB_API_HEADER,
            'Authorization': 'token {}'.format(self.token),
            'User-Agent': GITHUB_USER_AGENT,
        }
        return headers

    def post(self, url, data=None, headers=None):
        return self._do_request('post', url, json.dumps(data), headers)

    def get(self, url, data=None, headers=None):
        return self._do_request('get', url, data, headers)

    def put(self, url, data=None, headers=None):
        return self._do_request('put', url, json.dumps(data), headers)

    def patch(self, url, data=None, headers=None):
        return self._do_request('patch', url, json.dumps(data), headers)

    def _do_request(self, method, url, data=None, extra_headers=None):
        if data is None:
            data = dict()
        if extra_headers is None:
            extra_headers = dict()

        full_url = self.base_url + url
        headers = self.get_headers()
        headers.update(extra_headers)

        logger.debug('Sending a {} request to {}'.format(method, url))

        response = getattr(requests, method.lower())(full_url, data=data, headers=headers)
        if 200 <= response.status_code < 300:
            if 'application/json' in response.headers['Content-Type']:
                return response.json()
            else:
                return response.content
        elif response.status_code == 404:
            raise NotFoundError(response.content, status_code=response.status_code)
        else:
            raise GitClientError(response.content, status_code=response.status_code)


class GitHubBackend(BaseGitBackend):

    supports_pr_reviews = True

    def __init__(self, token, project, context):
        super(GitHubBackend, self).__init__(token, project)
        self.client = Github(token, user_agent=GITHUB_USER_AGENT, per_page=DEFAULT_PER_PAGE)
        self.context = context

    def _should_delete_comment(self, comment):
        return LINTLY_IDENTIFIER in comment.body

    @translate_github_exception
    def get_pull_request(self, pr):
        repo = self.client.get_repo(self.project.full_name)
        gh_pull = repo.get_pull(int(pr))

        pull_request = PullRequest(
            number=gh_pull.number,
            url=gh_pull.url,
            head_ref=gh_pull.head.ref,
            head_sha=gh_pull.head.sha,
            base_ref=gh_pull.base.ref,
            base_sha=gh_pull.base.sha
        )

        return pull_request

    @translate_github_exception
    def create_pull_request_comment(self, pr, comment):
        repo = self.client.get_repo(self.project.full_name)
        pull_request = repo.get_pull(int(pr))

        pull_request.create_issue_comment(
            body=comment
        )

    @translate_github_exception
    def delete_pull_request_comments(self, pr):
        repo = self.client.get_repo(self.project.full_name)
        pull_request = repo.get_issue(int(pr))
        for comment in pull_request.get_comments():
            if self._should_delete_comment(comment):
                comment.delete()

    def get_pr_diff(self, pr):
        client = GitHubAPIClient(token=self.token)
        client.base_url = 'https://api.github.com'
        diff_url = '/repos/{owner}/{repo_name}/pulls/{pr_number}'.format(
            owner=self.project.owner_login,
            repo_name=self.project.name,
            pr_number=pr
        )

        diff = client.get(diff_url, headers={'Accept': GITHUB_DIFF_HEADER})

        return diff.decode('utf-8')

    def _get_event(self, review_action):
        if review_action == ACTION_REVIEW_COMMENT:
            return 'COMMENT'
        elif review_action == ACTION_REVIEW_REQUEST_CHANGES:
            return 'REQUEST_CHANGES'
        elif review_action == ACTION_REVIEW_APPROVE:
            return 'APPROVE'

    def create_pull_request_review(self, pr, patch, all_violations, pr_review_action):
        comments = []
        for file_path in all_violations:
            violations = all_violations[file_path]

            # https://developer.github.com/v3/pulls/comments/#input
            for violation in violations:
                patch_position = patch.get_patch_position(file_path, violation.line)
                if patch_position is not None:
                    comments.append({
                        'path': file_path,
                        'position': patch_position,
                        'body': build_pr_review_line_comment(violation)
                    })

        client = GitHubAPIClient(token=self.token)
        data = {
            'body': build_pr_review_body(all_violations),
            'event': self._get_event(pr_review_action),
            'comments': comments,
        }

        url = '/repos/{owner}/{repo_name}/pulls/{pr_number}/reviews'.format(
            owner=self.project.owner_login,
            repo_name=self.project.name,
            pr_number=pr
        )
        client.post(url, data, headers={'Accept': GITHUB_API_PR_REVIEW_HEADER})

    @translate_github_exception
    def delete_pull_request_review_comments(self, pr):
        repo = self.client.get_repo(self.project.full_name)
        pull_request = repo.get_pull(int(pr))
        for comment in pull_request.get_review_comments():
            if self._should_delete_comment(comment):
                comment.delete()

    def post_status(self, state, description, sha, target_url=''):
        url = '/repos/{owner}/{repo_name}/statuses/{sha}'.format(
            owner=self.project.owner_login, repo_name=self.project.name, sha=sha)

        # Using wrapper client since PyGitHub makes unnecessary API calls
        client = GitHubAPIClient(token=self.token)
        data = {
            'state': state,
            'description': description,
            'target_url': target_url,
            'context': self.context
        }
        client.post(url, data)

    def create_check_run(self, commit_sha, description, violations):
        url = '/repos/{owner}/{repo_name}/check-runs'.format(
            owner=self.project.owner_login, repo_name=self.project.name)
        annotations = self._get_check_annotations(violations)

        client = GitHubAPIClient(token=self.token)
        data = {
            'name': self.context,
            'conclusion': 'success' if len(annotations) == 0 else 'failure',
            'head_sha': commit_sha,
            'output': {
                'title': description,
                'summary': description,
                'annotations': annotations
            }
        }
        response = client.post(url, data, headers={'Accept': GITHUB_CHECKS_HEADER})
        return response.get('id')

    # https://developer.github.com/v3/checks/runs/#update-a-check-run
    def update_check_run(self, check_run_id, description, violations):
        url = '/repos/{owner}/{repo_name}/check-runs/{check_run_id}'.format(
            owner=self.project.owner_login, repo_name=self.project.name, check_run_id=check_run_id)

        # PyGitHub does not support the Checks API
        client = GitHubAPIClient(token=self.token)
        data = {
            'output': {
                'title': description,
                'summary': description,
                'annotations': self._get_check_annotations(violations)
            }
        }
        client.patch(url, data, headers={'Accept': GITHUB_CHECKS_HEADER})

    def _get_check_annotations(self, violations):
        annotations = []
        for file_path in violations:
            file_violations = violations[file_path]

            # https://developer.github.com/v3/pulls/comments/#input
            for violation in file_violations:
                annotations.append({
                    'annotation_level': 'warning',
                    'path': file_path,
                    'start_line': violation.line,
                    'end_line': violation.line,
                    'message': build_check_line_comment(violation)
                })
        return annotations

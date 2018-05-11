from __future__ import absolute_import

import functools
import json
import logging
import requests

from github import GithubException, UnknownObjectException, Github

from lintly.formatters import build_pr_review_line_comment
from lintly.patch import Patch

from .base import BaseGitBackend
from .errors import NotFoundError, GitClientError
from .objects import Repository, Owner, PullRequest


logger = logging.getLogger(__name__)

# Get 100 items at a time so that we can make fewer API requests
DEFAULT_PER_PAGE = 100

GITHUB_API_HEADER = 'application/vnd.github.v3+json'
GITHUB_API_PR_REVIEW_HEADER = 'application/vnd.github.black-cat-preview+json'
GITHUB_DIFF_HEADER = 'application/vnd.github.3.diff'
GITHUB_USER_AGENT = 'Lintly'


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

    def _do_request(self, method, url, data=None, extra_headers=None):
        if data is None:
            data = dict()
        if extra_headers is None:
            extra_headers = dict()

        full_url = self.base_url + url
        headers = self.get_headers()
        headers.update(extra_headers)

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

    def __init__(self, token, project):
        super(GitHubBackend, self).__init__(token, project)
        self.client = get_github_client(token)

    def _github_repo_to_repository(self, gh_repo):
        """
        Organizations attached to a repository do not have their email or name fields filled in.
        """
        gh_owner = gh_repo.owner
        owner = Owner(
            login=gh_owner.login,
            type_=gh_owner.type,
        )
        repo = Repository(
            name=gh_repo.name,
            full_name=gh_repo.full_name,
            clone_url=gh_repo.clone_url,
            default_branch=gh_repo.default_branch,
            private=gh_repo.private,
            description=gh_repo.description,
            external_url=gh_repo.html_url,
            homepage=gh_repo.homepage,
            admin=gh_repo.permissions.admin,
            owner=owner
        )
        return repo

    def _github_owner_to_owner(self, gh_owner):
        owner = Owner(
            login=gh_owner.login,
            name=gh_owner.name,
            email=gh_owner.email,
            type_=gh_owner.type
        )
        return owner

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
    def delete_pull_request_comments(self, pr, bot):
        repo = self.client.get_repo(self.project.full_name)
        pull_request = repo.get_issue(int(pr))
        for comment in pull_request.get_comments():
            if comment.user.login == bot:
                comment.delete()

    def _get_pr_diff(self, pr):
        client = GitHubAPIClient(token=self.token)
        client.base_url = 'https://github.com'
        diff_url = '/{owner}/{repo_name}/pull/{pr_number}.diff'.format(
            owner=self.project.owner_login,
            repo_name=self.project.name,
            pr_number=pr
        )

        diff = client.get(diff_url, headers={'Accept': GITHUB_DIFF_HEADER})

        return diff.decode('utf-8')

    def create_pull_request_review(self, pr, all_violations):
        diff = self._get_pr_diff(pr)

        patch = Patch(diff)

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
            'body': 'Lintly has detected code quality issues in this pull request.',
            'event': 'COMMENT',
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
            # TODO: Come up with some identifier than indicates the PR review
            # comment came from Lintly and therefore can be deleted
            if ':frowning:' in comment.body:
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
            'context': 'Lintly'
        }
        client.post(url, data)

    @translate_github_exception
    def user_is_collaborator(self, full_name, user_login):
        repo = self.client.get_repo(full_name)
        return repo.has_in_collaborators(user_login)


def get_github_client(token):
    """
    Returns a Github client object for a given token, user, or project.
    :return: The Github client
    """
    return Github(token, user_agent=GITHUB_USER_AGENT, per_page=DEFAULT_PER_PAGE)

import functools
import json
import logging

import gitlab
import requests
from gitlab.v4.objects import VISIBILITY_PUBLIC

from .base import BaseGitBackend
from .errors import (
    NotSupportedError, NotFoundError, GitClientError, UnauthorizedError
)
from .objects import PullRequest, Commit, Repository, Owner


logger = logging.getLogger(__name__)

# Get 100 items at a time so that we can make fewer API requests
DEFAULT_PER_PAGE = 100

GITLAB_URL = 'https://gitlab.com'

GITLAB_API_VERSION = 4


def translate_gitlab_exception(func):
    """
    Decorator to catch GitLab-specific exceptions and raise them as GitClientError exceptions.
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except gitlab.GitlabError as e:
            status_to_exception = {
                401: UnauthorizedError,
                404: NotFoundError,
            }

            exc_class = status_to_exception.get(e.response_code, GitClientError)
            raise exc_class(str(e), status_code=e.response_code)

    return _wrapper


class GitLabAPIClient:
    """
    A wrapper class for making calls directly to the GitHub API and returning the results
    as JSON or a string (depending on the Content-Type header).
    """

    base_url = f'{GITLAB_URL}/api/v{GITLAB_API_VERSION}'

    def __init__(self, token=None, user=None, project=None):
        self.user = user
        self.project = project
        self.token = choose_gitlab_token(token=token, user=user, project=project)

    def __repr__(self):
        token = 'REDACTED' if self.token else 'None'
        return 'GitLabAPIClient(token={}, user={}, project={})'.format(
            token, self.user, self.project)

    def get_headers(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
        }
        return headers

    def post(self, url, data=None, headers=None):
        return self._do_request('post', url, json.dumps(data), headers)

    def get(self, url, data=None, headers=None):
        return self._do_request('get', url, data, headers)

    def delete(self, url, data=None, headers=None):
        return self._do_request('delete', url, json.dumps(data), headers)

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


class GitLabBackend(BaseGitBackend):

    supports_pr_reviews = False

    def __init__(self, project=None, user=None, token=None):
        super().__init__(project, user, token)
        self.client = get_gitlab_client(self.project, self.user, token=token)

    def _gitlab_owner_to_owner(self, gl_owner):
        owner = Owner(
            login=gl_owner['id'],
            name=gl_owner['name'],
        )
        return owner

    def _gitlab_group_to_owner(self, gl_group):
        owner = Owner(
            login=gl_group.full_path,
            name=gl_group.path,
        )
        return owner

    def _gitlab_project_to_repository(self, gl_project):
        owner = self._gitlab_owner_to_owner(gl_project.owner)
        repo = Repository(
            service='gitlab',
            name=gl_project.name,
            full_name=gl_project.path_with_namespace,
            clone_url=gl_project.http_url_to_repo,
            default_branch=gl_project.default_branch,
            private=gl_project.visibility != VISIBILITY_PUBLIC,
            description=gl_project.description,
            external_url=gl_project.web_url,
            admin=gl_project.permissions['project_access']['access_level'] >= gitlab.MASTER_ACCESS,
            owner=owner
        )
        return repo

    @translate_gitlab_exception
    def get_pull_request(self, pr):
        project = self.client.projects.get(self.project.full_name)
        mr = project.mergerequests.list(iid=pr)[0]
        target_sha = self.get_latest_branch_commit_sha(mr.target_branch)
        pull_request = PullRequest(
            number=pr,
            url=mr.web_url,
            head_ref=mr.source_branch,
            head_sha=mr.sha,
            base_ref=mr.target_branch,
            base_sha=target_sha
        )
        return pull_request

    @translate_gitlab_exception
    def create_pull_request_comment(self, pr, comment):
        project = self.client.projects.get(self.project.full_name)
        mr = project.mergerequests.list(iid=pr)[0]
        mr.notes.create({'body': comment})

    @translate_gitlab_exception
    def delete_pull_request_comments(self, pr, bot):
        project = self.client.projects.get(self.project.full_name)
        mr = project.mergerequests.list(iid=pr)[0]
        client = GitLabAPIClient(self.token, self.user, self.project)
        for note in mr.notes.list(all=True, per_page=DEFAULT_PER_PAGE):
            if note.author.username == bot:
                url = '/projects/{project_id}/merge_requests/{mr_id}/notes/{note_id}'.format(
                    project_id=project.id, mr_id=mr.id, note_id=note.id
                )
                client.delete(url)

    @translate_gitlab_exception
    def create_pull_request_review(self, build):
        raise NotSupportedError()

    @translate_gitlab_exception
    def delete_pull_request_review_comments(self, pr, bot):
        raise NotSupportedError()

    @translate_gitlab_exception
    def post_status(self, state, description, sha, target_url):
        # TODO: Fix this ugliness...
        if state == 'failure':
            state = 'failed'
        project = self.client.projects.get(self.project.full_name)
        gl_commit = project.commits.get(sha)
        gl_commit.statuses.create({'state': state,
                                   'description': description,
                                   'target_url': target_url,
                                   'name': 'Lintly'})

    @translate_gitlab_exception
    def user_is_collaborator(self, full_name, user_login):
        project = self.client.projects.get(self.project.full_name)
        return project.permissions['project_access']['access_level'] >= gitlab.DEVELOPER_ACCESS


def get_gitlab_client(token=None):
    """
    Returns a GitLab client object for a given token, user, or project.
    :return: The GitLab client
    """
    return Gitlab(GITLAB_URL, token, api_version=str(GITLAB_API_VERSION))

import logging
import os
import re

from . import git


logger = logging.getLogger(__name__)


# https://docs.travis-ci.com/user/environment-variables
class Travis(object):

    @property
    def pr(self):
        pr = os.environ['TRAVIS_PULL_REQUEST']
        if pr == 'false':
            return None
        else:
            return pr

    @property
    def repo(self):
        return os.environ['TRAVIS_REPO_SLUG']

    @property
    def commit_sha(self):
        return os.environ['TRAVIS_PULL_REQUEST_SHA']


# https://circleci.com/docs/1.0/environment-variables
class CircleCI(object):

    @property
    def pr(self):
        return os.environ['CIRCLE_PR_NUMBER']

    @property
    def repo(self):
        return os.environ['CIRCLE_PROJECT_USERNAME'] + '/' + os.environ['CIRCLE_PROJECT_REPONAME']

    @property
    def commit_sha(self):
        return os.environ['CIRCLE_SHA1']


# https://www.appveyor.com/docs/environment-variables
class AppVeyor(object):

    @property
    def pr(self):
        return os.environ['APPVEYOR_PULL_REQUEST_NUMBER']

    @property
    def repo(self):
        return os.environ['APPVEYOR_REPO_NAME']

    @property
    def commit_sha(self):
        return os.environ['APPVEYOR_REPO_COMMIT']


# http://docs.shippable.com/ci/env-vars/#stdEnv
class Shippable(object):

    @property
    def pr(self):
        return os.environ['PULL_REQUEST']

    @property
    def repo(self):
        return os.environ['SHIPPABLE_REPO_SLUG']

    @property
    def commit_sha(self):
        return os.environ['COMMIT']


# https://semaphoreci.com/docs/available-environment-variables.html
class Semaphore(object):

    @property
    def pr(self):
        return os.environ['PULL_REQUEST_NUMBER']

    @property
    def repo(self):
        return os.environ['SEMAPHORE_REPO_SLUG']

    @property
    def commit_sha(self):
        return os.environ['REVISION']


# https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
class CodeBuild(object):

    REPO_REGEX = r'.+github\.com/(?P<repo>.+\/.+)\.git'

    @property
    def pr(self):
        # CODEBUILD_SOURCE_VERSION=pr/1
        return os.environ['CODEBUILD_SOURCE_VERSION'].split('/')[1]

    @property
    def repo(self):
        # CODEBUILD_SOURCE_REPO_URL=https://github.com/owner/repo.git
        match = re.match(self.REPO_REGEX, os.environ['CODEBUILD_SOURCE_REPO_URL'])
        return match.group('repo')

    @property
    def commit_sha(self):
        return git.head()


# https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables
# Note: variables with '.' in the name will have dot replaced with underscore
# in actual environment
class AzureDevOps(object):

    @property
    def pr(self):
        return os.environ.get('SYSTEM_PULLREQUEST_PULLREQUESTNUMBER', None)

    @property
    def repo(self):
        return os.environ['BUILD_REPOSITORY_ID']

    @property
    def commit_sha(self):
        return os.environ['BUILD_SOURCEVERSION']


def find_ci_provider():
    ci_providers = [
        ('TRAVIS', Travis),
        ('CIRCLECI', CircleCI),
        ('APPVEYOR', AppVeyor),
        ('SHIPPABLE', Shippable),
        ('SEMAPHORE', Semaphore),
        ('CODEBUILD_BUILD_ID', CodeBuild),
        ('AZURE_HTTP_USER_AGENT', AzureDevOps),
    ]

    for ci_env_var, ci_cls in ci_providers:
        if ci_env_var in os.environ:
            logger.info('CI {} detected'.format(ci_cls.__name__))
            return ci_cls()
    else:
        logger.info('No CI detected')
        return None

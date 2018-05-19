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


def find_ci_provider():
    if 'TRAVIS' in os.environ:
        logger.info('Travis CI detected')
        return Travis()
    elif 'CIRCLECI' in os.environ:
        logger.info('Circle CI detected')
        return CircleCI()
    elif 'APPVEYOR' in os.environ:
        logger.info('AppVeyor detected')
        return AppVeyor()
    elif 'SHIPPABLE' in os.environ:
        logger.info('Shippable detected')
        return Shippable()
    elif 'SEMAPHORE' in os.environ:
        logger.info('Semaphore detected')
        return Semaphore()
    elif 'CODEBUILD_BUILD_ID' in os.environ:
        logger.info('CodeBuild detected')
        return CodeBuild()
    else:
        logger.info('No CI detected')
        return None

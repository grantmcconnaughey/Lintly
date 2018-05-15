import logging
import os


logger = logging.getLogger(__name__)


# https://docs.travis-ci.com/user/environment-variables
class Travis(object):

    @property
    def pr(self):
        return os.environ['TRAVIS_PULL_REQUEST']

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
    else:
        logger.info('No CI detected')
        return None

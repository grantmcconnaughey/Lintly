import logging
import os


logger = logging.getLogger(__name__)


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
    else:
        logger.info('No CI detected')
        return None

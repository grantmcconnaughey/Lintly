import logging
import os


logger = logging.getLogger(__name__)


class Travis:

    @property
    def pr(self):
        return os.environ['TRAVIS_PULL_REQUEST']

    @property
    def repo(self):
        return os.environ['TRAVIS_REPO_SLUG']

    @property
    def commit_sha(self):
        return os.environ['TRAVIS_COMMIT']


class CircleCI:

    @property
    def pr(self):
        return os.environ['CIRCLE_PR_NUMBER']

    @property
    def repo(self):
        return os.environ['CIRCLE_PROJECT_USERNAME'] + '/' + os.environ['CIRCLE_PROJECT_REPONAME']

    @property
    def commit_sha(self):
        return os.environ['CIRCLE_SHA1']


def find_ci_provider():
    if 'TRAVIS' in os.environ:
        logger.info('Using Travis CI')
        return Travis()
    elif 'CIRCLECI' in os.environ:
        logger.info('Using Circle CI')
        return CircleCI()
    else:
        logger.info('No CI detected')
        return None

import ci
import os

REDACTED = '********'


class Config(object):
    """A Config object that knows how to return configuration from the CLI or Continuous Integration services"""

    def __init__(self, cli_config):
        self.cli_config = cli_config

    def as_dict(self):
        return {
            'pr': self.pr,
            'repo': self.repo,
            'commit_sha': self.commit_sha,
            'api_key': REDACTED,
            'format': self.format,
            'fail_on': self.fail_on,
            'post_status': self.post_status,
            'request_changes': self.request_changes,
            'github_check_run_id': self.github_check_run_id,
        }

    @property
    def pr(self):
        return self.cli_config['pr'] or ci.pr()

    @property
    def repo(self):
        return self.cli_config['repo'] or ci.repo()

    @property
    def commit_sha(self):
        return self.cli_config['commit_sha'] or ci.commit_sha()

    @property
    def context(self):
        return self.cli_config['context']

    @property
    def api_key(self):
        return self.cli_config['api_key']

    @property
    def format(self):
        return self.cli_config['format']

    @property
    def fail_on(self):
        return self.cli_config['fail_on']

    @property
    def post_status(self):
        return self.cli_config['post_status']

    @property
    def request_changes(self):
        return self.cli_config['request_changes']

    @property
    def github_check_run_id(self):
        """The Check Run ID from GitHub Actions.

        https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
        """
        return os.environ.get('GITHUB_RUN_ID')

    @property
    def use_checks(self):
        return self.cli_config['use_checks']

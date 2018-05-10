# Merge config with configuration pulled from CI providers


class Config(object):
    """A Config object that knows how to return configuration from the CLI or Continuous Integration services"""

    def __init__(self, cli_config, ci=None):
        self.cli_config = cli_config
        self.ci = ci

    @property
    def pr(self):
        return self.cli_config['pr'] or getattr(self.ci, 'pr')

    @property
    def repo(self):
        return self.cli_config['repo'] or getattr(self.ci, 'repo')

    @property
    def api_key(self):
        return self.cli_config['api_key']

    @property
    def format(self):
        return self.cli_config['format']

    @property
    def site_url(self):
        return self.cli_config['site_url']

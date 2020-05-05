import logging
import logging.config
import sys

import click

from .builds import LintlyBuild
from .config import Config
from .constants import FAIL_ON_ANY, FAIL_ON_NEW
from .exceptions import NotPullRequestException
from .parsers import PARSERS


logger = logging.getLogger(__name__)


@click.command()
@click.option('--api-key',
              envvar='LINTLY_API_KEY',
              help='The GitHub API key to use for commenting on PRs (required)')
@click.option('--repo',
              envvar='LINTLY_REPO',
              help='The GitHub repo name in the format {owner}/{repo}')
@click.option('--pr',
              envvar='LINTLY_PR',
              help='The pull request number for this build (required)')
@click.option('--commit-sha',
              envvar='LINTLY_COMMIT_SHA',
              help='The commit Lintly is running against (required)')
@click.option('--format',
              envvar='LINTLY_FORMAT',
              type=click.Choice(list(PARSERS.keys())),
              default='flake8',
              help='The linting output format Lintly should expect to receive. Default "flake8"')
@click.option('--context',
              help='Override the commit status context')
@click.option('--fail-on',
              envvar='LINTLY_FAIL_ON',
              type=click.Choice([FAIL_ON_ANY, FAIL_ON_NEW]),
              default=FAIL_ON_ANY,
              help=('Whether Lintly should fail if any violations are detected '
                    'or only if new violations are detected. Default "any"'))
@click.option('--post-status/--no-post-status',
              default=True,
              help='Used to determine if Lintly should post a PR status to GitHub. Default true')
@click.option('--request-changes/--no-request-changes',
              default=True,
              help=('Whether Lintly should post violations as a PR request for '
                    'changes instead of a comment review. Default true'))
@click.option('--use-checks/--no-use-checks',
              default=False,
              help=('Whether Lintly should try to use the GitHub Checks API '
                    'to report on changes requested. This only works when '
                    'running in GitHub Actions. Default false'))
@click.option('--log',
              is_flag=True,
              help='Send Lintly debug logs to the console. Default false')
@click.option('--exit-zero/--no-exit-zero', default=False,
              help=('Whether Lintly should exit with error code indicating '
                    'amount of violations or not. Default false'))
def main(**options):
    """Slurp up linter output and send it to a GitHub PR review."""
    configure_logging(log_all=options.get('log'))

    stdin_stream = click.get_text_stream('stdin')
    stdin_text = stdin_stream.read()

    click.echo(stdin_text)

    config = Config(options)

    build = LintlyBuild(config, stdin_text)
    try:
        build.execute()
    except NotPullRequestException:
        logger.info('Not a PR. Lintly is exiting.')
        sys.exit(0)

    exit_code = 0
    # Exit with the number of files that have violations
    if not options['exit_zero']:
        exit_code = len(build.violations)
    sys.exit(exit_code)


def configure_logging(log_all=False):
    log_level = 'DEBUG' if log_all else 'WARNING'
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': 'Lintly: %(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'lintly': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True
            }
        }
    })

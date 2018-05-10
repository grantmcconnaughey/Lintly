import logging

import click

from .ci import find_ci_provider
from .config import Config
from .git.github import GitHubBackend
from .git.errors import GitClientError
from .formatters import build_pr_comment
from .parsers import PARSER_FORMATS, parse_violations
from .projects import Project


logger = logging.getLogger(__name__)


@click.command()
@click.option('--pr',
              envvar='LINTLY_PR',
              help='The pull request number for this build')
@click.option('--api-key',
              envvar='LINTLY_API_KEY',
              help='The GitHub API key to use for commenting on PRs')
@click.option('--repo',
              envvar='LINTLY_REPO',
              help='The GitHub repo name in the format {owner}/{repo}')
@click.option('--format',
              envvar='LINTLY_FORMAT',
              type=click.Choice(list(PARSER_FORMATS.keys())),
              default='unix',
              help='The linting output format Lintly should expect to receive')
@click.option('--site-url',
              envvar='LINTLY_SITE_URL',
              default='github.com',
              help='The GitHub URL to use. Defaults to github.com. Override this if you use GitHub Enterprise.')
def main(**options):
    """Slurp up linter output and send it to a GitHub PR review."""
    stdin_stream = click.get_text_stream('stdin')
    stdin_text = stdin_stream.read()

    ci = find_ci_provider()
    config = Config(options, ci=ci)

    # Parse violations from stdin
    parser_regex = PARSER_FORMATS.get(config.format)
    all_violations = parse_violations(stdin_text, regex=parser_regex)

    # Post a PR to GitHub
    post_pr_comment(config, all_violations)


def post_pr_comment(config, violations):
    """
    Posts a comment to the GitHub PR if the diff results have issues.
    """
    project = Project(config.repo)
    git_client = GitHubBackend(token=config.api_key, project=project)

    post_pr_comment = True

    # Attempt to post a PR review. If posting the PR review fails because the bot account
    # does not have permission to review the PR then simply revert to posting a regular PR
    # comment.
    try:
        # TODO: Allow configuration to post PR comment or review
        if False:
            logger.info('Deleting old PR review comments')
            git_client.delete_pull_request_review_comments(
                config.pr, bot=self.bot.username)

            logger.info('Creating PR review')
            git_client.create_pull_request_review(config.pr)
            post_pr_comment = False
    except GitClientError as e:
        # TODO: Make `create_pull_request_review` raise an `UnauthorizedError`
        # so that we don't have to check for a specific message in the exception
        if 'Viewer does not have permission to review this pull request' in str(e):
            logger.info("Could not post PR review (the bot account didn't have permission)")
            pass
        else:
            raise

    if post_pr_comment:
        # logger.info('Deleting old PR comment')
        # git_client.delete_pull_request_comments(config.pr, bot=self.bot.username)

        logger.info('Creating PR comment for')
        comment = build_pr_comment(config, violations)
        git_client.create_pull_request_comment(config.pr, comment)

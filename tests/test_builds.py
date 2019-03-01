import pytest

from lintly import builds
from lintly.config import Config

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


@pytest.fixture(
    params=[
        # format, context, expected_context
        ("black", None, "Lintly/black"),
        ("cfn-lint", None, "Lintly/cfn-lint"),
        ("flake8", "my-flake8-context", "my-flake8-context"),
    ]
)
def format_and_context(request):
    return request.param


@pytest.fixture
def config(format_and_context):
    cli_config = {
        "api_key": "api_key",
        "repo": "owner/repo",
        "pr": 1,
        "format": format_and_context[0],
        "commit_sha": "xyz123notarealsha",
        "context": format_and_context[1],
        "post_status": True,
    }

    return Config(cli_config)


@pytest.fixture
def GitHubBackend(monkeypatch):
    ghb_mock = Mock()
    monkeypatch.setattr(builds, "GitHubBackend", ghb_mock)
    return ghb_mock


def test_lintly_build(config, GitHubBackend, format_and_context):
    builds.LintlyBuild(config, "Some linter output")
    assert GitHubBackend.call_args[1]["context"] == format_and_context[2]

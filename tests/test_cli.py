import pytest
from click.testing import CliRunner
from lintly import cli






@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert not result.exception
    assert 'Usage' in result.output


# def test_cli_with_option(runner):
#     result = runner.invoke(cli.main, ['--as-cowboy'])
#     assert not result.exception
#     assert result.exit_code == 0
#     assert result.output.strip() == 'It works!'


# def test_cli_with_arg(runner):
#     result = runner.invoke(cli.main, ['Grant'])
#     assert result.exit_code == 0
#     assert not result.exception
#     assert result.output.strip() == 'It works!'

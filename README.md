# Lintly

[![Build Status](https://travis-ci.org/grantmcconnaughey/Lintly.svg?branch=master)](https://travis-ci.org/grantmcconnaughey/Lintly) [![codecov](https://codecov.io/gh/grantmcconnaughey/lintly/branch/master/graph/badge.svg)](https://codecov.io/gh/grantmcconnaughey/lintly)

A Continuous Integration CLI that slurps up linter output and sends it to a GitHub PR review.

## Usage

First, `pip` install lintly:

    $ pip install lintly

> Lintly requires Python 2.7 or 3.4+.

Next, set the `LINTLY_API_KEY` environment variable to your GitHub API Key:

    $ export LINTLY_API_KEY="12345"

Finally, pipe the output of your linter to the `lintly` script:

    $ flake8 | lintly

Now you will see linting errors in your Pull Requests! Nifty!

![Lintly used on a pull request](./example.png)

## Supported Git Services

- GitHub

> Support for GitLab and Bitbucket is planned.

## Supported Linters

- [flake8](http://flake8.pycqa.org/en/latest/)
    ```
    $ flake8 | lintly --format=flake8
    ```
- [black](https://black.readthedocs.io/en/stable/)
    ```
    $ black --check | lintly --format=black
    ```
- [pylint](https://www.pylint.org/)
    - For pylint you must use the `json` output format.
    ```
    $ pylint . --output-format=json | lintly --format=pylint-json
    ```
- [eslint](https://eslint.org/)
    ```
    $ eslint . | lintly --format=eslint
    ```
- [stylelint](https://stylelint.io/)
    ```
    $ stylelint . | lintly --format=stylelint
    ```

- [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint)
    ```
    $ cfn-lint template.yaml | lintly --format=cfn-lint
    ```

Additional linters can be added by modifying the `lintly/parsers.py` module.

## Configuration

At a minimum Lintly needs to know the following information to determine how to post the correct GitHub PR Review:

- **GitHub API key** (`--api-key` or `LINTLY_API_KEY` env var)
    - Generate your own [API Key here](https://github.com/settings/tokens/new). The API key will need the following GitHub scopes:
        - `repo:status` so that Lintly can post commit statuses on PRs.
        - `public_repo` so that Lintly can create pull request reviews on public repos.
        - `repo` so that Lintly can create pull request reviews on private repos.
- **GitHub repository** (`--repo` or `LINTLY_REPO` env var)
    - This is your repository in the format `grantmcconnaughey/lintly`.
    > Note: Most Continuous Integration platforms will provide this value automatically.
- **Pull Request number** (`--pr` or `LINTLY_PR` env var)
    > Note: Most Continuous Integration platforms will provide this value automatically.

These configuration values can be provided to Lintly via environment variables or by being passed in as arguments to the Lintly CLI. A list of all configuration values can be viewed by running `lintly --help`.

## Supported Continuous Integration platforms

Lintly works out of the box with the following Continuous Integration platforms:

- [Travis CI](#travis-ci)
- Circle CI
- GitHub Actions
- Drone CI
- AppVeyor
- Shippable
- Semaphore
- AWS CodeBuild
- Azure DevOps

When using these Continuous Integration platforms the repository, pull request number, and commit SHA will be detected automatically.

### Travis CI example

To use with Lintly with Travis CI, add the following to your `.travis.yml` config file:

```yml
language: python

jobs:
  include:
    - stage: lint
      install: pip install lintly
      script: flake8 | lintly --format=flake8

stages:
  - lint
```

## To-Do

- Add support for GitHub Enterprise custom GitHub URLs
- Configuration to post either a PR comment or PR review
- Link to Build URL from commit status
- Support for config file
- Auto-detect linters
- GitLab support

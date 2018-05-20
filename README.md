# Lintly

[![Build Status](https://travis-ci.org/grantmcconnaughey/Lintly.svg?branch=master)](https://travis-ci.org/grantmcconnaughey/Lintly) [![codecov](https://codecov.io/gh/grantmcconnaughey/lintly/branch/master/graph/badge.svg)](https://codecov.io/gh/grantmcconnaughey/lintly)

Slurp up linter output and send it to a GitHub PR review. The CLI version of [lintly.com](https://lintly.com).

## Usage

First, `pip` install lintly:

    $ pip install lintly

Next, set the `LINTLY_API_KEY` environment variable to your GitHub API Key:

    $ export LINTLY_API_KEY="12345"

Finally, pipe the output of your linter to `lintly`:

    $ flake8 | lintly

Now you will see linting errors in your Pull Requests! Nifty!

![Lintly used on a pull request](./example.png)

## Support Git Services

- GitHub

> Support for GitLab and Bitbucket is planned.

## Supported Linters

- [flake8](http://flake8.pycqa.org/en/latest/)
    ```
    $ flake8 | lintly
    ```
- [eslint](https://eslint.org/)
    ```
    $ eslint --format=unix | lintly --format=eslint-unix
    ```

Additional linters can be added by modifying the `lintly/parsers.py` module.

## Configuration

At the minimum, Lintly needs to know the following information to determine how to post the correct GitHub PR Review:

- GitHub API key
    - Generate your own [API Key here](https://github.com/settings/tokens/new). Your API key will need the following GitHub scopes:
        - `repo:status` so that Lintly can post commit statuses on PRs.
        - `public_repo` so that Lintly can create pull request reviews on public repos.
        - `repo` so that Lintly can create pull request reviews on private repos.
- GitHub repository
    > Note: Some Continuous Integration tools will provide this value automatically.
- Pull Request number
    > Note: Some Continuous Integration tools will provide this value automatically.

These configuration values can be provided to Lintly via environment variables or by being passed in as arguments to the Lintly CLI.

## Using Lintly with Continuous Integration platforms

Lintly works out of the box with the following Continuous Integration platforms:

- [Travis CI](#travis-ci)
- Circle CI
- AppVeyor
- Shippable
- Semaphore
- CodeBuild

When using these Continuous Integration platforms the repository, pull request number, and commit SHA will be provided automatically.

### Travis CI

To use with Lintly with Travis CI, add the following to your `.travis.yml` config file:

```yml
language: python

jobs:
  include:
    - stage: lint
      install: pip install lintly
      script: flake8 | lintly

stages:
  - lint
```

## To-Do

- Support for [stylelint](https://stylelint.io/)
- Configuration to post either a PR comment or PR review
- Link to Build URL from commit status
- Support for config file
- Documentation

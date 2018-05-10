# Lintly

[![Build Status](https://travis-ci.org/grantmcconnaughey/Lintly.svg?branch=master)](https://travis-ci.org/grantmcconnaughey/Lintly)

Slurp up linter output and send it to a GitHub PR review.

# Installation

Simply run:

    $ pip install -e .

# Usage

First, `pip` install lintly:

    $ pip install lintly

Next, simply pipe the output of your linter to Lintly:

    $ flake8 | lintly

# Supported Linters

- flake8
- eslint
- stylelint

# Configuration

At the minimum, Lintly needs to know the following information to determine how to post the correct GitHub PR Review:

- GitHub API key
- GitHub repository
    > Note: Some Continuous Integration tools will provide this value automatically.
- Pull Request number
    > Note: Some Continuous Integration tools will provide this value automatically.

These configuration values can be provided to Lintly via environment variables or by being passed in as arguments to the Lintly CLI.

# Using Lintly with Continuous Integration Tools

Lintly works out of the box with Travis and Circle CI. When using these Continuous Integration services the repository, pull request number, and commit SHA will be provided automatically.

# To-Do

- Use Jinja for comment templating
- Support for eslint
- Support for stylelint

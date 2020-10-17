# Lintly Changelog

## 0.6.0 (October 27, 2020)

* Add support for Python 3.9
* Upgrade `click` version requirements
* Fixed an issue preventing Lintly from submitting a review when there are 51+ review comments

## 0.5.0 (May 5, 2020)

* **Backward Incompatible**: Change the default format from "unix" to "flake8."
  This has no functional difference, as they're the same format. However, it
  will result in a different GitHub commit status context, which could prevent
  you from merging PRs if the unix commit status is required by repo settings.
* Add support for GitHub Checks when called from GitHub Actions with the `--use-checks` flag.
* Add support for posting PR reviews that approve or request changes with the `--request-changes` flag.
* Update PR review comments to link to Lintly repo.
* Update license year.

## 0.4.2 (March 12, 2020)

* Fix issue parsing Pylint output when there are no violations.

## 0.4.1 (January 12, 2020)

* Add support for Python 3.7 and 3.8
* Add support for [cfn-nag](https://github.com/stelligent/cfn_nag)
* Now using [ci.py](https://github.com/grantmcconnaughey/ci.py) for CI service detection

## 0.4.0 (December 31, 2019)

* Add support for GitHub Actions
* Add support for Drone CI
* Add support for Azure DevOps
* Add Windows compatibility

## 0.3.0 (March 2, 2019)

* Support for [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint)
* Support for overriding the default PR status context using `--context`
* Change: Default PR status contexts have changed from "Lintly" to "Lintly/{format}"

## 0.2.0 (November 21, 2018)

* Support for [Black](https://black.readthedocs.io/en/stable/)

## 0.1.2 (June 10, 2018)

* Initial release
* Support for Python 2.7 and 3.4+
* Support for GitHub repos
* Support for Flake8, Pylint, ESLint, and Stylelint
* Support for Travis CI, Circle CI, AppVeyor, Shippable, Semaphore, and CodeBuild

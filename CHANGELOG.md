# Lintly Changelog

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

import abc
import os
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from lintly.parsers import PARSERS


class ParserTestCaseMixin(object):
    """Mixin for testing parsers.

    Attributes
    ----------
    linter_output : str
        A linter output to test against.
    """
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def parser(self):
        """lintly.parsers.BaseLintParser: a parser to test."""
        pass

    @property
    @abc.abstractmethod
    def linter_output_file_name(self):
        """str: linter output file name (relative to the `linters_output` directory)."""
        pass

    @property
    @abc.abstractmethod
    def expected_violations(self):
        """dict: a mapping between files and expected violations' attributes.

        Examples
        --------
        {
            'path/to/file': [{
                'line': 42,
                'column': 42,
                'code': 'the-answer',
                'message': 'don\'t panic & bring your towel'
            }]
        }
        """
        pass

    @staticmethod
    def load_linter_output(file_name):
        path = os.path.join(os.path.dirname(__file__), 'linters_output', file_name)
        with open(path, 'r') as linter_output:
            return linter_output.read()

    def setUp(self):
        self.linter_output = self.load_linter_output(self.linter_output_file_name)

    def test_parse_violations(self):
        violations = self.parser.parse_violations(self.linter_output)
        # Checking files.
        self.assertEqual(set(violations.keys()), set(self.expected_violations.keys()))
        # Checking violations.
        for file_path, violations in violations.items():
            expected_violations = self.expected_violations[file_path]
            # Checking violations count.
            self.assertEqual(len(violations), len(expected_violations))
            # Checking violations' attributes.
            for violation_index, violation in enumerate(violations):
                self.check_object_attrs(violation, expected_violations[violation_index])

    def check_object_attrs(self, _object, expected_attrs):
        for expected_attr, expected_value in expected_attrs.items():
            self.assertTrue(hasattr(_object, expected_attr))
            self.assertEqual(getattr(_object, expected_attr), expected_value)


class Flake8ParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['flake8']
    linter_output_file_name = 'flake8.txt'
    expected_violations = {
        'lintly/parsers.py': [
            {'line': 80, 'column': 5, 'code': 'E303', 'message': 'too many blank lines (3)'},
            {'line': 216, 'column': 1, 'code': 'W391', 'message': 'blank line at end of file'}
        ],
        'lintly/violations.py': [
            {'line': 1, 'column': 1, 'code': 'F401', 'message': '\'itertools\' imported but unused'},
            {'line': 20, 'column': 5, 'code': 'C901', 'message': '\'Violation.complex_method\' is too complex (11)'}
        ]
    }


class BanditJSONParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['bandit-json']
    linter_output_file_name = 'bandit-json.txt'
    expected_violations = {
        'build/lib/lintly/formatters.py': [
            {'line': 14, 'column': 0, 'code': 'B701 (jinja2_autoescape_false)',
             'message': ('Using jinja2 templates with autoescape=False is dangerous and can lead to XSS. '
                         'Use autoescape=True or use the select_autoescape function to mitigate XSS vulnerabilities.')}
        ],
        'lintly/formatters.py': [
            {'line': 14, 'column': 0, 'code': 'B701 (jinja2_autoescape_false)',
             'message': ('Using jinja2 templates with autoescape=False is dangerous and can lead to XSS. '
                         'Use autoescape=True or use the select_autoescape function to mitigate XSS vulnerabilities.')}
        ],
        'tests/test_builds.py': [
            {'line': 48, 'column': 0, 'code': 'B101 (assert_used)',
             'message': ('Use of assert detected. '
                         'The enclosed code will be removed when compiling to optimised byte code.')}
        ],
        'tests/test_cli.py': [
            {'line': 13, 'column': 0, 'code': 'B101 (assert_used)',
             'message': ('Use of assert detected. '
                         'The enclosed code will be removed when compiling to optimised byte code.')},
            {'line': 14, 'column': 0, 'code': 'B101 (assert_used)',
             'message': ('Use of assert detected. '
                         'The enclosed code will be removed when compiling to optimised byte code.')},
            {'line': 15, 'column': 0, 'code': 'B101 (assert_used)',
             'message': ('Use of assert detected. '
                         'The enclosed code will be removed when compiling to optimised byte code.')}
        ]
    }


class GitleaksParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['gitleaks']
    linter_output_file_name = 'gitleaks.json'
    expected_violations = {
        'relative/path/to/output': [
            {'line': 5, 'column': 0, 'code': 'AKIAIO5FODNN7EXAMPLE',
             'message': 'AWS Access Key'}
        ],
        'relative/path/to/output2': [
            {'line': 2, 'column': 0, 'code': '-----BEGIN PRIVATE KEY-----',
             'message': 'Asymmetric Private Key'}
        ]
    }


class HadolintParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['hadolint']
    linter_output_file_name = 'hadolint.json'
    expected_violations = {
        'relative/path/to/file1': [
            {'line': 12, 'column': 1, 'code': 'DL3015',
             'message': 'Avoid additional packages by specifying `--no-install-recommends`'}
        ],
        'relative/path/to/file2': [
            {'line': 19, 'column': 1, 'code': 'DL3020',
             'message': 'Use COPY instead of ADD for files and folders'}
        ]
    }


class TerrascanParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['terrascan']
    linter_output_file_name = 'terrascan.json'
    expected_violations = {
        'main.tf': [
            {'line': 6, 'column': 0, 'code': 'AWS LambdaFunction (lambdaNotEncryptedWithKms)',
             'message': 'Lambda does not use KMS CMK key to protect environment variables.'}
        ],
        'api_gateway_config.tf': [
            {'line': 15, 'column': 0, 'code': 'AWS.API Gateway.Logging.Medium.0567 (apiGatewayName)',
             'message': 'Enable AWS CloudWatch Logs for APIs'}
        ]
    }


class PylintJSONParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['pylint-json']
    linter_output_file_name = 'pylint-json.txt'
    expected_violations = {
        'lintly/patch.py': [
            {'line': 22, 'column': 0, 'code': 'W0511 (fixme)', 'message': 'TODO: Cache this'},
            {'line': 1, 'column': 0, 'code': 'C0111 (missing-docstring)', 'message': 'Missing module docstring'}
        ],
        'lintly/config.py': [
            {'line': 6, 'column': 0, 'code': 'C0301 (line-too-long)', 'message': 'Line too long (112/100)'},
            {'line': 1, 'column': 0, 'code': 'C0111 (missing-docstring)', 'message': 'Missing module docstring'},
            {
                'line': 10, 'column': 8, 'code': 'C0103 (invalid-name)',
                'message': 'Attribute name "ci" doesn\'t conform to snake_case naming style'
            }
        ]
    }

    def test_pylint_no_errors(self):
        violations = self.parser.parse_violations('')
        self.assertEqual(violations, dict())

        violations = self.parser.parse_violations('No config file found, using default configuration\n')
        self.assertEqual(violations, dict())


class ESLintParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['eslint']
    linter_output_file_name = 'eslint.txt'
    expected_violations = {
        'static/file1.js': [
            {'line': 1, 'column': 1, 'code': 'no-undef', 'message': '\'$\' is not defined'},
            {
                'line': 1, 'column': 11, 'code': 'space-before-function-paren',
                'message': 'Missing space before function parentheses'
            },
            {'line': 2, 'column': 1, 'code': 'indent', 'message': 'Expected indentation of 2 spaces but found 4'}
        ],
        'static/file2.js': [
            {'line': 3, 'column': 1, 'code': 'indent', 'message': 'Expected indentation of 4 spaces but found 8'},
            {'line': 4, 'column': 68, 'code': 'semi', 'message': 'Extra semicolon'}
        ]
    }

    @patch('lintly.parsers.ESLintParser._get_working_dir', return_value='/Users/grant/project')
    def test_parse_violations(self, _get_working_dir_mock):
        super(ESLintParserTestCase, self).test_parse_violations()


class StylelintParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['stylelint']
    linter_output_file_name = 'stylelint.txt'
    expected_violations = {
        'lintly/static/sass/file1.scss': [
            {'line': 13, 'column': 1, 'code': 'max-empty-lines', 'message': 'Expected no more than 1 empty line'}
        ],
        'lintly/static/sass/file2.scss': [
            {
                'line': 11, 'column': 1, 'code': 'at-rule-empty-line-before',
                'message': 'Expected empty line before at-rule'
            },
            {'line': 27, 'column': 1, 'code': 'max-empty-lines', 'message': 'Expected no more than 1 empty line'},
            {'line': 31, 'column': 22, 'code': 'number-leading-zero', 'message': 'Expected a leading zero'}
        ]
    }


class BlackParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['black']
    linter_output_file_name = 'black.txt'
    expected_violations = {
        file_path: [{'line': 1, 'column': 1, 'code': '`black`', 'message': 'this file needs to be formatted'}]
        for file_path in ['lintly/violations.py', 'lintly/parsers.py']
    }

    @patch('lintly.parsers.BlackParser._get_working_dir', return_value='/Users/jouyuy/Dev/workspace/Lintly')
    def test_parse_violations(self, _get_working_dir_mock):
        super(BlackParserTestCase, self).test_parse_violations()


class CfnLintParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['cfn-lint']
    linter_output_file_name = 'cfn-lint.txt'

    expected_violations = {
        "templates/template.yaml": [
            {'line': 2, 'column': 9, 'code': 'W2001', 'message': 'Parameter UnusedParameter not used.'},
            {'line': 5, 'column': 9, 'code': 'W2001', 'message': 'Parameter AnotherOne not used.'}
        ],
        "templates/template2.yaml": [
            {'line': 7, 'column': 9, 'code': 'E1012',
             'message': 'Ref PrincipalOrgID not found as a resource or parameter'},
        ]
    }


class CfnNagParserTestCase(ParserTestCaseMixin, unittest.TestCase):
    parser = PARSERS['cfn-nag']
    linter_output_file_name = 'cfn-nag.json'

    expected_violations = {
        "cloudformation/perfect-stack.yaml": [],
        "cloudformation/problem-stack.yaml": [
            {'line': 24, 'column': 0, 'code': 'F3',
             'message': 'IAM role should not allow * action on its permissions policy'},
            {'line': 150, 'column': 0, 'code': 'F3', 'message':
             'IAM role should not allow * action on its permissions policy'},
            {'line': 50, 'column': 0, 'code': 'W35',
             'message': 'S3 Bucket should have access logging configured'}
        ],
        "cloudformation/warning-stack.yaml": [
            {'line': 320, 'column': 0, 'code': 'W42',
             'message': 'Security Groups ingress with an ipProtocol of -1 found '},
        ]
    }

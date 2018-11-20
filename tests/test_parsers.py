import abc
import os
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from lintly.parsers import PARSERS


class ParserTestCase(unittest.TestCase):
    """Base class for testing parsers.

    Attributes
    ----------
    linter_output : str
        A linter output to test against.
    """

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

    @staticmethod
    def load_linter_output(file_name):
        path = os.path.join(os.path.dirname(__file__), 'linters_output', file_name)
        with open(path, 'r') as linter_output:
            return linter_output.read()

    def setUp(self):
        self.linter_output = self.load_linter_output(self.linter_output_file_name)


class PylintJSONParserTestCase(ParserTestCase):
    parser = PARSERS['pylint-json']
    linter_output_file_name = 'pylint-json.txt'

    def test_parse(self):
        violations = self.parser.parse_violations(self.linter_output)

        self.assertEqual(len(violations), 2)

        assert 'lintly/patch.py' in violations
        assert len(violations['lintly/patch.py']) == 2

        assert 'lintly/config.py' in violations
        assert len(violations['lintly/config.py']) == 3


class ESLintParserTestCase(ParserTestCase):
    parser = PARSERS['eslint']
    linter_output_file_name = 'eslint.txt'

    @patch('lintly.parsers.ESLintParser._get_working_dir', return_value='/Users/grant/project')
    def test_parse(self, _get_working_dir_mock):
        violations = self.parser.parse_violations(self.linter_output)

        self.assertEqual(len(violations), 2)

        assert 'static/file1.js' in violations
        assert len(violations['static/file1.js']) == 3

        assert 'static/file2.js' in violations
        assert len(violations['static/file2.js']) == 2


class StylelintParserTestCase(ParserTestCase):
    parser = PARSERS['stylelint']
    linter_output_file_name = 'stylelint.txt'

    def test_parse(self):
        violations = self.parser.parse_violations(self.linter_output)

        self.assertEqual(len(violations), 2)

        assert 'lintly/static/sass/file1.scss' in violations
        assert len(violations['lintly/static/sass/file1.scss']) == 1

        assert 'lintly/static/sass/file2.scss' in violations
        assert len(violations['lintly/static/sass/file2.scss']) == 3

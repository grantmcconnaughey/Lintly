import os
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from lintly.parsers import PARSERS


def load_output(file_name):
    path = os.path.join(os.path.dirname(__file__), 'linter_output', file_name)
    with open(path) as f:
        return f.read()


class PylintJSONParser(unittest.TestCase):

    def setUp(self):
        self.parser = PARSERS['pylint-json']

    def test_parse(self):
        output = load_output('pylint-json.txt')

        violations = self.parser.parse_violations(output)

        self.assertEqual(len(violations), 2)

        assert 'lintly/patch.py' in violations
        assert len(violations['lintly/patch.py']) == 2

        assert 'lintly/config.py' in violations
        assert len(violations['lintly/config.py']) == 3


class ESLintParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = PARSERS['eslint']

    @patch('lintly.parsers.ESLintParser._get_working_dir', return_value='/Users/grant/project')
    def test_parse(self, get_working_dir_mock):
        output = load_output('eslint.txt')

        violations = self.parser.parse_violations(output)

        self.assertEqual(len(violations), 2)

        assert 'static/file1.js' in violations
        assert len(violations['static/file1.js']) == 3

        assert 'static/file2.js' in violations
        assert len(violations['static/file2.js']) == 2


class StylelintParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = PARSERS['stylelint']

    def test_parse(self):
        output = load_output('stylelint.txt')

        violations = self.parser.parse_violations(output)

        self.assertEqual(len(violations), 2)

        assert 'lintly/static/sass/file1.scss' in violations
        assert len(violations['lintly/static/sass/file1.scss']) == 1

        assert 'lintly/static/sass/file2.scss' in violations
        assert len(violations['lintly/static/sass/file2.scss']) == 3

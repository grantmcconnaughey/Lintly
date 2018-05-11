"""
Parsers accept linter output and return file paths and all of the violations in that file.
"""
import collections
import os
import re

from .violations import Violation


class BaseLintParser(object):

    def parse_violations(self, output):
        raise NotImplementedError


class LineRegexParser(BaseLintParser):
    """
    A parser that runs a regular expression on each line of the output to return violations. The regex should match the following capture groups:

        - path
        - line
        - column
        - code
        - message
    """

    def __init__(self, regex):
        self.regex = regex

    def parse_violations(self, output):
        violations = collections.defaultdict(list)

        line_regex = re.compile(self.regex)

        # Collect all the issues into a dict where the keys are the file paths and the values are a
        # list of the issues in that file.
        for line in output.strip().splitlines():
            clean_line = line.strip()

            match = line_regex.match(clean_line)

            if not match:
                continue

            path = os.path.normpath(match.group('path'))

            violation = Violation(
                line=int(match.group('line')),
                column=int(match.group('column')),
                code=match.group('code'),
                message=match.group('message')
            )

            violations[path].append(violation)

        return violations


# TODO: Switch this to more of a registry pattern
PARSERS = {
    # Default flake8 format
    # docs/conf.py:230:1: E265 block comment should start with '# '
    # path:line:column: CODE message
    'unix': LineRegexParser(r'^(?P<path>.*):(?P<line>\d+):(?P<column>\d+): (?P<code>\w\d+) (?P<message>.*)$'),

    # ESLint's unix formatter
    # lintly/static/js/scripts.js:69:1: 'lintly' is not defined. [Error/no-undef]
    # path:line:column: message [CODE]
    'eslint-unix': LineRegexParser(r'^(?P<path>.*):(?P<line>\d+):(?P<column>\d+): '
                                   r'(?P<message>.+) \[(Warning|Error)/(?P<code>.+)\]$'),

}

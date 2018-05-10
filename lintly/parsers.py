import collections
import re

from .violations import Violation

# Parsers are named regexes that accept a line of linting output and return the following groups:
# - path
# - line
# - column
# - code
# - message
PARSER_FORMATS = {
    'unix': r'^(?P<path>.*):(?P<line>\d+):(?P<column>\d+): (?P<code>\w\d+) (?P<message>.*)$',
}


def parse_violations(output, regex):
    """
    Parses the output string and returns the violations dict.
    :param output: The output from running the linter command.
    :return: The violations dict.
    """
    # results = output.replace(self.path, '')
    violations = collections.defaultdict(list)

    line_regex = re.compile(regex)

    # Collect all the issues into a dict where the keys are the file paths and the values are a
    # list of the issues in that file.
    for line in output.strip().splitlines():
        clean_line = line.strip()

        match = line_regex.match(clean_line)

        if not match:
            continue

        path = match.group('path')

        violation = Violation(
            line=int(match.group('line')),
            column=int(match.group('column')),
            code=match.group('code'),
            message=match.group('message')
        )

        violations[path].append(violation)

    return violations

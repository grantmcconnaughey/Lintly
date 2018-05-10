"""
Formats text that will be posted to Pull Requests.
"""


def build_pr_comment(config, violations):
    """
    Creates a Markdown representation of the comment to be posted to a pull request.
    :return: The comment
    """

    comment_lines = ['### Lintly',
                     'The following code quality issues were introduced:']

    for file_path in sorted(violations):
        file_violations = violations[file_path]
        comment_lines.append('\n#### `{}`'.format(file_path))
        for violation in file_violations:
            comment_lines.append('* **{}**: {} (line {}, column {})'.format(
                violation.code,
                violation.message,
                violation.line,
                violation.column,
            ))

    comment = '\n'.join(comment_lines)
    return comment

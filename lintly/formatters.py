"""
Formats text that will be posted to Pull Requests.
"""
import os

from jinja2 import Environment, FileSystemLoader


TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')


env = Environment(
    loader=FileSystemLoader(TEMPLATES_PATH),
    autoescape=False
)


def build_pr_comment(config, violations):
    """
    Creates a Markdown representation of the comment to be posted to a pull request.
    :return: The comment
    """
    template = env.get_template('pr_comment.txt')
    return template.render(violations=violations)

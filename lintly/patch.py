import logging
import re

from cached_property import cached_property


FILE_NAME_LINE = re.compile(r'^\+\+\+ b/(?P<file_name>.+)')
RANGE_INFORMATION_LINE = re.compile(r'^@@ .+\+(?P<line_number>\d+),')
MODIFIED_LINE = re.compile(r'^\+(?!\+|\+)')
NOT_REMOVED_OR_NEWLINE_WARNING = re.compile(r'^[^-\\]')


logger = logging.getLogger(__name__)


class Patch(object):
    """
    Parses the body of a diff and returns the lines that changed as well as their "position",
    as outlined by GitHub here: https://developer.github.com/v3/pulls/comments/#create-a-comment
    """

    def __init__(self, body=''):
        self.body = body

    @cached_property
    def changed_lines(self):
        """
        A list of dicts in the format:
            {
                'file_name': str,
                'content': str,
                'line_number': int,
                'position': int
            }
        """
        lines = []
        file_name = ''
        line_number = 0
        patch_position = -1
        found_first_information_line = False

        for i, content in enumerate(self.body.splitlines()):
            range_information_match = RANGE_INFORMATION_LINE.search(content)
            file_name_line_match = FILE_NAME_LINE.search(content)

            if file_name_line_match:
                file_name = file_name_line_match.group('file_name')
                found_first_information_line = False
            elif range_information_match:
                line_number = int(range_information_match.group('line_number'))
                if not found_first_information_line:
                    # This is the first information line. Set patch position to 1 and start counting
                    patch_position = 0
                    found_first_information_line = True
            elif MODIFIED_LINE.search(content):
                line = {
                    'file_name': file_name,
                    'content': content,
                    'line_number': line_number,
                    'position': patch_position
                }

                lines.append(line)
                line_number += 1
            elif NOT_REMOVED_OR_NEWLINE_WARNING.search(content) or content == '':
                line_number += 1

            patch_position += 1

        return lines

    def get_patch_position(self, file_name, line_number):
        matching_lines = [line for line in self.changed_lines
                          if line['file_name'] == file_name and line['line_number'] == line_number]

        if len(matching_lines) == 0:
            return None
        elif len(matching_lines) == 1:
            return matching_lines[0]['position']
        else:
            logger.warning('Invalid patch or build.')
            logger.warning('Multiple matching lines found for {file_name} on line '
                           '{line_number}'.format(file_name=file_name, line_number=line_number))

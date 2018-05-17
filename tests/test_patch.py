import os
import unittest

from lintly.patch import Patch


def load_diff(file_name):
    path = os.path.join(os.path.dirname(__file__), 'diffs', file_name)
    with open(path) as f:
        return f.read()


class PatchTests(unittest.TestCase):

    def test_patch_with_added_lines_only(self):
        diff = load_diff('no_newline_at_eof.diff')
        patch = Patch(diff)

        changed_lines = patch.changed_lines

        self.assertEqual(len(changed_lines), 3)

        expected_first_line = {
            'content': "+        print 'Less than 9'",
            'file_name': 'mccabe.py',
            'line_number': 61,
            'position': 6
        }
        self.assertEqual(changed_lines[0], expected_first_line)

        expected_first_line = {
            'content': "+    elif c < 10:",
            'file_name': 'mccabe.py',
            'line_number': 62,
            'position': 7
        }
        self.assertEqual(changed_lines[1], expected_first_line)

        expected_first_line = {
            'content': "+        print 'Less than 10'",
            'file_name': 'mccabe.py',
            'line_number': 63,
            'position': 8
        }
        self.assertEqual(changed_lines[2], expected_first_line)

    def test_patch_with_added_and_removed_lines(self):
        diff = load_diff('single_file.diff')
        patch = Patch(diff)

        changed_lines = patch.changed_lines

        self.assertEqual(len(changed_lines), 2)

        expected_first_line = {
            'content': '+                        self.is_auth = True',
            'file_name': 'dir1/dir2/britecore.py',
            'line_number': 270,
            'position': 7
        }
        self.assertEqual(changed_lines[0], expected_first_line)

        expected_second_line = {
            'content': "+        raise web.seeother(render_this + '?' + urlencode(web.input()))",
            'file_name': 'dir1/dir2/britecore.py',
            'line_number': 779,
            'position': 16
        }
        self.assertEqual(changed_lines[1], expected_second_line)

    def test_patch_with_multiple_files(self):
        diff = load_diff('multiple_files.diff')
        patch = Patch(diff)

        changed_lines = patch.changed_lines

        self.assertEqual(len(changed_lines), 9)

        expected = (['my_file_name.py'] * 6) + (['test_different_commits.py'] * 3)
        actual_changed_file_names = [x['file_name'] for x in changed_lines]
        self.assertEqual(expected, actual_changed_file_names)

        expected_line_numbers = [1, 2, 3, 5, 6, 7, 11, 12, 13]
        actual_line_numbers = [x['line_number'] for x in changed_lines]
        self.assertEqual(expected_line_numbers, actual_line_numbers)

        expected_positions = [1, 2, 3, 6, 7, 8, 4, 5, 6]
        actual_positions = [x['position'] for x in changed_lines]
        self.assertEqual(expected_positions, actual_positions)

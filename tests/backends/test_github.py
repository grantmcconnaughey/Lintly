import unittest

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from lintly.backends.github import GitHubBackend
from lintly.constants import LINTLY_IDENTIFIER


class GitHubBackendTest(unittest.TestCase):
    def setUp(self):
        # Set up patched PyGithub client.
        patcher = patch("lintly.backends.github.Github")
        self.addCleanup(patcher.stop)
        patcher.start()
        # Define the GitHubBackend under test.
        fake_project = Mock()
        fake_project.full_name = "dummy_org/dummy_repo"
        self.backend = GitHubBackend(
            "super_secret_token", fake_project, "Lintly/flake8"
        )

    def test_delete_pull_request_review_comments(self):
        # Set up comment object mocks.
        comments_data = (
            # Commit where comment first appeared, comment body, whether comment should be deleted.
            ("000000", LINTLY_IDENTIFIER + " an old Lintly comment", True),
            ("abc123", LINTLY_IDENTIFIER + " a current Lintly comment", False),
            ("000000", "an old non-Lintly comment", False),
            ("abc123", "a current non-Lintly comment", False),
        )
        mock_review_comments = [
            Mock(original_commit_id=commit_id, body=body)
            for commit_id, body, _ in comments_data
        ]
        # Set up rest of mocks for the PyGithub client.
        fake_pr = Mock()
        fake_pr.head.sha = "abc123"
        fake_pr.get_review_comments.return_value = mock_review_comments
        self.backend.client.get_repo.return_value.get_pull.return_value = fake_pr
        # Call.
        self.backend.delete_pull_request_review_comments("123")
        # Assert delete() was only called on the comments where we expect them to be called.
        for mock_comment, comment_data in zip(mock_review_comments, comments_data):
            _, _, should_call = comment_data
            self.assertEqual(mock_comment.delete.called, should_call)

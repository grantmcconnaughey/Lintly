from .base import BaseGitBackend


class DummyGitBackend(BaseGitBackend):
    """
    A Git backend class that returns dummy data for all of the abstract methods.
    """

    supports_pr_reviews = False

    def get_pull_request(self, pr):
        pass

    def create_pull_request_comment(self, pr, comment):
        pass

    def delete_pull_request_comments(self, pr, bot):
        pass

    def create_pull_request_review(self, build):
        pass

    def delete_pull_request_review_comments(self, pr, bot):
        pass

    def post_status(self, state, description, sha, target_url):
        pass

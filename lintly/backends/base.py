
class BaseGitBackend(object):
    """
    A base class for making calls to external Git APIs.
    """

    supports_pr_reviews = False

    def __init__(self, token, project):
        self.token = token
        self.project = project

    def __repr__(self):
        token = '********' if self.token else 'None'
        return '{}(token={}, project={})'.format(
            self.__class__.__name__, token, self.project)

    def get_pull_request(self, pr):
        """
        Returns a pull request for a given PR number.
        """
        raise NotImplementedError

    def create_pull_request_comment(self, pr, comment):
        """
        Creates a comment on a pull request.
        """
        raise NotImplementedError

    def delete_pull_request_comments(self, pr):
        """
        Deletes all pull request comments for the bot account.
        """
        raise NotImplementedError

    def get_pr_diff(self, pr):
        """
        Returns a diff for a pull request.
        """
        raise NotImplementedError

    def create_pull_request_review(self, pr, patch, all_violations, pr_review_action):
        """
        Creates a pull request review for the given build.
        """
        raise NotImplementedError

    def delete_pull_request_review_comments(self, pr):
        """
        Deletes all pull request review comments for the bot account.
        """
        raise NotImplementedError

    def post_status(self, state, description, sha, target_url):
        raise NotImplementedError

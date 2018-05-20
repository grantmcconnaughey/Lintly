
class PullRequest(object):

    def __init__(self, number, url, head_ref, head_sha, base_ref, base_sha):
        self.number = number
        self.url = url
        self.head_ref = head_ref
        self.head_sha = head_sha
        self.base_ref = base_ref
        self.base_sha = base_sha


class Repository:

    def __init__(self, name, full_name, clone_url, default_branch, private, service='github', description='',
                 external_url='', homepage='', admin=False, owner=None):
        self.service = service
        self.name = name
        self.full_name = full_name
        self.clone_url = clone_url
        self.default_branch = default_branch
        self.private = private
        self.description = description
        self.external_url = external_url
        self.homepage = homepage
        self.owner = owner
        self.admin = admin


class Commit:

    def __init__(self, sha, message, external_url, author_name='', author_email='',
                 author_avatar_url='', committer_name='', committer_email='',
                 committer_avatar_url=''):
        self.sha = sha
        self.message = message
        self.external_url = external_url
        self.author_name = author_name
        self.author_email = author_email
        self.author_avatar_url = author_avatar_url
        self.committer_name = committer_name
        self.committer_email = committer_email
        self.committer_avatar_url = committer_avatar_url


class Owner:

    def __init__(self, login, name=None, email=None, type_='User'):
        self.login = login
        self.name = name
        self.email = email
        self.type = type_


class PullRequest:

    def __init__(self, number, url, head_ref, head_sha, base_ref, base_sha):
        self.number = number
        self.url = url
        self.head_ref = head_ref
        self.head_sha = head_sha
        self.base_ref = base_ref
        self.base_sha = base_sha

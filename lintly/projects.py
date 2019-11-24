class Project(object):

    def __init__(self, full_name):
        self.full_name = full_name

    def __str__(self):
        return self.full_name

    @property
    def owner_login(self):
        return self.full_name.split('/')[0]

    @property
    def name(self):
        return self.full_name.split('/')[1]

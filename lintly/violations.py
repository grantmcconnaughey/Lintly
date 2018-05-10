
class Violation(object):

    def __init__(self, line, column, code, message):
        self.line = line
        self.column = column
        self.code = code
        self.message = message

    def __str__(self):
        return self.message

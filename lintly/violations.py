class Violation(object):
    def __init__(self, line, column, code, message):
        self.line = line
        self.column = column
        self.code = code
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return 'Violation(line={}, column={}, code="{}", message="{}")'.format(
                        self.line, self.column, self.code, self.message)

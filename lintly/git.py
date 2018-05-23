import sh


def head():
    """Returns the head commit"""
    return sh.git('rev-parse', 'HEAD').stdout[:40]

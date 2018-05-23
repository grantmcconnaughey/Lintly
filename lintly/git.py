import sh


def head():
    """Returns the head commit"""
    sha = sh.git('rev-parse', 'HEAD').stdout[:40]
    return sha.decode('utf-8')

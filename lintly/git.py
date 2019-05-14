import subprocess


def head():
    """Returns the head commit"""
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:40]
    return sha.decode('utf-8')

import sh
import six


def head():
    """Returns the head commit"""
    return six.u(sh.git('rev-parse', 'HEAD').stdout)[:40]

"""
Slurp up linter output and send it to a GitHub PR review.
"""
import codecs
import os
from setuptools import find_packages, setup

dependencies = [
    'ci-py',
    'cached-property<2.0',
    'click<7.0',
    'jinja2<3.0',
    'PyGithub<2.0',
    'python-gitlab<2.0',
    'six',
]


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


setup(
    name='lintly',
    version='0.5.0',
    url='https://github.com/grantmcconnaughey/lintly',
    license='MIT',
    author='Grant McConnaughey',
    author_email='grantmcconnaughey@gmail.com',
    description='Automated GitHub PR code reviewer for Python, JavaScript, CSS, and more.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'lintly = lintly.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ]
)

"""
Slurp up linter output and send it to a GitHub PR review.
"""
from setuptools import find_packages, setup

dependencies = [
    'click<7.0',
    'jinja2<3.0',
    'PyGithub<2.0',
    'python-gitlab<2.0',
    'sh<1.13',
    'six',
]

setup(
    name='lintly',
    version='0.1.0',
    url='https://github.com/grantmcconnaughey/lintly',
    license='BSD',
    author='Grant McConnaughey',
    author_email='grantmcconnaughey@gmail.com',
    description='Slurp up linter output and send it to a GitHub PR review.',
    long_description=__doc__,
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
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

"""sfdclib package setup"""

from setuptools import setup
import textwrap
import sys

setup(
    name='sfdclib',
    version='0.1',
    author='Andrey Shevtsov',
    maintainer='Andrey Shevtsov',
    maintainer_email='ashevtsov@rbauction.com',
    packages=['sfdclib'],
    url='https://github.com/rbauction/sfdclib',
    license='MIT',
    description=("SFDClib is a Salesforce.com Metadata API and Tooling "
        "API client built for Python 3.3 and 3.4."),
    long_description=textwrap.dedent(open('README.rst', 'r').read()),
    install_requires=[
        'requests[security]'
    ],
    keywords = "python salesforce salesforce.com metadata tooling api",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
)

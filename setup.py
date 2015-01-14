import os
from n2cw import VERSION
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="n2cw",
    version=VERSION,
    author="Matthew Wedgwood",
    author_email="mwedgwood@gmail.com",
    description=("A wrapper for sending Nagios plugin output to CloudWatch"),
    license="MIT",
    keywords=["amazon", "aws", "cloudwatch", "nagios", "metrics", "monitoring"],
    url = "http://github.com/slank/n2cw",
    packages=['n2cw'],
    long_description=read('README.md'),
    install_requires=[
        'botocore>=0.80.0',
    ],
    entry_points={
        'console_scripts': [
            'n2cw=n2cw.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)

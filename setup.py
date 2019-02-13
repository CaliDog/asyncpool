from setuptools import setup
import sys

py_version = sys.version_info[:2]

if py_version < (3, 3):
    raise Exception("AsyncPool requires Python >= 3.3.")

long_description = """
AsyncPool is a asyncio-based coroutine worker pool, intended to process through large amounts of jobs
efficiently and with explicit timeouts.
"""


def my_test_suite():
    import asynctest
    test_loader = asynctest.TestLoader()
    test_suite = test_loader.discover('tests')
    return test_suite


setup(
    name='asyncpool',
    version='1.0',
    url='http://github.com/calidog/asyncpool/',
    author='Ryan Sears',
    author_email='ryan@calidog.io',
    description='Async coroutine worker pool',
    long_description=long_description,
    packages=['asyncpool'],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
        "Environment :: Console",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='setup.my_test_suite',
)

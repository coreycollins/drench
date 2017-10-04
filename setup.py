import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(name='statemachine',
      version='1.0',
      description='Generate state machines for AWS Step Fucntions',
      author='Corey Collins',
      author_email='ccollins@cmsdm.com',
      packages=['statemachine','lambda'],
      package_data={'lambda': ['lambda/*.py']},
      include_package_data=True,
      tests_require=['pytest'],
      scripts=['scripts/statetest'],
      cmdclass={'test': PyTest},
      install_requires=[]
)

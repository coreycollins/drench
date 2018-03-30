from setuptools import setup, find_packages

setup(name='drench_sdk',
      version='1.0',
      description='Generate state machines for AWS Step Fucntions',
      author='Corey Collins',
      author_email='ccollins@cmsdm.com',
      packages=find_packages(),
      install_requires=[
          'boto3',
          'python-lambda-local',
          'jsonpath_ng',
          'requests'
          ]
)

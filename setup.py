from setuptools import setup, find_packages

setup(name='drench_sdk',
      version='1.0',
      description='Generate state machines for AWS Step Fucntions',
      author='Corey Collins',
      author_email='ccollins@cmsdm.com',
      packages=find_packages(),
      install_requires=[
          'click>=5.1',
          'jsonpath_ng',
          'requests',
          'boto3'
      ],
      entry_points={
          'console_scripts': [
              'drench_sdk = drench_sdk.cli:main',
          ],
      })

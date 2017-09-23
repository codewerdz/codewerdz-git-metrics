from codewerdz.git import __version__

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='codewerdz-git',
      packages=find_packages(exclude=["test*"]),
      version=__version__,
      description='A tool that analyses git to determine the ratio of code commits to doc commits.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='git documentation datascience analysis log',
      url='https://github.com/codewerdz/codewerdz-git',
      author='Troy Howard',
      author_email='thoward37@gmail.com',
      license='MIT',
      include_package_data=True,
      install_requires=[
        'whatthepatch==0.0.4',
        'click',
        'iso8601'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
        'console_scripts': ['codewerdz-git=codewerdz.git.cli:cli'],
      },
      zip_safe=False)

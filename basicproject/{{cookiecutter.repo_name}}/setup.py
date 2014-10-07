#!/usr/bin/env python

from setuptools import setup

setup(
    name='{{cookiecutter.repo_name}}',
    version='{{cookiecutter.version}}',
    description='{{cookiecutter.description}}',
    long_description='{{cookiecutter.description}}',
    author='{{cookiecutter.full_name}}',
    author_email='{{cookiecutter.email}}',
    url='https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.repo_name}}',
    packages=['{{cookiecutter.repo_name}}',],
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
)

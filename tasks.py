#!/usr/bin/env python
# coding=utf-8

import sys
from invoke import run, task
from invoke.util import log


@task
def test():
    run('py.test tests/ --pep8 --cov pyseries --cov-report term-missing')


@task
def clean():
    run('find . -name *.pyc -delete')
    run('find . -name *.pyo -delete')
    run('find . -name *~ -delete')
    run('find . -name __pycache__ -delete')
    run('find . -name .coverage -delete')
    run('rm -rf dist/')
    run('rm -rf .cache/')
    run('rm -rf pyseries.egg-info')
    run('rm -rf build/')
    log.info('cleaned up')


@task
def release(push_tags=False):
    # Are you sure to release?
    try:
        input("Is everything commited? Are you ready to release? "
              "Press any key to continue - abort with Ctrl+C")
    except KeyboardInterrupt as e:
        print("Release aborted...")
        exit()

    run('bumpversion --message "Release version {new_version}" release')
    run('python setup.py sdist bdist_wheel')
    run('bumpversion --message "Preparing next version {new_version}" '
        '--no-tag minor')

    # Push tags if enabled
    if push_tags:
        run('git push origin master --tags')
    else:
        print("Don't forget to push the tags (git push origin master --tags)!")

# Warn the user when not using virtualenv
if not hasattr(sys, 'real_prefix'):
    print('YOU ARE NOT RUNNING INSIDE A VIRTUAL ENV!')

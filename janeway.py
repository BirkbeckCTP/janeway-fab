import os

from fabric.api import task, prefix, env, cd, run, lcd, local, hide, sudo
from fabric.contrib import files
from functools import wraps, partial

import fab_settings


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@task
def directory():
    return fab_settings.BASE_DIR


def virtualenv(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        path =  "source {0}".format(fab_settings.VIRTUAL_ENV_PATH)
        with prefix(path): # might be able to replace this with 'workon prj'
            return func(*args, **kwargs)
    return _wrapper


@task
def git_pull():
    with env.cd(directory()):
        cmd = 'git pull'
        env.run(cmd)


@task
@virtualenv
def migrate():
    with env.cd(directory()):
        cmd = 'python3 manage.py migrate'
        env.run(cmd)


@task
@virtualenv
def install_requirements():
    with env.cd(directory()):
        cmd = 'pip3 install -r ../requirements.txt'
        env.run(cmd)


@task
@virtualenv
def build_assets():
    with env.cd(directory()):
        cmd = 'python3 manage.py build_assets'
        env.run(cmd)


@task
@virtualenv
def collect_static():
    with env.cd(directory()):
        cmd = 'python3 manage.py collectstatic --no-input'
        env.run(cmd)


@task
@virtualenv
def update_settings():
    with env.cd(directory()):
        cmd = 'python3 manage.py sync_settings_to_journals'
        env.run(cmd)


@task
@virtualenv
def merge_migrations():
    with env.cd(directory()):
        cmd = 'python3 manage.py makemigrations --merge'
        env.run(cmd)


@task
@virtualenv
def backup():
    with env.cd(directory()):
        cmd = 'python3 manage.py backup'
        env.run(cmd)


@task
def update_styling_overrides():
    dir = "{0}files/styling/".format(directory())

    with env.cd(dir):
        cmd = "git pull"
        env.run(cmd)


@task
def update_plugins():
    plugin_dir = "{0}plugins".format(directory())
    with env.cd(plugin_dir):
        cmd = 'ls -d */'
        dirs = env.run(cmd)

    for folder in dirs.split('  '):
        if folder not in ['__init__.py', '__pycache__/']:
            print(folder, "{0}/{1}".format(plugin_dir, folder))
            with env.cd("{0}/{1}".format(plugin_dir, folder)):
                cmd = 'git pull'
                env.run(cmd, warn_only=True)

    migrate()
    collect_static()



@task
def update():
    backup()
    git_pull()
    install_requirements()
    migrate()
    update_styling_overrides()
    build_assets()
    collect_static()
    update_settings()
import os, shutil, getpass, json

from fabric.api import task, prefix, env, cd, run, lcd, local, hide, sudo
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.operations import prompt, local as lrun
from fabric.contrib import files

import janeway
import fab_settings

DEV, TEST, SETUP, STAGING, LIVE = 'dev', 'test', 'setup', 'staging', 'live'

def setenv(obj):
    for key, val in obj.items():
        setattr(env, key, val)

env.hosts = []
env.run = run
env.cd = cd

def _local_machine(hosts, **kwargs):
    obj = {}
    obj['user'] = getpass.getuser()

    # custom
    def _runwrapper(*args, **kwargs):
        """when attempting to run a command as root on the dev machine, it runs the
        command as a sudo otherwise it will try to ssh in as the root user."""
        _sudo = lambda cmd, *args, **kwargs: lrun("sudo %s" % cmd, *args, **kwargs)
        if env.user == 'root': 
            cmd = args[0]
            return _sudo(cmd, *args[1:], **kwargs)
        elif kwargs.has_key('use_sudo') and kwargs['use_sudo'] == True:
            del kwargs['use_sudo']
            cmd = args[0]
            return _sudo(cmd, *args[1:], **kwargs)
        if kwargs.has_key('use_sudo'):
            del kwargs['use_sudo']
        return lrun(*args, **kwargs)
    obj['run'] = _runwrapper
    obj['cd'] = lcd
    obj['file_exists'] = os.path.exists
    obj['listdir'] = os.listdir

    obj['hosts'] = hosts
    obj['is_mac'] = os.path.exists('/usr/sbin/apachectl')
    obj.update(kwargs)

    if kwargs.has_key('simple') and kwargs['simple']:
        return obj

    setenv(obj)

def _remote_machine(hosts, **kwargs):
    "sets the environment to the remote test server and any Fabric commands to use their remote versions."
    obj = {}
    def _runwrapper(*args, **kwargs):
        func = run
        if kwargs.has_key('capture'):
            del kwargs['capture']
        if kwargs.has_key('use_sudo'):
            if kwargs['use_sudo'] == True:
                func = sudo
            del kwargs['use_sudo']
        return func(*args, **kwargs)
    obj['user'] = fab_settings.SERVER_USER
    obj['run'] = _runwrapper
    obj['cd'] = cd
    obj['file_exists'] = files.exists
    obj['listdir'] = remote_listdir

    obj['hosts'] = hosts
    obj['is_mac'] = False
    obj.update(kwargs)

    if kwargs.has_key('simple') and kwargs['simple']:
        return obj

    setenv(obj)


def remote_listdir(path):
    with hide('everything'):
        output = run('ls %s' % path)
        if not output.startswith('ls: cannot access'):
            return output.split()
        return []


@task
def server(ej_env=LIVE, simple=False):
    return _remote_machine([fab_settings.SERVER_IP], code=ej_env, db_server=('localhost', 3306), simple=simple)
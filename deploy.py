#!/usr/bin/python
import yaml
import os
import sys
from subprocess import Popen, PIPE


def hookprint(msg):
    msg = 'deploy: ' + msg
    print >> sys.stderr, msg


def command(cmd, inp=None, wd=None):
    child = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, cwd=wd)
    out, err = child.communicate(inp)
    return out, err, child.returncode


def last_deploy_tag_name(branch_name):
    return branch_name + '-last-deploy'


def get_changeset_from_log(log):
    log = log.partition('\n')[0]
    log = log[len('changeset:') :]
    log = log.strip()
    log = log.partition(':')
    return log[0]


def get_branch_change(branch_name):
    tag = last_deploy_tag_name(branch_name)
    #find revision for this tag
    tag_changeset_cmd = command('hg log -r "{0}"'.format(tag))
    if tag_changeset_cmd[2]:
        tag_changeset = False
    else:
        tag_changeset = get_changeset_from_log(tag_changeset_cmd[0])
    
    #find last revision for branch
    branch_changeset_cmd = command('hg log -b "{0}" -l 1'.format(branch_name))
    if branch_changeset_cmd[2]:
        branch_changeset = False
    else:
        branch_changeset = get_changeset_from_log(branch_changeset_cmd[0])
        
    return tag_changeset, branch_changeset


def do_sync(changeset_from, changeset_to, location_src, location_dst, need_delete):
    #TODO use the two changesets to determine files that need to be deleted on the remote host
    if need_delete:
        delete_arg = '--delete '
    else:
        delete_ard = ''

    rsync_command = 'rsync -az {0}--exclude=.hg {1}/ {2}'.format(location_src, location_dst)
    _, err, code = command(rsync_command)
    if code:
        hookprint('Failed to sync {0} and {1}'.format(location_src, location_dst))
        hookprint('STD ERR: {0}'.format(err))
        sys.exit(1)


def do_command(changeset_from, changeset_to, server, cmd, wd):
    hookprint('ACTION executing command {0} on {1}'.format(cmd, server))

    if server != '$local':
        #TODO properly escape a command
        cmd = 'ssh {0} "{1}"'.format(server, cmd)

    out, err, code = command(cmd, wd=wd)
    hookprint('exit code {0}'.format(code))
    if out:
        hookprint('STD OUT: {0}'.format(out))
    if err:
        hookprint('STD ERR: {0}'.format(err))


def do_actions(changeset_from, changeset_to, actions):
    for action in actions:
        if 'sync' in action:
            do_sync(changeset_from, changeset_to, action['source'], action['dest'], action.get('delete', False))
        elif 'command' in action:
            do_command(changeset_from, changeset_to, action.get('where', '$local'), action['command'], action.get('wd', False))
        else:
            hookprint('Unknown action "{0}"'.format(action))
            sys.exit(1)


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


def update_repo(changeset):
    _, _, code = command('hg update -r {0} --clean'.format(changeset))
    if code:
        hookprint('Failed to update repository to revision {0}'.format(changeset))
        sys.exit(1)


def do_deploy(repo_folder=False, repo_branch=False):
    #load config and search for actions
    if not repo_folder:
        repo_folder = os.getcwd()
    else:
        repo_folder = os.path.abspath(repo_folder)
        os.chdir(repo_folder)
    wd_split = os.path.split(repo_folder)
    repos_folder = wd_split[0]
    repo_id = wd_split[1]

    cfg = yaml.load(open(os.path.join(repos_folder, 'deploy.yml')))

    # get branches configuration for this repo
    if not repo_id in cfg:
        hookprint('The repository {0} is not configured for deploy'.format(repo_id))
        sys.exit(0)

    branches = cfg[repo_id]

    for branch_name, actions in branches.iteritems():
        changesets = get_branch_change(branch_name)
        branch_changed = changesets[0] != changesets[1]
        # if repo_branch is not set then redeploy only changed branches
        # else redeploy only repo_branch
        if branch_changed and not repo_branch or branch_name == repo_branch:
            hookprint('Branch {0} needs to be redeployed'.format(branch_name))
            update_repo(changesets[1])
            do_actions(changesets[0], changesets[1], actions)
            #update bookmark
            _, err, code = command('hg bookmark -fr {0} {1}'.format(changesets[1], last_deploy_tag_name(branch_name)))
        else:
            hookprint('Branch {0} does not need to be redeployed'.format(branch_name))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        do_deploy(sys.argv[1])
    elif len(sys.argv) == 3:
        do_deploy(sys.argv[1], sys.argv[2])
    else:
        do_deploy()

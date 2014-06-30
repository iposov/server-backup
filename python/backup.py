from subprocess import Popen
import yaml
import sys
import os
import socket
import tarfile
from datetime import datetime
import tempfile
import shutil
import pycurl
# TODO import and use argparse

CONFIG_FILE_NAME = "backup.yml"
WEBDAV_CREDENTIALS_FILE = "/etc/webdav-logins.yml"
NOW = datetime.now()
TEMP_DIR = None
HOST = socket.gethostname()


def upload_to_webdav(webdav_key):
    print "backup: Uploading started"
    #read credentials
    try:
        with open(WEBDAV_CREDENTIALS_FILE) as cfg_file:
            cfg = yaml.load(cfg_file)
            if webdav_key not in cfg:
                print >> sys.stderr, "Failed to find webdav credentials for key " + webdav_key
                sys.exit(4)
            cfg = cfg[webdav_key]
    except IOError:
        print >> sys.stderr, "Failed to read file with WebDAV credentials " + WEBDAV_CREDENTIALS_FILE
        sys.exit(5)

    #create url
    url = cfg['url']
    if 'subfolder' in cfg:
        sub = cfg['subfolder']
        if sub == '$host':
            sub = HOST
        url += '/' + sub

        # create subdirectory
        # http://api.yandex.ru/disk/doc/dg/reference/mkcol.xml
        curl = None
        try:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)

            curl.setopt(pycurl.USERNAME, cfg['login'])
            curl.setopt(pycurl.PASSWORD, cfg['password'])
            curl.setopt(pycurl.CUSTOMREQUEST, "MKCOL")

            curl.perform()

            #TODO test return code: 201 - ok, 405 - already exists (?) or some other problem
        except IOError as e:
            print >> sys.stderr, "Failed to create remote folder " + e.message
            sys.exit(6)
        finally:
            if curl is not None:
                curl.close()

    #list all files
    all_tar_files = [f for f in os.listdir(TEMP_DIR) if f.endswith(".tar.gz")]  # TODO change condition

    #upload each file separately
    for file_to_upload_name in all_tar_files:
        print "backup: Uploading file " + file_to_upload_name

        file_to_upload_path = TEMP_DIR + '/' + file_to_upload_name
        file_size = os.path.getsize(file_to_upload_path)
        curl = None
        try:
            curl = pycurl.Curl()
            with open(file_to_upload_path, 'rb') as file_object:
                curl.setopt(pycurl.URL, url + '/' + file_to_upload_name)

                curl.setopt(pycurl.USERNAME, cfg['login'])
                curl.setopt(pycurl.PASSWORD, cfg['password'])

                curl.setopt(pycurl.UPLOAD, 1)
                curl.setopt(pycurl.READFUNCTION, file_object.read)
                curl.setopt(pycurl.INFILESIZE, file_size)

                curl.perform()
        except IOError as e:
            print >> sys.stderr, "Failed to upload file " + file_to_upload_name + " error: " + e.message
        finally:
            if curl is not None:
                curl.close()


def create_file_name(target_name, postfix=None):
    time = NOW.strftime("%m-%d-%y--%H-%M-%S")
    if postfix is not None:
        target_name += '-' + postfix
    return target_name + '-' + HOST + '-' + time


def action_tar(target_name, folders_to_tar):
    print "backup:", "taring folders " + ", ".join(folders_to_tar)
    tar_file_name = create_file_name(target_name) + '.tar.gz'
    with tarfile.open(TEMP_DIR + '/' + tar_file_name, mode="w:gz") as tar_file:
        for folder in folders_to_tar:
            tar_file.add(folder)


def action_mongo(target_name, action):
    db_name = action['mongo']
    output_folder_name = TEMP_DIR + '/' + db_name + '-mongo-backup'

    mongo_command = ["mongodump", "--db", db_name, "-o", output_folder_name]

    host = action.get('host', '$local')

    print "backup: Starting mongo dump for db %s on host %s" % (db_name, host)

    if host != '$local':
        mongo_command += ["--host", host]

    dumper = Popen(" ".join(mongo_command), shell=True)
    dumper.communicate()

    print "backup: mongodump return code " + str(dumper.returncode)

    if dumper.returncode != 0:
        return

    #taring result
    print "backup: taring mongodump result"
    mongo_tar_file_name = create_file_name(target_name, 'mongodb-' + db_name) + '.tar.gz'
    with tarfile.open(TEMP_DIR + '/' + mongo_tar_file_name, mode="w:gz") as tar_file:
        tar_file.add(output_folder_name)


def do_target(target_name, target):
    print "backup: Backing up target " + target_name
    folders_to_tar = []

    for action in target:
        if 'folder' in action:
            folders_to_tar.append(action['folder'])
        elif 'mongo' in action:
            action_mongo(target_name, action)

    action_tar(target_name, folders_to_tar)


#returns config loaded from file_path or None if failed
def try_load_config(file_path):
    try:
        with open(file_path) as config_file:
            return yaml.load(config_file)
    except IOError:
        return None


#loads config from a file either in the working dir or in /etc
def load_config():
    cfg = try_load_config(CONFIG_FILE_NAME)
    if cfg is None:
        cfg = try_load_config('/etc/' + CONFIG_FILE_NAME)
    return cfg


def do_backup(target_name=None):
    cfg = load_config()
    if cfg is None:
        print >> sys.stderr, "Could not find config file"
        sys.exit(3)

    print "backup: Backup started"

    if target_name is None:
        print "backup: Backing up all targets"
        for target_name, target in cfg.iteritems():
            do_target(target_name, target)
    else:
        if target_name not in cfg:
            print >> sys.stderr, "Unknown target {0}".format(target_name)
            sys.exit(2)
        else:
            do_target(target_name, cfg[target_name])


if __name__ == '__main__':
    TEMP_DIR = tempfile.mkdtemp()

    try:
        if len(sys.argv) != 3:
            print >> sys.stderr, "Usage: backup.py webdav -a|--all|target-name"
            sys.exit(1)
        webdav = sys.argv[1]
        target_arg = sys.argv[2]
        if target_arg == '-a' or target_arg == '--all':
            do_backup()
        else:
            do_backup(target_arg)

        upload_to_webdav(webdav)

    finally:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        # pass
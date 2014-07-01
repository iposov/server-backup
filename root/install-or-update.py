#!/usr/bin/python
import os
import re
import sys
import shutil

# get script folder

file_path = sys.argv[0]
script_dir, _ = os.path.split(file_path)

# create /etc/der if it does not exist

if not os.path.isdir('/etc/der'):
    os.makedirs('/etc/der', mode=0755)

# copy contents of /etc/der removing .example if a file does not exist

etc_der_folder = script_dir + '/etc/der'
for config_file_example in os.listdir(etc_der_folder):
    match = re.match("^(.*)\.example(.*)$", config_file_example)
    if match is None:
        continue
    config_file_name = match.group(1) + match.group(2)

    destination_file = '/etc/der/' + config_file_name
    if not os.path.isfile(destination_file):
        shutil.copyfile(etc_der_folder + '/' + config_file_example, destination_file)

# remove /opt/der if it already exists, the copy new version

if os.path.isdir('/opt/der'):
    shutil.rmtree('/opt/der')

shutil.copytree(script_dir + '/opt/der', '/opt/der')
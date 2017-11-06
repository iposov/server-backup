import argparse
import shutil
import sys
import tempfile
from datetime import datetime
import yaml
import socket
import os

from destinations.Destination import Destination
from Target import Target


class BackupContext:

    def __init__(self, argparse_callback):
        def _load_yaml(filename, required=True):
            try:
                with open(filename) as config_file:
                    return yaml.load(config_file)
            except IOError:
                print >> sys.stderr, "Could not find file %s" % filename
                if required:
                    sys.exit(3)
                else:
                    return object()

        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--backups", required=False, default='/etc/der/backup.yml')
        parser.add_argument("-c", "--credentials", required=False, default='/etc/der/credentials.yml')
        parser.add_argument("-d", "--destinations", required=False, default='/etc/der/destinations.yml')

        argparse_callback(parser)

        self.args = parser.parse_args()

        self.config = _load_yaml(self.args.backups)
        self.credentials = _load_yaml(self.args.credentials, required=False)
        self.destinations = _load_yaml(self.args.destinations)

        self.now = datetime.now()
        self.host = socket.gethostname()

        self.temp_dir = None
        self.temp_dir_delete = False

        self.dry_run = False

    def get_parser_argument(self, arg, default=None):
        if default is None:
            return getattr(self.args, arg)
        else:
            return getattr(self.args, arg, default)

    def get_targets(self, specified_target_name):

        if specified_target_name == 'all':
            result = []
            for target_name, target in self.config.iteritems():
                result.append(Target(self, target_name, target))
            return result
        else:
            if specified_target_name not in self.config:
                return []
            else:
                return [Target(self, specified_target_name, self.config[specified_target_name])]

    def get_destinations(self, specified_destination_id):
        if specified_destination_id in self.destinations:
            return [Destination.create(self, specified_destination_id, self.destinations[specified_destination_id])]
        else:
            return []

    def set_temp_dir(self, temp_dir=None, delete=True):
        if temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()
        else:
            self.temp_dir = unicode(os.path.abspath(temp_dir), encoding='utf8')
        self.temp_dir_delete = delete
        self.log("using temporary dir {}; delete it: {}".format(self.temp_dir, self.temp_dir_delete))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.temp_dir_delete:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def log(self, message):  # TODO add prefix, datetime
        print message

    def log_error(self, message):  # TODO add prefix, datetime
        print >> sys.stderr, message

    def temp_path(self, local_path):
        return os.path.join(self.temp_dir, local_path)

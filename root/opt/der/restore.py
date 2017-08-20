#!/usr/bin/python
import sys
import os

from lib.backup.BackupContext import BackupContext
from lib.backup.TarArchive import TarArchive


if __name__ == '__main__':
    def argparse_callback(parser):
        parser.add_argument(
            "--put-back",
            help="overwrite the location where the backup was taken from",
            action="store_true"
        )

        parser.add_argument("target", help="target id")
        parser.add_argument("destination", help="id of a destination to store backup")
        parser.add_argument("filename", help="filename to restore")  # TODO make it possible to list files

    with BackupContext(argparse_callback) as context:
        target_name = context.get_parser_argument('target')
        destination_id = context.get_parser_argument('destination')
        filename = context.get_parser_argument('filename')  # TODO allow omitting extension
        put_back = context.get_parser_argument("put_back")

        print "put back", put_back

        context.dry_run = not put_back
        if context.dry_run:
            restore_dir = filename
            if restore_dir.endswith('.tar.gz'):
                restore_dir = restore_dir[:-7]
            if restore_dir.endswith('.tgz'):
                restore_dir = restore_dir[:-4]
            restore_dir += '.restore'
            os.mkdir(restore_dir)
            context.set_temp_dir(restore_dir, delete=False)
        else:
            context.set_temp_dir()

        targets = context.get_targets(target_name)
        destinations = context.get_destinations(destination_id)

        if not targets:
            context.log_error("Unknown target {0}".format(context.target_name))
            sys.exit(2)
        if len(targets) != 1:
            context.log_error('You must specify exactly one target to restore')
            sys.exit(2)

        if not destinations:
            context.log_error("Unknown destination {0}".format(context.target_name))
            sys.exit(3)
        if len(destinations) != 1:
            context.log_error('You must specify exactly one destination from which to restore')
            sys.exit(3)

        destination = destinations[0]
        target = targets[0]

        local_download_path = destination.download(filename, context.temp_dir)

        with TarArchive(local_download_path, write = False) as tar_archive:
            target.restore(tar_archive)

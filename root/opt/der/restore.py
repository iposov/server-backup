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

        parser.add_argument("-t", "--temporary-dir", required=False, default=None)
        parser.add_argument("-D", "--delete-temporary-dir", required=False, default=None)


    def delete_temporary_dir(arg_value, default):
        if arg_value == '1' or arg_value == 'yes' or arg_value == 'true':
            return True
        elif arg_value is None:
            return default
        else:
            return False


    with BackupContext(argparse_callback) as context:
        target_name = context.get_parser_argument('target')
        destination_id = context.get_parser_argument('destination')
        filename = context.get_parser_argument('filename')  # TODO allow omitting extension
        put_back = context.get_parser_argument("put_back")
        temporary_dir = context.get_parser_argument("temporary_dir")
        dtd = context.get_parser_argument('delete_temporary_dir')

        print "put back", put_back

        context.dry_run = not put_back
        if context.dry_run:
            if temporary_dir is None:
                restore_dir = filename
                if restore_dir.endswith('.tar.gz'):
                    restore_dir = restore_dir[:-7]
                if restore_dir.endswith('.tgz'):
                    restore_dir = restore_dir[:-4]
                restore_dir += '.restore'
                if not os.path.isdir(restore_dir):
                    os.mkdir(restore_dir)
            else:
                restore_dir = temporary_dir

            context.set_temp_dir(restore_dir, delete=delete_temporary_dir(dtd, False))
        else:
            context.set_temp_dir(temporary_dir, delete=delete_temporary_dir(dtd, True))

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

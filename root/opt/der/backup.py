#!/usr/bin/python
import sys

# TODO encrypt backups, use gpg with an asymmetric key
# TODO save output to log
from lib.backup.BackupContext import BackupContext
from lib.backup.TarArchive import TarArchive


if __name__ == '__main__':
    def argparse_callback(parser):
        parser.add_argument("target", help="target id or 'all'")
        parser.add_argument("destination", help="id of a destination to store backup")

    with BackupContext(argparse_callback) as context:
        target_name = context.get_parser_argument('target')
        destination_id = context.get_parser_argument('destination')

        context.set_temp_dir()

        targets = context.get_targets(target_name)
        destinations = context.get_destinations(destination_id)

        if not targets:
            context.log_error("Unknown target {0}".format(context.target_name))
            sys.exit(2)

        if not destinations:
            context.log_error("Unknown destination {0}".format(context.target_name))
            sys.exit(3)

        tar_archives_paths = []
        for target in targets:
            tar_path = target.tar_path()
            with TarArchive(tar_path) as tar_archive:
                tar_elements = target.run()
                for tar_element in tar_elements:
                    context.log(u'taring {} as {}'.format(tar_element.path, tar_element.tar_path))
                    tar_archive.add(tar_element)
                tar_archives_paths.append(tar_path)

        for destination in destinations:
            for tar_path in tar_archives_paths:
                destination.upload(tar_path)

        # TODO remove old backups

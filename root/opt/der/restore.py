#!/usr/bin/python
import sys

from lib.backup.BackupContext import BackupContext


if __name__ == '__main__':
    def argparse_callback(parser):
        parser.add_argument("target", help="target id")
        parser.add_argument("destination", help="id of a destination to store backup")
        parser.add_argument("filename", help="filename to restore")  # TODO make it possible to list files

    with BackupContext(argparse_callback) as context:
        target_name = context.get_parser_argument('target')
        destination_id = context.get_parser_argument('destination')
        filename = context.get_parser_argument('filename')

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

        destination.download(filename, context.temp_dir)
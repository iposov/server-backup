#!/usr/bin/python
import sys

# TODO encrypt backups, use gpg with an asymmetric key
# TODO save output to log
from lib.backup.BackupContext import BackupContext
from lib.backup.TarArchive import TarArchive


if __name__ == '__main__':
    with BackupContext() as context:
        targets = context.get_targets()
        destinations = context.get_destinations()

        if not targets:
            print >> sys.stderr, "Unknown target {0}".format(context.target_name)
            sys.exit(2)

        if not targets:
            print >> sys.stderr, "Unknown destination {0}".format(context.target_name)
            sys.exit(3)

        tar_archives = []
        for target in targets:
            tar_path = target.tar_path()
            with TarArchive(tar_path) as tar_archive:
                tar_elements = target.run()
                for tar_element in tar_elements:
                    context.log('taring %s' % tar_element.description())
                    tar_archive.add(tar_element)
                tar_archives.append(tar_archive)

        #TODO destination send
        # for destination in destinations:
        #     for tar_archive in tar_archives:
        #         destination.send()

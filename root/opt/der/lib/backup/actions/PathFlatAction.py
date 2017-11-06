from Action import Action
from TarElement import TarElement

import glob
import fnmatch
import os


def _matches(path, glob):
    # TODO we must be sure that this works exactly as glob.glob() does
    path_s = path.split('/')
    glob_s = glob.split('/')
    if len(path_s) != len(glob_s):
        return False
    for i in xrange(0, len(path_s)):
        if not fnmatch.fnmatch(path_s[i], glob_s[i]):
            return False
    return True


class PathFlatAction(Action):
    NAME = 'paths-flat'

    def __init__(self, target, action_description):
        Action.__init__(self, target, action_description)
        self.folder_glob = self.action_description[PathFlatAction.NAME]

    def run(self):
        paths_from_glob = glob.glob(self.folder_glob)

        if len(paths_from_glob) == 0:
            self.context.log_error("did not find path(s): " + self.folder_glob)

        tar = []
        for path in paths_from_glob:
            tar.append(TarElement(self.target.context, os.path.abspath(path), temporary=False))

        return tar

    def pre_restore(self, tar):
        glob = self.folder_glob
        if glob.startswith('/'):
            glob = glob[1:]

        tar_elements = []
        for path in tar.iterate_tar_paths():
            if _matches(path, glob):
                tar_elements.append(TarElement(self.target.context, path, temporary=False))

        return tar_elements

    def restore(self):
        if self.context.dry_run:
            return

        restore_path = self.tar_element.path


        pass
from Action import Action
from TarElement import TarElement

import glob
import fnmatch
import os


class PathAction(Action):
    NAME = 'paths'

    def __init__(self, target, action_description):
        Action.__init__(self, target, action_description)
        self.folder_glob = self.action_description[PathAction.NAME]

    def _path_infix(self):
        return self.folder_glob.replace('/', '--').replace('*', '_S_').replace('?', '_Q_')

    def run(self):
        paths_from_glob = glob.glob(self.folder_glob)

        if len(paths_from_glob) == 0:
            self.context.log_error("did not find path(s): " + self.folder_glob)

        tar = []
        for path in paths_from_glob:
            # TODO realpath eliminates information about the name of the soft link
            tar.append(TarElement(self.target.context, os.path.realpath(os.path.abspath(path)), temporary=False, path_infix=self._path_infix()))

        return tar

    def pre_restore(self, tar):
        tar_elements = []
        tar_prefix = self._path_infix()

        for path in tar.iterate_tar_paths():
            split_path = path.split('/')
            if split_path[0] == tar_prefix:
                split_path.pop(0)
                tar_elements.append(TarElement(self.target.context, '/'.join(split_path), temporary=False, path_infix=tar_prefix))

        return tar_elements

    def restore(self):
        pass

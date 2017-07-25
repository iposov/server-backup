from Action import Action
from glob import glob
from TarElement import TarElement


class PathAction(Action):
    NAME = 'paths'

    def tar_elements(self):
        folder_glob = self.action_description[PathAction.NAME]
        paths_from_glob = glob(folder_glob)
        if len(paths_from_glob) == 0:
            self.context.log_error("did not find path(s): " + folder_glob)

        tar = []
        for path in paths_from_glob:
            tar.append(TarElement(path, None))

        return tar

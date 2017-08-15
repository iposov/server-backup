from Destination import Destination

import shutil
import os


class PathDestination(Destination):

    NAME = 'path'

    def __init__(self, context, destination_id, destination_description):
        Destination.__init__(self, context, destination_id, destination_description)
        self.path = destination_description[PathDestination.NAME]
        if not os.path.exists(self.path):
            context.log_error('path for path-destination does not exist: ' + self.path)

    def remote_path(self, name):
        return os.path.join(self.path, name)

    def upload(self, local_path):
        name = os.path.basename(local_path)
        shutil.copyfile(local_path, self.remote_path(name))

    def remove(self, file_name):
        os.remove(self.remote_path(file_name))

    def list_files(self):
        os.listdir(self.path)

    def download(self, file_name, local_dir):
        local_download_path = os.path.join(local_dir, file_name)
        shutil.copyfile(self.remote_path(file_name), local_download_path)
        return local_download_path

    def close(self):
        pass
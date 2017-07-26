from Destination import Destination

import shutil
import os


class PathDestination(Destination):

    NAME = 'path'

    def __init__(self, destination_id, destination_description):
        Destination.__init__(self, destination_id, destination_description)
        self.path = destination_description[PathDestination.NAME]

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
        shutil.copyfile(self.remote_path(file_name), os.path.join(local_dir, file_name))

    def close(self):
        pass
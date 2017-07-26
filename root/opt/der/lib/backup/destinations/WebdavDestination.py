from Destination import Destination

import urlparse

class WebdavDestination(Destination):

    NAME = 'webdav'

    def __init__(self, destination_id, destination_description):
        path = destination_description[WebdavDestination.NAME]

        #parse path
        url = urlparse.urlparse(path)
        #TODO here

    def upload(self, local_path):
        Destination.upload(self, local_path)

    def remove(self, file_name):
        Destination.remove(self, file_name)

    def list_files(self):
        Destination.list_files(self)

    def download(self, file_name, local_dir):
        Destination.download(self, file_name, local_dir)

    def close(self):
        Destination.close(self)


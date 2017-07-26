class Destination:
    @staticmethod
    def create(destination_id, destination_description):
        import PathDestination, WebdavDestination
        destinations = [PathDestination.PathDestination, WebdavDestination.WebdavDestination]
        for d in destinations:
            if d.NAME in destination_description:
                return d(destination_id, destination_description)

        pass

    def __init__(self, destination_id, destination_description):
        self.destination_id = destination_id
        self.destination = destination_description

    def upload(self, local_path):
        pass

    def download(self, file_name, local_dir):
        pass

    # return list of file names
    def list_files(self):
        pass

    def remove(self, file_name):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
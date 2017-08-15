class Destination:

    @staticmethod
    def create(context, destination_id, destination_description):
        import PathDestination, WebdavDestination
        destinations = [PathDestination.PathDestination, WebdavDestination.WebdavDestination]
        for d in destinations:
            if d.NAME in destination_description:
                return d(context, destination_id, destination_description)

        pass

    def __init__(self, context, destination_id, destination_description):
        self.context = context
        self.destination_id = destination_id
        self.destination = destination_description

    def upload(self, local_path):
        pass

    # should return local download path
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
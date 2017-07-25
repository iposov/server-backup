import tarfile


class TarArchive:

    def __init__(self, path, write=True):
        self.path = path

        if write:
            mode = "w:gz"
        else:
            mode = "r:gz"

        self.tar_file = tarfile.open(path, mode=mode)

    def __enter__(self):
        self.tar_file.__enter__()
        return self

    def add(self, tar_element):
        self.tar_file.add(tar_element.path, arcname=tar_element.tar_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.tar_file.__exit__(exc_type, exc_val, exc_tb)

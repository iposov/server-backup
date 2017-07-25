class TarElement:

    def __init__(self, path, tar_name):
        self.path = path
        self.tar_name = tar_name

    def description(self):
        if self.tar_name is None:
            return self.path
        else:
            return self.tar_name + ' at ' + self.path
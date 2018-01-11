import tarfile
import os


def _ensure_not_absolute(path):
    if path.startswith('/'):
        return path[1]
    else:
        return path


def _ensure_is_dir(path):
    if path.endswith('/'):
        return path
    else:
        return path + '/'


def _tar_file_name_to_unicode(filename):
    # TODO are we sure that tar has UTF-8 inside?
    return unicode(filename, encoding="utf8")


class TarArchive:
    def __init__(self, path, write=True):
        self.path = path

        if write:
            mode = "w:gz"
        else:
            mode = "r:gz"

        print "opening", path
        #dereference: https://stackoverflow.com/a/39321142
        #set dereference to false because the size of backup may become very large
        self.tar_file = tarfile.open(path, mode=mode, errorlevel=1, dereference=False)

    def __enter__(self):
        self.tar_file.__enter__()
        return self

    def add(self, tar_element):
        self.tar_file.add('/' + tar_element.path, arcname=tar_element.tar_path)

    def extract(self, tar_element):
        extract_path_prefix = tar_element.tar_path
        extract_path_prefix_as_folder = _ensure_is_dir(extract_path_prefix)

        extract_path_prefix_for_tar_module = tar_element.path_prefix.encode('utf8')

        for file_ in self.tar_file:
            name = _ensure_not_absolute(_tar_file_name_to_unicode(file_.name))

            if name == extract_path_prefix or name.startswith(extract_path_prefix_as_folder):
                local_path = tar_element.path
                try:
                    if tar_element.path_infix is not None:
                        file_.path = file_.path[len(tar_element.path_infix):]
                    self.tar_file.extract(file_, path=extract_path_prefix_for_tar_module)
                except IOError as e:  # try again if error occurs, but prevously remove a file that may have existed there
                    pass
                    os.remove(local_path)
                    self.tar_file.extract(file_, path=extract_path_prefix_for_tar_module)
                finally:
                    pass
                    # os.chmod(local_path, file_.mode)

    def iterate_tar_paths(self):
        for file_ in self.tar_file:
            yield _ensure_not_absolute(_tar_file_name_to_unicode(file_.name))

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.tar_file.__exit__(exc_type, exc_val, exc_tb)

import os


def _ensure_not_absolute(path):
    if path.startswith('/'):
        path = path[1:]
    return path


def _ensure_absolute(path):
    if not path.startswith('/'):
        path = u'/' + path
    return path


def _path_prefix(context, temporary):
    base_dir = _ensure_absolute(context.temp_dir)
    enforce_base_dir = context.dry_run

    if enforce_base_dir or temporary:
        result = base_dir
    else:
        result = u''

    return _ensure_absolute(result)


class TarElement:

    # path and tar_name must be always local
    def __init__(self, context, path, temporary=True, path_infix=None):
        path = _ensure_not_absolute(path)

        self.path_prefix = _path_prefix(context, temporary)

        # TODO make this properties
        self.path = os.path.join(self.path_prefix, path)
        self.tar_path = path
        self.path_infix = path_infix
        if path_infix is not None:
            self.tar_path = os.path.join(path_infix, self.tar_path)

    def ensure_path_exists(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)


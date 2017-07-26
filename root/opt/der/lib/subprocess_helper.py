import subprocess


def call(args_list, logger=None):
    def escape_argument(arg):
        return "'" + arg.replace("'", "'\''") + "'"

    command_line_args = [arg[0] if isinstance(arg, list) else escape_argument(arg) for arg in args_list]
    # TODO use Popen constructor and communicate to get stderr/stdout
    command_line = " ".join(command_line_args)

    if logger is not None:
        logger('issuing command: ' + command_line)

    return subprocess.call(command_line, shell=True)
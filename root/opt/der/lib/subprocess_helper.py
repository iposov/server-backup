import subprocess


def call(args_list, logger=None):
    def escape_argument(arg):
        return "'" + arg.replace("'", "'\\''") + "'"

    command_line_args = []
    command_line_args_to_print = []

    for arg_info in args_list:
        print_arg = True
        escape_arg = True

        if isinstance(arg_info, list):
            arg = arg_info[0]
            for i in xrange(1, len(arg_info)):
                command = arg_info[i]
                if command == 'as-is':
                    escape_arg = False
                elif command == 'secret':
                    print_arg = False
        else:
            arg = arg_info

        if escape_arg:
            arg = escape_argument(arg)

        command_line_args.append(arg)
        command_line_args_to_print.append(arg if print_arg else '[[secret]]')

    # TODO use Popen constructor and communicate to get stderr/stdout
    command_line = " ".join(command_line_args)
    command_line_to_print = " ".join(command_line_args_to_print)

    if logger is not None:
        logger('issuing command: ' + command_line_to_print)

    return subprocess.call(command_line, shell=True)


def _ensure_wrapped(arg):
    if not isinstance(arg, list):
        return [arg]
    else:
        return arg


def secret(arg):
    arg = _ensure_wrapped(arg)
    return arg + ['secret']


def as_is(arg):
    arg = _ensure_wrapped(arg)
    return arg + ['as-is']
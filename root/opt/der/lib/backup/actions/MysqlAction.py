from Action import Action
from TarElement import TarElement

import os
import lib.subprocess_helper as sh


class MysqlAction(Action):

    NAME = 'mysql'

    def __init__(self, target, action_description):
        Action.__init__(self, target, action_description)

        tar_element_name = self.target.name + '-mysql-backup'
        self.tar_element = TarElement(target.context, tar_element_name)
        self.tar_element.ensure_path_exists()

    def run(self):
        mysql_command = ["mysqldump", "-B"]

        host = self.add_standard_args_to_mysql_command(mysql_command)

        db_name = self.get_db_name()
        mysql_command += [db_name, sh.as_is('>'), self.tar_db_path()]

        self.context.log("backup: Starting mysql dump for db {} on host {}".format(db_name, host))
        return_code = sh.call(mysql_command, logger=self.context.log)

        if return_code != 0:
            self.context.log_error("Failed to create mysql dump, return code {}".format(return_code))
        else:
            self.context.log("backup: mysql dump successful")

        return [self.tar_element]

    def add_standard_args_to_mysql_command(self, mysql_command):
        self._add_credentials_to_mysql_command(mysql_command)
        host = self._add_host_to_mysql_command(mysql_command)
        return host

    def _add_host_to_mysql_command(self, mysql_command):
        host = self.action_description.get('host', '$local')  # TODO implement other hosts
        if host != '$local':
            mysql_command += ['-h', host]

        return host

    def _add_credentials_to_mysql_command(self, mysql_command):
        db_name = self.get_db_name()

        if 'auth' in self.action_description:
            auth = self.action_description['auth']

            credentials = self.context.credentials.get(auth, None)
            if credentials is None:
                self.context.log_error("credentials '%s' needed for mysql db %s" % (auth, db_name))

            user = credentials['login']
            password = credentials['password']

            mysql_command += ['-u', user, sh.secret('-p%s' % password)]

    def tar_db_path(self):
        return os.path.join(self.tar_element.path, self.get_db_name() + '.sql')

    def get_db_name(self):
        db_name = self.action_description[MysqlAction.NAME]
        return db_name

    def pre_restore(self, tar):
        return [self.tar_element]

    def restore(self):
        if self.context.dry_run:
            return

        mysql_command = ['mysql']

        host = self.add_standard_args_to_mysql_command(mysql_command)

        mysql_command += [sh.as_is("<"), self.tar_db_path()]

        self.context.log("restore: Starting mysql restore for db %s on host %s" % (self.get_db_name(), host))
        return_code = sh.call(mysql_command, logger=self.context.log)

        if return_code != 0:
            self.context.log_error("Failed to restore mysql, return code %d" % return_code)
        else:
            self.context.log("restore: mysql restore successful")

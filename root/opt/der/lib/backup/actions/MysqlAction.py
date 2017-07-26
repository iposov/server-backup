from Action import Action

import os
import lib.subprocess_helper as sh


class MysqlAction(Action):

    NAME = 'mysql'

    def _tar_element_name(self):
        return self.target.name + '-mysql-backup'

    def run(self):
        Action.run(self)

        db_name = self.action_description[MysqlAction.NAME]

        mysql_command = ["mysqldump", "-B"]

        if 'auth' in self.action_description:
            auth = self.action_description['auth']

            credentials = self.context.credentials.get(auth, None)
            if credentials is None:
                self.context.log_error("credentials '%s' needed for mysql db %s" % (auth, db_name))

            user = credentials['login']
            password = credentials['password']

            mysql_command += ['-u', user, sh.secret('-p%s' % password)]

        mysql_command += [db_name, sh.as_is('>'), os.path.join(self.tar_element().path, db_name + '.sql')]

        host = self.action_description.get('host', '$local')
        if host != '$local':
            mysql_command += ['-h', host]

        # TODO implement other hosts
        self.context.log("backup: Starting mysql dump for db %s on host %s" % (db_name, host))
        return_code = sh.call(mysql_command, logger=self.context.log)

        if return_code != 0:
            self.context.log_error("Failed to create mysql dump, return code %d" % return_code)
        else:
            self.context.log("backup: mysql dump successful")
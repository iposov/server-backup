from Action import Action
from lib.subprocess_helper import call


class MongoAction(Action):
    NAME = "mongo"

    def _tar_element_name(self):
        return self.target.name + '-mongo-backup'

    def run(self):
        Action.run(self)

        db_name = self.action_description[MongoAction.NAME]

        mongo_command = ["mongodump", "--db", db_name, "-o", self._tar_element().path]

        host = self.action_description.get('host', '$local')
        if host != '$local':
            mongo_command += ["--host", host]

        self.context.log("backup: Starting mongo dump for db %s on host %s" % (db_name, host))
        return_code = call(mongo_command, logger=self.context.log)

        if return_code != 0:
            self.context.log_error("backup: failed to create mongo dump, exit code %d" % return_code)
        else:
            self.context.log('backup: mongo dump successful')

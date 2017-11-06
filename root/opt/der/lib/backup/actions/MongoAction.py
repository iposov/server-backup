import os

from Action import Action
from TarElement import TarElement
from lib.subprocess_helper import call


class MongoAction(Action):
    NAME = "mongo"

    def __init__(self, target, action_description):
        Action.__init__(self, target, action_description)

        tar_element_name = self.target.name + '-mongo-backup'
        self.tar_element = TarElement(target.context, tar_element_name)
        self.tar_element.ensure_path_exists()

    def run(self):
        Action.run(self)

        db_name = self.action_description[MongoAction.NAME]

        mongo_command = ["mongodump", "--db", db_name, "-o", self.tar_element.path]

        host = self.action_description.get('host', '$local')
        if host != '$local':
            mongo_command += ["--host", host]

        self.context.log("backup: Starting mongo dump for db %s on host %s" % (db_name, host))
        return_code = call(mongo_command, logger=self.context.log)

        if return_code != 0:
            self.context.log_error("backup: failed to create mongo dump, exit code %d" % return_code)
        else:
            self.context.log('backup: mongo dump successful')

        return [self.tar_element]

    def pre_restore(self, tar):
        return [self.tar_element]

    def restore(self):
        db_name = self.action_description[MongoAction.NAME]

        mongo_command = ["mongorestore", "--db", db_name]

        host = self.action_description.get('host', '$local')
        if host != '$local':
            mongo_command += ["--host", host]

        if self.context.dry_run:
            mongo_command += ["--dryRun"]

        mongo_command += [os.path.join(self.tar_element.path, db_name)]

        self.context.log("backup: Starting mongo restore for db {} on host {}".format(db_name, host))
        return_code = call(mongo_command, logger=self.context.log)

        if return_code != 0:
            self.context.log_error("backup: failed to create mongo dump, exit code {}".format(return_code))
        else:
            self.context.log('backup: mongo dump successful')


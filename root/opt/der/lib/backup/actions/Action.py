import os


class Action:

    @staticmethod
    def create(target, action_description):
        import PathAction, MongoAction, MysqlAction
        actions = [PathAction.PathAction, MongoAction.MongoAction, MysqlAction.MysqlAction]
        for a in actions:
            if a.NAME in action_description:
                return a(target, action_description)
        target.context.log_error("Action description can not be recognized")
        import sys
        sys.exit(1)

    def __init__(self, target, action_description):
        """
        :type target: Target.Target
        :type action_description: object
        """
        self.target = target
        self.action_description = action_description

        self.context = target.context

    def run(self):
        pass

    #  returns tar elements to untar
    def pre_restore(self, tar):
        pass

    def restore(self):
        pass
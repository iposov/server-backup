import os

from TarElement import TarElement


class Action:

    @staticmethod
    def create(target, action_description):
        import PathAction, MongoAction, MysqlAction
        actions = [PathAction.PathAction, MongoAction.MongoAction, MysqlAction.MysqlAction]
        for a in actions:
            if a.NAME in action_description:
                return a(target, action_description)

    def __init__(self, target, action_description):
        """
        :type target: Target.Target
        :type action_description: object
        """
        self.target = target
        self.action_description = action_description

        self.context = target.context

    def _tar_element_name(self):
        return None

    def tar_elements(self):
        tar_element_name = self._tar_element_name()

        if tar_element_name is None:
            return []
        else:
            return [TarElement(
                self.context.temp_path(tar_element_name),
                tar_element_name
            )]

    def _tar_element(self):
        return self.tar_elements()[0]

    # create paths if they do not exist, TODO make creating paths a separate function
    def run(self):
        tar_elements = self.tar_elements()
        for tar_element in tar_elements:
            if not os.path.exists(tar_element.path):
                os.makedirs(tar_element.path)

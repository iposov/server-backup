from actions.Action import Action
import re
import os
from datetime import datetime

_TIME_FORMAT_ = "%m-%d-%y--%H-%M-%S"


class Target:
    def __init__(self, context, target_name, target_description):
        """
        :type context: BackupContext
        :type target_name: string name of the target
        :type target_description: object yaml description of a target, an array of yaml objects
        """
        self.context = context
        self.name = target_name
        self.actions = []
        for action_description in target_description:
            self.actions.append(Action.create(self, action_description))

    def run(self):
        tar_elements = []

        for action in self.actions:
            tar_elements.extend(action.tar_elements())
            action.run()

        return tar_elements

    def tar_name(self):
        # TODO we previously had a postfix here, but did not use it
        time = self.context.now.strftime(_TIME_FORMAT_)
        return self.name + '-' + self.context.host + '-' + time + '.tar.gz'

    def tar_path(self):
        return self.context.temp_path(self.tar_name())

    @staticmethod
    def parse_tar_name(path):
        name = os.path.basename(path)
        match = re.search("\d\d-\d\d-\d\d--\d\d-\d\d-\d\d", name)
        if match is None:
            return None
        return datetime.strptime(match.group(0), _TIME_FORMAT_)
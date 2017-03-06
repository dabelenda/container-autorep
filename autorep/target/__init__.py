import autorep


class AbstractTargetDriver(object):

    def get_state(self, hostlist):
        return autorep.ReplicationList()

    def apply_changes(self, hostlist, current, changes):
        pass

import autorep


class AbstractReplicationGraphBuilder(object):
    def get_changes(self, hostlist, currentstate):
        return autorep.ReplicationList()


import autorep


class AbstractClusteringDecider(object):
    def get_cluster_changes(self, localchanges):
        return autorep.ReplicationList()

import autorep.clustering


class StandaloneDecider(autorep.clustering.AbstractClusteringDecider):

    def get_cluster_changes(self, localchanges):
        return localchanges

import clustering
import autorep


class StandaloneDecider(clustering.AbstractClusteringDecider):

    def get_cluster_changes(self, localchanges):
        return localchanges

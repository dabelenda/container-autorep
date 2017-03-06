import replication
import autorep
import networkx as nx


class AllMasterGraphBuilder(replication.AbstractReplicationGraphBuilder):

    def get_changes(self, hostlist, currentstate):
        dg=nx.DiGraph()
        ret = []

        # build the full directionnal mesh of all replications possible
        for i in hostlist:
            for j in hostlist:
                if i == j:
                    continue
                dg.add_edge(i, j, object=autorep.ReplicationMode.OneWay)

        for rep in currentstate:
            if rep.source not in hostlist or rep.target not in hostlist:
            # target or host does not exist anymore, remove the replication entry
                dg.add_edge(rep.source, rep.target, object=autorep.ReplicationMode.Remove)
                continue
            # the replication is already here, remove it from the graph
            dg.remove_edge(rep.source, rep.target)

        # convert graph to ReplicationList
        for (u, v, d) in dg.edges(data='object'):
            ret.append( autorep.ReplicationDefinition(u, v, d) )

        return autorep.ReplicationList( ret )


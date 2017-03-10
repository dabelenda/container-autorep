import unittest
from unittest.mock import sentinel
import autorep.replication.fullmesh


class TestAllMasterGraphBuilder(unittest.TestCase):

    def test_get_changes_with_empty_current(self):
        hostlist = [sentinel.host1, sentinel.host2, sentinel.host3]
        currentreplist = []
        ReplicationDefinition = unittest.mock.MagicMock()
        ReplicationList = unittest.mock.MagicMock()
        ReplicationMode = unittest.mock.MagicMock()
        ReplicationMode.OneWay = sentinel.oneway

        with unittest.mock.patch('autorep.ReplicationList', ReplicationList), unittest.mock.patch('autorep.ReplicationDefinition', ReplicationDefinition), unittest.mock.patch('autorep.ReplicationMode', ReplicationMode):
            autorep.replication.fullmesh.AllMasterGraphBuilder().get_changes(hostlist, currentreplist)

        calls = ReplicationDefinition.mock_calls

        for i in hostlist:
            for j in hostlist:
                if not i == j:
                    self.assertIn( unittest.mock.call(i, j, ReplicationMode.OneWay), calls )
                    calls.remove( unittest.mock.call(i, j, ReplicationMode.OneWay) )
        self.assertEqual( [], calls )

    def test_get_changes_with_one_new_host(self):
        hostlist = [sentinel.host1, sentinel.host2, sentinel.host3]
        currentreplist = []
        ReplicationDefinition = unittest.mock.MagicMock()
        ReplicationList = unittest.mock.MagicMock()
        ReplicationMode = unittest.mock.MagicMock()
        ReplicationMode.OneWay = sentinel.oneway

        for i in hostlist[0:len(hostlist)-1]:
            for j in hostlist[0:len(hostlist)-1]:
                if not i == j:
                    tmp = unittest.mock.MagicMock()
                    tmp.source = i
                    tmp.target = j

                    currentreplist.append( tmp )

        with unittest.mock.patch('autorep.ReplicationList', ReplicationList), unittest.mock.patch('autorep.ReplicationDefinition', ReplicationDefinition), unittest.mock.patch('autorep.ReplicationMode', ReplicationMode):
            autorep.replication.fullmesh.AllMasterGraphBuilder().get_changes(hostlist, currentreplist)

        calls = ReplicationDefinition.mock_calls

        for i in hostlist:
            for j in hostlist:
                if not i == j and ( i == hostlist[len(hostlist)-1] or j == hostlist[len(hostlist)-1] ):
                    self.assertIn( unittest.mock.call(i, j, ReplicationMode.OneWay), calls )
                    calls.remove( unittest.mock.call(i, j, ReplicationMode.OneWay) )
        self.assertEqual( [], calls )

    def test_get_changes_with_one_less_node(self):
        hostlist = [sentinel.host1, sentinel.host2, sentinel.host3]
        currentreplist = []
        ReplicationDefinition = unittest.mock.MagicMock()
        ReplicationList = unittest.mock.MagicMock()
        ReplicationMode = unittest.mock.MagicMock()
        ReplicationMode.Remove = sentinel.remove

        for i in hostlist:
            for j in hostlist:
                if not i == j:
                    tmp = unittest.mock.MagicMock()
                    tmp.source = i
                    tmp.target = j

                    currentreplist.append( tmp )

        with unittest.mock.patch('autorep.ReplicationList', ReplicationList), unittest.mock.patch('autorep.ReplicationDefinition', ReplicationDefinition), unittest.mock.patch('autorep.ReplicationMode', ReplicationMode):
            autorep.replication.fullmesh.AllMasterGraphBuilder().get_changes(hostlist[0:len(hostlist)-1], currentreplist)

        calls = ReplicationDefinition.mock_calls

        for i in hostlist:
            for j in hostlist:
                if not i == j and ( i == hostlist[len(hostlist)-1] or j == hostlist[len(hostlist)-1] ):
                    self.assertIn( unittest.mock.call(i, j, ReplicationMode.Remove), calls )
                    calls.remove( unittest.mock.call(i, j, ReplicationMode.Remove) )
        self.assertEqual( [], calls )


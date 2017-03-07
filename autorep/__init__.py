""" Module
"""
import time
import sys
import enum


class ReplicationMode(enum.Enum):
    """ Class
    """

    OneWay = "oneway"
    Remove = "remove"


class ReplicationDefinition(object):
    """ Class
    """

    def __init__(self, source, target, mode=ReplicationMode.OneWay):
        if not isinstance(mode, ReplicationMode):
            raise ValueError("Argument mode must be instance of ReplicationMode")
        if not isinstance(source, str):
            raise ValueError("Argument source must be a string")
        if not isinstance(target, str):
            raise ValueError("Argument target must be a string")

        self.source = source
        self.target = target
        self.mode = mode

    def __str__(self):
        return "%s from: \"%s\" to \"%s\" " % (self.mode, self.source, self.target)


class ReplicationList(object):
    """ Class
    """

    def __init__(self, *args):
        pos = 0
        if len(args) == 1 and isinstance(args, tuple):
            args = args[0]
        self.replications = []
        for arg in args:
            pos += 1
            try:
                self.add(arg)
            except ValueError as exce:
                raise ValueError("At position %i: %s" % (pos, exce))
    def __str__(self):
        ret = "ReplicationList("

        for each in self.replications:
            ret = ret + ("(%s), " % str(each))

        ret = ret + ")"
        return ret

    def __iter__(self):
        return self.replications.__iter__()

    def add(self, repdef):
        """ pack
        """
        if not isinstance(repdef, ReplicationDefinition):
            raise ValueError("Argument is not a ReplicationDefinition instance")

        self.replications.append(repdef)

    def pack(self):
        """ pack
        """
        pass


def main_loop(conf, sourcedriver, targetdriver, graphdriver, clusteringdriver):
    """ pack
    """
    while True:
        try:
            hostlist = sourcedriver.get_hostlist()
            currentstate = targetdriver.get_state(hostlist)
            localchanges = graphdriver.get_changes(hostlist, currentstate)
            clusterchanges = clusteringdriver.get_cluster_changes(localchanges)
            targetdriver.apply_changes(hostlist, currentstate, clusterchanges)
        except Exception as exce:
            print("Failed to update state: " + str(exce))
            raise exce

        sys.stdout.flush()
        time.sleep(conf['AUTOREP_UPDATE_PERIOD'])


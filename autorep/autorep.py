""" Module
"""
import time
import sys
import importlib
import inspect
import enum

import envconfig
import target
import source
import clustering
import replication


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


def get_driver_class(modulename, baseclass):
    """ pack
    """
    mod = importlib.import_module(modulename)
    klass = None

    for klassname in dir(mod):
        tmpklass = getattr(mod, klassname)
        if not inspect.isclass(tmpklass):
            continue
        if issubclass(tmpklass, baseclass) and not tmpklass == baseclass:
            if klass is not None:
                raise envconfig.InvalidConfig("Multiple candidate classes available in %s" %
                                              modulename)
            klass = tmpklass

    return klass


def main_loop(conf, sourcedriver, targetdriver, graphdriver):
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


if __name__ == '__main__':
    env_vars_def = {
        'AUTOREP_TARGET_DRIVER_MODULE' : {
            envconfig.Options.parser: envconfig.Parser.String,
            envconfig.Options.required: lambda conf: True,
        },
        'AUTOREP_SOURCE_DRIVER_MODULE' : {
            envconfig.Options.parser: envconfig.Parser.String,
            envconfig.Options.required: lambda conf: True,
        },
        'AUTOREP_CLUSTERING_DRIVER_MODULE' : {
            envconfig.Options.parser: envconfig.Parser.String,
            envconfig.Options.required: lambda conf: True,
        },
        'AUTOREP_REPLICATION_GRAPH_DRIVER_MODULE' : {
            envconfig.Options.parser: envconfig.Parser.String,
            envconfig.Options.required: lambda conf: True,
        },
        'AUTOREP_UPDATE_PERIOD' : {
            envconfig.Options.parser: envconfig.Parser.Integer,
            envconfig.Options.required: lambda conf: True,
        },
    }

    try:
        mainconf = envconfig.Parser.parse(env_vars_def)
    except envconfig.InvalidConfig as exce:
        print(exce)
        sys.exit(1)

    try:
        driverclass = get_driver_class('target.' + mainconf['AUTOREP_TARGET_DRIVER_MODULE'],
                                       target.AbstractTargetDriver)
        if driverclass is None:
            raise envconfig.InvalidConfig("No valid driver found in %s" % 'target.' +
                                          mainconf['AUTOREP_TARGET_DRIVER_MODULE'])
        targetdriver = driverclass()
    except ImportError:
        print("Target Driver \"%s\" does not exist" % mainconf['AUTOREP_TARGET_DRIVER_MODULE'])
        sys.exit(2)
    except envconfig.InvalidConfig as exce:
        print(exce)
        exit(3)

    try:
        driverclass = get_driver_class('source.' + mainconf['AUTOREP_SOURCE_DRIVER_MODULE'],
                                       source.AbstractSourceDriver)
        if driverclass is None:
            raise envconfig.InvalidConfig("No valid driver found in %s" % 'source.' +
                                          mainconf['AUTOREP_SOURCE_DRIVER_MODULE'])
        sourcedriver = driverclass()
    except ImportError as exce:
        print("Source Driver \"%s\" does not exist" % mainconf['AUTOREP_SOURCE_DRIVER_MODULE'])
        print(exce)
        sys.exit(4)
    except envconfig.InvalidConfig as exce:
        print(exce)
        exit(5)

    try:
        driverclass = get_driver_class('clustering.' + mainconf['AUTOREP_CLUSTERING_DRIVER_MODULE'],
                                       clustering.AbstractClusteringDecider)
        if driverclass is None:
            raise envconfig.InvalidConfig("No valid driver found in %s" % 'clustering.' +
                                          mainconf['AUTOREP_CLUSTERING_DRIVER_MODULE'])
        clusteringdriver = driverclass()
    except ImportError:
        print("Clustering Driver \"%s\" does not exist" %
              mainconf['AUTOREP_CLUSTERING_DRIVER_MODULE'])
        sys.exit(6)
    except envconfig.InvalidConfig as exce:
        print(exce)
        exit(7)

    try:
        driverclass = get_driver_class('replication.' +
                                       mainconf['AUTOREP_REPLICATION_GRAPH_DRIVER_MODULE'],
                                       replication.AbstractReplicationGraphBuilder)
        if driverclass is None:
            raise envconfig.InvalidConfig("No valid driver found in %s" % 'replication.' +
                                          mainconf['AUTOREP_REPLICATION_GRAPH_DRIVER_MODULE'])
        graphdriver = driverclass()
    except ImportError as exce:
        print("Replication Graph Driver \"%s\" does not exist" %
              mainconf['AUTOREP_REPLICATION_GRAPH_DRIVER_MODULE'])
        print(exce)
        sys.exit(8)
    except envconfig.InvalidConfig as exce:
        print(exce)
        exit(9)

    main_loop(mainconf, sourcedriver, targetdriver, graphdriver)

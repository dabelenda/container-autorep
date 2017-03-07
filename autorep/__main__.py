import sys
import envconfig
import importlib
import inspect
import autorep

from autorep import  target, source, clustering, replication

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
    driverclass = get_driver_class('autorep.target.' + mainconf['AUTOREP_TARGET_DRIVER_MODULE'],
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
    driverclass = get_driver_class('autorep.source.' + mainconf['AUTOREP_SOURCE_DRIVER_MODULE'],
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
    driverclass = get_driver_class('autorep.clustering.' + mainconf['AUTOREP_CLUSTERING_DRIVER_MODULE'],
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
    driverclass = get_driver_class('autorep.replication.' +
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

autorep.main_loop(mainconf, sourcedriver, targetdriver, graphdriver, clusteringdriver)


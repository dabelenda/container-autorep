import os
import enum


class Options(enum.Enum):
    required   = 1
    parser     = 2
    default    = 3
    enumvalues = 4


class InvalidConfig(ValueError):
    """Exception when an Environment variable is not correctly set."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def parse_boolean(key, vardef, rawval):
    truevals = [ 't', 'true', 'yes', 'y' ]
    falsevals = [ 'f', 'false', 'no', 'n' ]
    if rawval.lower() in truevals:
        return True
    if rawval.lower() in falsevals:
        return False
    raise InvalidConfig("Value for %s must be a Boolean (i.e. any value in %s case insensitive) got %s" % (key, truevals + falsevals, rawval))


def parse_integer(key, vardef, rawval):
    try:
        ret = int(rawval)
    except ValueError:
        raise InvalidConfig("Value for %s must be an Integer got %s", key, rawval)
    return ret


def parse_enum(key, vardef, rawval):
    mapping = vardef.get(Options.enumvalues, {})
    if not rawval in mapping:
        raise InvalidConfig("Value for Enum Variable %s (%s) is not in %s" % (key, rawval, list(mapping.keys()) ))

    return mapping[rawval]


def parse_string(key, vardef, rawval):
    return rawval


def getenv(name):
    ret = os.getenv(name)
    if ret is None:
        raise InvalidConfig("Environment Variable \"%s\" is not defined." % (name))
    return ret


class ConfigModel(object):
    """Class to check the configuration via env variables.
    """

    def __getitem__(self, key):
        return self.__dict__[key]

    def __init__(self, env_vars):
        for key, optiondef in env_vars.items():
            if optiondef.get(Options.default, None) is not None:
                self.__dict__[key] = optiondef[Options.default]
            try:
                self.__dict__[key] = optiondef[Options.parser](key, optiondef, getenv(key))
            except InvalidConfig as e:
                if optiondef.get(Options.required, lambda conf: False)(self):
                    raise e

    def get(self, key, default):
        return self.__dict__.get(key, default)


class Parser(enum.Enum):
    Boolean = parse_boolean
    Integer = parse_integer
    String = parse_string
    Enum   = parse_enum

    @staticmethod
    def parse(model_def):
        return ConfigModel(model_def)


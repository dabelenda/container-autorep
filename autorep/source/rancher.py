from . import AbstractSourceDriver
import envconfig

import urllib.request
import json


class Driver(AbstractSourceDriver):

    def __init__(self):
        env_vars_def= {
                'RANCHER_METADATA_APIVERSION' : {
                     envconfig.Options.parser: envconfig.Parser.String,
                     envconfig.Options.required: lambda conf: True,
                },
                'RANCHER_AUTOREP_TARGET_SERVICE_NAME' : {
                     envconfig.Options.parser: envconfig.Parser.String,
                     envconfig.Options.required: lambda conf: True,
                },
                'RANCHER_REFERENCE_CONAINTER_MODE' : {
                     envconfig.Options.parser: envconfig.Parser.Enum,
                     envconfig.Options.required: lambda conf: True,
                     envconfig.Options.enumvalues: {
                         'containerip' : 'primary_ip',
                         'containername' : 'name',
                     },
                },
        }
        self.conf = envconfig.Parser.parse(env_vars_def)

    def get_rancher(self, topic):
        url = 'http://rancher-metadata/%s/%s' % (self.conf['RANCHER_METADATA_APIVERSION'], topic)
        req = urllib.request.Request(url, headers={'Accept':'application/json'})
        return json.load(urllib.request.urlopen(req))

    def get_hostlist(self):
        stack_name = False
        if '/' in self.conf['RANCHER_AUTOREP_TARGET_SERVICE_NAME']:
            split = self.conf['RANCHER_AUTOREP_TARGET_SERVICE_NAME'].split('/') 
            stack_name = True
        if stack_name:
            topic = 'stacks/%s/services/%s/containers' % (split[0], split[1])
        else:
            topic = 'services/%s/containers' % (self.conf['RANCHER_AUTOREP_TARGET_SERVICE_NAME'])
        containerdata = self.get_rancher(topic)
        containerlist = []
        for container in containerdata:
            containerlist.append(container[self.conf['RANCHER_REFERENCE_CONAINTER_MODE']])

        return containerlist

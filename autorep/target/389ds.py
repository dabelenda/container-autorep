import envconfig
import ldap
import ldap.modlist as modlist
import tempfile

from . import AbstractTargetDriver
import autorep


class Driver(AbstractTargetDriver):
    def __init__(self):
        env_vars_def = {
            'LDAP_USE_LDAPS' : {
                 envconfig.Options.parser: envconfig.Parser.Boolean,
                 envconfig.Options.default: False,
            },
            'LDAP_USE_STARTTLS' : {
                 envconfig.Options.parser: envconfig.Parser.Boolean,
                 envconfig.Options.default: False,
            },
            'LDAP_PORT' : {
                 envconfig.Options.parser: envconfig.Parser.Integer,
            },
            'LDAP_CA_CERTIFICATE' : {
                 envconfig.Options.parser: envconfig.Parser.String,
            },
            'LDAP_BIND_DN' : {
                 envconfig.Options.parser: envconfig.Parser.String,
            },
            'LDAP_BIND_PASSWORD' : {
                 envconfig.Options.parser: envconfig.Parser.String,
                 envconfig.Options.required: lambda conf: conf.get('LDAP_BIND_DN', None) is not None,
            },
            'LDAP_REPLICATED_BASE_DN' : {
                 envconfig.Options.parser: envconfig.Parser.String,
                 envconfig.Options.required: lambda conf: True,
            },
            'LDAP_REPLICATION_DN' : {
                 envconfig.Options.parser: envconfig.Parser.String,
                 envconfig.Options.required: lambda conf: True,
            },
            'LDAP_REPLICATION_PASSWORD' : {
                 envconfig.Options.parser: envconfig.Parser.String,
                 envconfig.Options.required: lambda conf: True,
            },
        }
        self.conf = envconfig.Parser.parse(env_vars_def)


    def get_hostreplication_state(self, host, conn):
        res = conn.search_s('cn=mapping tree,cn=config', ldap.SCOPE_SUBTREE, 'cn=%s' % self.conf['LDAP_REPLICATED_BASE_DN'])
        myslaves = conn.search_s('%s' % res[0][0], ldap.SCOPE_SUBTREE, 'objectClass=nsds5replicationagreement')
        ret = []
        for each in myslaves:
            target = each[1]['nsDS5ReplicaHost'][0].decode('utf-8')
            val = autorep.ReplicationDefinition(source=host, target=target, mode=autorep.ReplicationMode.OneWay)
            ret.append(val)

        return ret

    def get_conn(self, host):
        scheme = 'ldaps' if self.conf['LDAP_USE_LDAPS'] else 'ldap'
        port = self.conf.get('LDAP_PORT', 636 if self.conf['LDAP_USE_LDAPS'] else 389)

        if self.conf['LDAP_USE_LDAPS'] or self.conf['LDAP_USE_STARTTLS']:
            ldap.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            ldap.set_option( ldap.OPT_X_TLS_DEMAND, True )

        if self.conf.get('LDAP_CA_CERTIFICATE', None) is not None:
            certfile = tempfile.NamedTemporaryFile('w')
            certfile.write(self.conf['LDAP_CA_CERTIFICATE'])
            certfile.flush()
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, certfile.name)

        conn = ldap.initialize('%s://%s:%s' % (scheme, host, port), bytes_mode=False)

        if self.conf.get('LDAP_BIND_DN', None) is not None:
            conn.simple_bind_s(self.conf['LDAP_BIND_DN'], self.conf['LDAP_BIND_PASSWORD'])

        return conn

    def get_state(self, hostlist):
        res = []
        try:
            for host in hostlist:
                conn = self.get_conn(host)
                res = res + self.get_hostreplication_state(host, conn)
        except Exception as e:
            print("error for host %s : %s" % (host, str(e)))

        return autorep.ReplicationList(res)

    def add_replication(self, repl, replcount):
        print("will add replication from %s to %s" % ( repl.source, repl.target ) )
        source = self.get_conn(repl.source)

        dn = 'cn="meTo%s",cn=replica,cn="%s",cn=mapping tree,cn=config' % (repl.target, self.conf['LDAP_REPLICATED_BASE_DN'])
        repldef = {}
        repldef['objectClass'] = [b'top', b'nsds5ReplicationAgreement']
        repldef['cn'] = ('meTo' + repl.target).encode('utf-8')
        repldef['nsds5replicahost'] = repl.target.encode('utf-8')
        repldef['nsds5ReplicaBindDN'] = self.conf['LDAP_REPLICATION_DN'].encode('utf-8')
        repldef['nsds5replicaport'] = '389'.encode('utf-8')
        repldef['nsds5replicabindmethod'] = 'SIMPLE'.encode('utf-8')
        repldef['nsds5replicacredentials'] = self.conf['LDAP_REPLICATION_PASSWORD'].encode('utf-8')
        repldef['nsds5replicaroot'] = self.conf['LDAP_REPLICATED_BASE_DN'].encode('utf-8')
        repldef['description'] = ("agreement between %s and %s" % (repl.source, repl.target)).encode('utf-8')

        if ( replcount[repl.source] == 0 and replcount[repl.target] == 0 ) or replcount[repl.target] == 0:
            repldef['nsds5BeginReplicaRefresh'] = 'start'.encode('utf-8')
        replcount[repl.source] = replcount[repl.source] + 1
        replcount[repl.target] = replcount[repl.target] + 1

        ldif = modlist.addModlist(repldef)
        source.add_s(dn, ldif)
        source.unbind_s()

        print("added replication from %s to %s" % ( repl.source, repl.target ) )

    def del_replication(self, repl):
        print("will remove replication from %s to %s" % ( repl.source, repl.target ) )
        source = self.get_conn(repl.source)

        dn = 'cn="meTo%s",cn=replica,cn="%s",cn=mapping tree,cn=config' % (repl.target, self.conf['LDAP_REPLICATED_BASE_DN'])
        ldif = source.delete_s(dn)
        source.unbind_s()

    def apply_changes(self, hostlist, current, changes):
        replcount = dict()
        for host in hostlist:
            replcount[host] = 0

        for repl in current:
            if repl.target in replcount:
                replcount[repl.target] = replcount[repl.target] + 1
            if repl.source in replcount:
                replcount[repl.source] = replcount[repl.source] + 1

        for change in changes:
            if change.mode == autorep.ReplicationMode.OneWay:
                self.add_replication(change, replcount)
            if change.mode == autorep.ReplicationMode.Remove:
                self.del_replication(change)

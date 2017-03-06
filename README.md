AutoRep Service
===============

This python module is a framework to manage replication of services that are not able to do auto-discovery and cannot be configured install-time using files.

This framework is split into 4 parts that together bring the ability to manage the replication.

The frequency of the update of the configuration is controlled using environment variable *AUTOREP_UPDATE_PERIOD* which is the number of seconds between replication configuration update.

## Source

The Metadata source, allows the discovery of all nodes that should be member of the replicating cluster.

The module is selected using environment variable *AUTOREP_SOURCE_DRIVER_MODULE*

Currently supports the following modules.

### rancher

Query the rancher-metadata service to get the list. Configuration is done using the environment variables:

- RANCHER_METADATA_APIVERSION: the version of the rancher api to query, tested with *2016-07-29*
- RANCHER_AUTOREP_TARGET_SERVICE_NAME: the name of the rancher service to track, format *stack name*/*service name*
- RANCHER_REFERENCE_CONAINTER_MODE: how to reference the container, can be *containerip* for the private IP, or *containername* for the container name


## Target

The service needing control for replication.

The module is selected using environment variable : *AUTOREP_TARGET_DRIVER_MODULE*

Currently supports the following modules.

### 389ds

Configuration is done using the environment variables:


- *LDAP_PORT*: The port to use for connection, defaults to the proper port (636 for ldaps and 389 for ldap).
- *LDAP_USE_LDAPS*: Set to "true" to use ldaps protocol
- *LDAP_USE_STARTTLS*: Set to "true" to use starttls over ldap connection
- *LDAP_CA_CERTIFICATE*: The CA to use to validate the server Certificate
- *LDAP_BIND_DN*: The DN the script will use to connect to the LDAP server
- *LDAP_BIND_PASSWORD*: The Password the script will use to connect to the LDAP server
- *LDAP_REPLICATED_BASE_DN*: The baseDN that will be replicated
- *LDAP_REPLICATION_DN*: The username to use for replication auth
- *LDAP_REPLICATION_PASSWORD*: The password to use for replication auth

## Replication Graph

This controls how the replication topology is setup.

The module is selected using the environment variable *AUTOREP_REPLICATION_GRAPH_DRIVER_MODULE*.

Currently supports the following modules.

### fullmesh

Will make all nodes master and make all nodes replicate on all other nodes.

## Clustering

This allows autorep to be put in cluster itself.

The module is selected using the environment variable *AUTOREP_CLUSTERING_DRIVER_MODULE*.

Currently supports the following modules.

### standalone

Instances of autorep using this module will behave without consulting any other instance, thus will apply the changes it deems fit without qualms.

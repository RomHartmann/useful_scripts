Solr Cloud on Container Engine
==============================

This is the configuration for the Solr Cloud Cluster, which is running on Google Container Engine

This Solr deployment assumes that there is a zookeeper cluster setup with three nodes. These 
nodes must have exposed services on ports 2181, 2888 and 3888.

Lastly, in order for Solr to start correctly, the container must be started with an environment
variable called `KUBERNETES` that contains any value (the startup script checks for the 
existance of the varibale, not its value)

## Security

The endpoint is exposed via a NGinX proxy. Basic security has been setup.

## Example Config Upload

Configs can be uploaded to Zookeeper using the Solr zkCli.sh

Example command:

```
./zkcli.sh -z localhost:2181 -cmd upconfig -confdir ~/Development/alice/alice-solr /solr/solr-collection-configs/connectors/conf -confname connectors
```

## Folder Structure

Each of the folders in the directory `solr-collection-configs` contains the configuration for a single Solr collection. Importantly,
each folder contains a sub-folder called *conf* that is the actual folder that will be uploaded to Zookeeper
using the zkcli.sh script, as provided in the Solr distribution.

## Managed Schema

The Solr collections have been, and must continue to be, configured using the *managed schema* feature of the
SolrCloud stack. As a net result, it is vital that any give user first **PULL** the config from the Zookeeper
instance using the *downconfig* command of the *zkcli.sh* scipt before finally uploading using the *upconfig* 
command.

The basic pattern is this:

1. Download SolrConfig using the *downconfig* command
2. Perform changes to the various files (**EXCLUDING** the managed-schema file)
3. Upload changes using the *upconfig* commmand
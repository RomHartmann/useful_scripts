#!/bin/bash

echo "Waiting 30s for zookeeper to come online!"
sleep 30

if [ ! -z "$KUBERNETES" ]; then
    echo "starting in kubernetes mode with external zookeper cluster."
    echo "Solr Mem set to $SOLR_MEM"
    echo "hostname set to $POD_NAME.$SERVICE_NAME"
    echo "Solr Data Dir set to $DATA_MOUNT_PATH"
    echo
    echo "Setting up environment and copying solrconfig to datadir"
    # Copies the solr.xml file from the default location to the mounted volume
    # Sets the correct file permissions
    sudo cp /opt/solr/server/solr/solr.xml $DATA_MOUNT_PATH
    sudo chown -R solr:solr /data
    echo
    echo "Starting solr...."
    echo "Solr Command: /opt/solr/bin/solr start -f -c -z $ZOOKEEPER_CLUSTER -s $DATA_MOUNT_PATH -m $SOLR_MEM -h $POD_NAME.$SERVICE_NAME"
    exec /opt/solr/bin/solr start -f -c -z $ZOOKEEPER_CLUSTER -s $DATA_MOUNT_PATH -m $SOLR_MEM -h $POD_NAME.$SERVICE_NAME
else
    echo "starting in localmode"
    exec /opt/solr/bin/solr start -f -c
fi
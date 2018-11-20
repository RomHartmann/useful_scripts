Kubernetes Solr Implementation
==============================

This is an implementation of Solr on Kubernetes, managed with Zookeeper.

# Step by step on how to set up Solr

### 1)  Build docker images and upload

```
# login to AWS
$(aws ecr get-login --no-include-email)

# Create repo if it does not exist yet.
aws ecr create-repository --repository-name solr
aws ecr create-repository --repository-name zookeeper
```

```
# cd into solr
export SOLR_DIR=$(pwd)

docker build -t solr:7.2 .
docker tag solr:7.2 00112233.dkr.ecr.us-east-1.amazonaws.com/solr:7.2
docker push 00112233.dkr.ecr.us-east-1.amazonaws.com/solr:7.2

# cd into zookeeper
docker build -t zookeeper:3.4.11 .
docker tag zookeeper:3.4.11 00112233.dkr.ecr.us-east-1.amazonaws.com/zookeeper:3.4.11
docker push 00112233.dkr.ecr.us-east-1.amazonaws.com/zookeeper:3.4.11
```


### 2) Create Zookeeper Stateful sets

```
kubectl create -f zookeeper/zookeeper-statefulset.yaml
```

Wait for 2 minutes (until logs have calmed down)


### 3)  Upload collection configs

a)  Download solr from http://archive.apache.org/dist/lucene/solr/7.2.1/

b)  Port-forward onto zookeeper
```
kubectl port-forward zk-0 2181:2181
```

c)  from inside of `solr-7.2.1`

Make sure that `$SOLR_DIR` from step(1) ends with `solr/solr/`

```
cd solr-7.2.1/server/scripts/cloud-scripts

# name of our collection
COLLECTION_NAME="general"

# local path of solr configs.
COLLECTION_CONFIGS="$SOLR_DIR/solr-collection-configs/collection_set/conf"
# check `ls $COLLECTION_CONFIGS`

# upload our configs
./zkcli.sh -z localhost:2181 -cmd upconfig -confdir $COLLECTION_CONFIGS -confname $COLLECTION_NAME
```

If this fails with `org/apache/solr/cloud/ZkCLI : Unsupported major.minor version 52.0`,
then you need to update or install java:  
`brew install Caskroom/cask/java`  

### Create Solr statefulset

```
kubectl create -f solr/solr-statefulset.yaml
```

d)  Port-forward into solr

```
kubectl port-forward solr-0 8983:8983
```

e)  Set up collection

i)  Create new collection
ii)  Select collection set
iii)  Give it the same name
iv)  Select 3 shards, 1 replication


### Set up basic auth ingress

`cd /infrastructure/basic_auth_ingress`
Follow `README.md`








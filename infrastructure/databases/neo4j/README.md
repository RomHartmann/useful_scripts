neo4j database stateful set
---------------------------

https://hub.docker.com/_/neo4j/

## How to use this image

### Start an instance of neo4j
You can start a Neo4j container like this:

```
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    neo4j
```

which allows you to access neo4j through your browser at http://localhost:7474.

This binds two ports (7474 and 7687) for HTTP and Bolt access to the Neo4j API. 
A volume is bound to /data to allow the database to be persisted outside the container.

By default, this requires you to login with neo4j/neo4j and change the password. 
You can, for development purposes, disable authentication by passing `--env=NEO4J_AUTH=none` to docker run.

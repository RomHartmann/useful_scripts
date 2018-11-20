Elasticsearch Docker deployment
-------------------------------

### Elasticsearch cluster
https://github.com/kubernetes/examples/tree/master/staging/elasticsearch/production_cluster

```
kubectl create -f k8-es/service-account.yaml
kubectl create -f k8-es/es-discovery-svc.yaml
kubectl create -f k8-es/es-svc.yaml
kubectl create -f k8-es/es-master-rc.yaml

kubectl create -f k8-es/rbac.yaml

# Wait until es-master is provisioned
kubectl create -f k8-es/es-client-rc.yaml

# Wait until es-client is provisioned
kubectl create -f k8-es/es-data-rc.yaml
```

Now we have the elasticsearch cluster running.

### Kibana

Next we install kibana into that cluster in order to have a UI available.

```
kubectl create -f kibana/kibana-svc.yaml
```


## Destroy all

```
kubectl delete -f k8-es/service-account.yaml
kubectl delete -f k8-es/es-discovery-svc.yaml
kubectl delete -f k8-es/es-svc.yaml
kubectl delete -f k8-es/es-master-rc.yaml
kubectl delete -f k8-es/rbac.yaml
kubectl delete -f k8-es/es-client-rc.yaml
kubectl delete -f k8-es/es-data-rc.yaml
kubectl delete -f kibana/kibana-svc.yaml
```


Don't work.  Maybe this:
```
Readiness probe failed: dial tcp 100.116.0.5:9300: getsockopt: connection refused
Back-off restarting failed container


```
elk:
https://github.com/kayrus/elk-kubernetes

other:
http://arveknudsen.com/?p=425

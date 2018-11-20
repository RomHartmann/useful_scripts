Nginx-Ingress
-------------

### 1)  Create htpasswd and add as secret

```
# install htpasswd if necessary
sudo apt-get install apache2-utils

htpasswd -c secrets/auth pass

kubectl create secret generic basic-auth --from-file=secrets/auth
```

### 2)  Role Based Access Controller

```
kubectl create namespace nginx-ingress
```

```
kubectl apply -f rbac.yaml
```

### 3) Add Nginx Controller

```
kubectl apply -f nginx-controller.yaml
```

In route53, add link record to external services:

```
monitoring route
Everything else route
```

### 4) Add Ingress

Given hostmane created in route53 above, 

```
kubectl apply -f ingress.yaml
```



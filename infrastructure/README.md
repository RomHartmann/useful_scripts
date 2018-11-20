Kubernetes Infrastructure
-------------------------

How to deploy and work with the infrastructure elements.

## Deploy Kubernetes to AWS

Look for instructions within `/AWS/README.md`

## Kubernetes with GCP

Simply go into the console and create a cluster with Kubernetes Engine.


## Deploy container to Kubernetes

### A)  Create the docker image

The docker image needs to be built on the local machine first.
Use the tag sytem `-t` to name the image.
Then point the command at where the `Dockerfile` is situated.  Easiest is to `cd`
to the path containing the Dockerfile and then just use `.`.

```
docker build -t {imageTag} .
```

#### GCP:
Path to the container registry.  eg: `us.gcr.io/project/image-name:version`

```
docker build -t us.gcr.io/project/image-name:version .
```

#### AWS:
Just give it a name and version, though th

```docker build -t image-name:0.1 .```

Then tag it with the Container registry path:

```
docker tag {image_name} {ECR path}
```

ECR path: `{aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/{ECR name}`

eg. `app-id.dkr.ecr.us-east-1.amazonaws.com/project`

```
docker tag image-name app-id.dkr.ecr.us-east-1.amazonaws.com/project
```

### b)  Push the docker image to a container registry.
Before images can be deployed to Kubernetes, they need to first exist in a container registry.
This allows Kubernetes to pull the image onto a node without needing access to your local computer.

#### GCP:

a)  Get credentials first:
`gcloud container clusters get-credentials {cluster-name} --zone us-west1-d --project {project_name}`

b)  Then push image:
`gcloud docker -- push {imageTag}`

#### AWS:
https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html

**IMPORTANT**:  The repo with the image name must be created _before_ the image is created

I.e. if you want an image for a task (eg `this_does_something`), then the repo must be created first.

a)  Get login details for AWS ECR if you havn't already.  Run command to docker login for your registry.
`$(aws ecr get-login --no-include-email)`

b) Create repo

```
aws ecr create-repository --repository-name {imageTag}
```

c)  Push Image to ECR:

`docker push {aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/{ECR name}`


### c)  Push K8 configuration yaml

Kubernetes is declarative:  This means that you tell it how you want something to look like
and then K8 will try its best to make your wishes come true.

The configuration comes in the form of a yaml file, and it needs to follow this order:

- Resources
- Deployments
- Containers

This means, if you use any shared disks or network resources, they need to be defined first.
Thus, even though a service sits on top of a deployment, the service needs to be defined first
because it is a network resource, and the deployment (and thus pods) are _used_ by the service.

An example my_service.yaml (indendtaion is important):

```
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: default
  labels:
    app: my-app
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 2345
    protocol: TCP
  selector:
    app: my-app
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: my-app
  namespace: default
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: app-id.dkr.ecr.us-east-1.amazonaws.com/project
        # image: us.gcr.io/project/my-app:latest   # for GCP
        env:
        - name: MY_PASSWORD
          valueFrom:
            secretKeyRef:
              name: my-special-key
              key: my-special-key
        ports:
        - containerPort: 2345
        resources:
         requests:
          memory: "1000Mi"
```


## Useful Kubernetes things

#### Secrets

We don't like keeping any secrets in code, so we deploy them to kubernetes secrets.  Eg:

```kubectl create secret generic my-special-key --from-file=secrets/my-special-key```

This creates a secret called `my-special-key` from a file in the relative folder `secrets`.
Make sure to remember to add `secrets` folder to the `.gitignore` file.

This key is then stored within Kubernetes, and we can set an environment MY_PASSWORD
variable to that secret in the yaml file like this:

```
        env:
        - name: MY_PASSWORD
          valueFrom:
            secretKeyRef:
              name: my-special-key
              key: my-special-key
```

This looks at the key called `my-special-key` for the `my-special-key` variable.
The variable has this name because that is what the file was called in the `secrets` folder.

#### Create/Delete Deployment

```
kubectl create -f my_service.yaml
kubectl delete -f my_service.yaml
```

#### Port forwarding

You can port forward a running **pod** from kubernetes to your local machine:

```
kubectl port-forward redis-0 6379:6379
```


#### SSH into a **pod**

```
kubectl exec -it <pod name> bash
```

- `-it` for `interactive` and `tag name`.
- <pod name> the name of a pod. Could be one of the pods in a deployment.
- `bash` what to execute


#### Prometheus

Install Prometheus
------------------

Will allow us to do better monitoring of our cluster.

## Install

https://github.com/camilb/prometheus-kubernetes

```
curl -L https://git.io/getPrometheusKubernetes | sh -

cd prometheus-kubernetes
./deploy
```

Then we can port forward into them
```
./prometheus/tools/grafana_proxy.sh
./prometheus/tools/prometheus_proxy.sh
```

Or set up some ingress or proxies for them within our infrastructure

## Ingress

`cd prometheus/tools/ingress`

```
# install htpasswd
sudo apt-get install apache2-utils

./init.sh
```

Domain:  `domain.io`
username: `appteam`
password: `xxx`



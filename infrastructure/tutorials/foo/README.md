Docker + kubernetes setup for an example Python Flask app
_________________________________________________________

## Flask

Set up the flask app to run on localhost on a given port


## Docker

Create the Dockerfile.  Expose the port you set in Flask.
Remember that a Dockerfile builds sequentially, thus we install from requirements.txt
before copying the code, else we would have to reinstall every time we change our code.

Then build the docker image:

```
docker build -t foo .

docker run -e SECRET_ENV="loc_sec" -e CONFIG_MAP="loc_cm" -p 5000:5000 foo
```


## Kubernetes

run `kubectl proxy` and go to
http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/#!/overview?namespace=default
to view the dashboard.

### AWS

First, lets create the Secret and ConfigMap that our environment variables need

**NOTE:** Add the secrets folder into the `.gitignore` file!!! (I commented it out for illustration purposes)

```
# Secret:
kubectl create secret generic secret-name --from-file=secrets/my-secret

# ConfigMap
kubectl create configmap cm-name --from-file=config_maps/my-configmap.conf
```

You can now navigate to Secrets and ConfigMaps in the K8 dashboard to look at them.

```
# login to AWS
$(aws ecr get-login --no-include-email)

# Create repo if it does not exist yet.
aws ecr create-repository --repository-name foo

# Tag the image with an AWS account specific name so that we can pull it later.
docker tag foo 00112233.dkr.ecr.us-east-1.amazonaws.com/foo
docker push 00112233.dkr.ecr.us-east-1.amazonaws.com/foo
```

Now we want to create a service out of this application so that other services within
Kubernetes can talk to it.

We create a yaml file and define everything from there.

```
kubectl create -f foo_service.yaml
```

If you go to the dashboard you'll be able to see the service and deployment there.
To delete it again, run `kubectl delete -f foo_service.yaml`.  If you delete the pod from the
dashboard then Kubernetes will just recreate it, because that is its job.


Now that the deployment and service is up, we can work with it.  We can only interact with pods
form our local machine, so lets get the pod name (does not matter which one)

```
POD_NAME=$(kubectl get pods | grep fooapp | cut -f1 -d' ' | head -1)
```

a)  `exec` into it.  This allows us to ssh directly into the machine.
```
kubectl exec -it $POD_NAME bash
```

b)  `port forward into the pod`
```
kubectl port-forward $POD_NAME 5000:5000
```

Once you've port forwared, you can run `localhost:5000` on your local machine again, and
then the page will be hosted from inside of Kubernetes!! You can even go into the
Deployment -> Pods -> logs to check out our logging of the secret and config map.


## Where we are so far

We have now packaged our app as a docker image and deployed it into Kubernetes, and can run access
the service on our local machine via localhost by port forwarding.

When we port forward into our pod the Deployment load balances our app between its
pods.

We can, however, not yet access this API from the outside world.  For that we need to
change our Service to be of type LoadBalancer (that is, a network loadbalancer instead of the
application load balancer that we already have from the Deployment).  We can, however,
connect to our app from any other pod that is already in the Kubernetes cluster via localhost.



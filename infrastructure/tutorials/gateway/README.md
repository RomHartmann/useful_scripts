Gateway Service
_______________

For proper documentation for how to deploy this service, go look at tutorials/foo.

This service just goes and fetches whatever foo returns on / and returns that and a bit more.

```
docker build -t gateway .

# login to AWS
$(aws ecr get-login --no-include-email)

# Create repo if it does not exist yet.
aws ecr create-repository --repository-name gateway

# Tag the image with an AWS account specific name so that we can pull it later.
docker tag gateway appid.dkr.ecr.us-east-1.amazonaws.com/gateway
docker push appid.dkr.ecr.us-east-1.amazonaws.com/gateway

# kubectl delete -f gateway-service.yaml
kubectl create -f gateway-service.yaml

POD_NAME=$(kubectl get pods | grep gateway | cut -f1 -d' ' | head -1)
kubectl port-forward $POD_NAME 5000:5000

```


#### Create DNS address via Route53

Where we want the public to hit:  `http://tutorial.xyz.io/`.  
Service in K8 that should hit:  `gateway-service/`  

So, first we will register the tutorial subdomain:

Go to the UI, into the relevant domain and then create a new record set.

1)  Set the subdomain name  
2)  "Yes" Alias  
3)  Alias must be the the external IP created by the Service.


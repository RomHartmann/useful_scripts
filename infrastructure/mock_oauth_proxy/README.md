Mock oAuth service
------------------

This is just a layer over http://oauthbin.com/ so that we can deploy it
in our infrastructure and serve over https.  All we do is pass everything
accross exactly and return the result.

## Install instructions:

```
docker build -t oauth_proxy .

# login to AWS
$(aws ecr get-login --no-include-email)

# Create repo if it does not exist yet.
aws ecr create-repository --repository-name oauth_proxy

# Tag the image with an AWS account specific name so that we can pull it later.
docker tag oauth_proxy 00112233.dkr.ecr.us-east-1.amazonaws.com/oauth_proxy
docker push 00112233.dkr.ecr.us-east-1.amazonaws.com/oauth_proxy

kubectl create -f oauth_service.yaml
```

To update code:

```
docker build -t oauth_proxy .
docker tag oauth_proxy 00112233.dkr.ecr.us-east-1.amazonaws.com/oauth_proxy
docker push 00112233.dkr.ecr.us-east-1.amazonaws.com/oauth_proxy

kubectl delete deployment oauth-proxy
kubectl create -f oauth_service.yaml
```

### Create DNS address via Route53

Where we want the public to hit:  `http://oauth_proxy.myassistant.ai/` (because that is the certificate we used).  
Service in K8 that should hit:  `oauth-proxy-service`  

So, first we will register the `oauth-proxy` subdomain:

Go to the UI, into the relevant domain and then create a new record set.

1)  Set the subdomain name  
2)  "Yes" Alias  
3)  Alias must be the the external IP created by the Service:   
```
kubectl describe service oauth-proxy-service | grep "LoadBalancer Ingress" | awk '{print $3}'
```

It takes about 5 minutes for AWS to get the load balancers up and running.

Name the record set `oauth_proxy`, and then after another 10 minutes you should be able to hit these successfully:

```
http://oauth_proxy.myassistant.ai/
https://oauth_proxy.myassistant.ai/
```

#### And then we can run it locally with 

```
docker run -p 8080:8080 oauth_proxy
```

## Instructions for Use (copy-pasted from http://oauthbin.com/)
This is a test server with a predefined static set of keys and tokens, you can make your requests using them to test your code.

Your Consumer Key / Secret
consumer key: key
consumer secret: secret
Use this key and secret for all your requests.

Getting a Request Token
request token endpoint: http://oauthbin.com/v1/request-token
A successful request will return the following:

oauth_token=requestkey&oauth_token_secret=requestsecret

An unsuccessful request will attempt to describe what went wrong.

Example
http://oauthbin.com/v1/request-token?oauth_consumer_key=key&oauth_nonce=ddea2516611d0433cf5dbfe979987628&oauth_signature=163O%2BmwOE2JSV%2Fbl1oW5%2FKuPv1g%3D&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1520623987&oauth_version=1.0
Getting an Access Token
The Request Token provided above is already authorized, you may use it to request an Access Token right away.

access token endpoint: http://oauthbin.com/v1/access-token
A successful request will return the following:

oauth_token=accesskey&oauth_token_secret=accesssecret

An unsuccessful request will attempt to describe what went wrong.

Example
http://oauthbin.com/v1/access-token?oauth_consumer_key=key&oauth_nonce=6637639550fd55be5fb9ddc46eb0c300&oauth_signature=XkiGWY7Xgwgcmp4iHb08P2U%2F%2FcY%3D&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1520623987&oauth_token=requestkey&oauth_version=1.0
Making Authenticated Calls
Using your Access Token you can make authenticated calls.

api endpoint: http://oauthbin.com/v1/echo
A successful request will echo the non-OAuth parameters sent to it, for example:

method=foo&bar=baz

An unsuccessful request will attempt to describe what went wrong.

Example
http://oauthbin.com/v1/echo?bar=baz&method=foo%2520bar&oauth_consumer_key=key&oauth_nonce=8af8e6177556dd7ac5be2d09e484f180&oauth_signature=lhGEOJzNeYjIAPCw4PHWCRDryqc%3D&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1520623987&oauth_token=accesskey&oauth_version=1.0



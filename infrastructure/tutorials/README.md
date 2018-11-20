Complete Infrastructure Tutorial
________________________________

This is partly a reference sheet, and partly a tutorial on how to deploy any
component of our infrastructure onto Kubernetes.

1)  Python Flask app microservice (foo)
2)  Flask API Gateway calling foo (gateway)
3)  Nginx reverse proxy controller (ingress)

## 1)  Python Flask app microservice - foo

Check /foo/README.md for detailed instructions on how to set up a Python
microservice in Flask, how to dockerize it and then deploy it onto Kubernetes.

## 2)  Flask API Gateway calling foo - gateway

The deployment instructions are the same as for the foo microservice.
However, this service is set up differently from foo because it does a
GET request against foo and returns what it got from fooapp-service:80/

## 3)  Nginx reverse proxy controller - ingress
Both foo and the gateway sit completely within the K8s environment and cannot
be reached by a public call.
So we set up an Nginx reverse proxy controller which is outwards facing
and passes calls from the public DNS address to the service which has to handle it.









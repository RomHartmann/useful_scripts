AWS Kubernetes Deployment
-------------------------

Steps required to set up K8s on AWS.  From  
- https://kumorilabs.com/blog/k8s-1-deploy-kubernetes-cluster-aws-kops/
- https://kumorilabs.com/blog/k8s-2-maintaining-your-kubernetes-cluster/
- https://github.com/kubernetes/kops/blob/master/docs/aws.md

## 1)  Install prerequisites
#### a)  install `kubectl`  
https://kubernetes.io/docs/tasks/tools/install-kubectl/

mac:  
`brew install kubectl`

linux:
```
apt-get update && apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF
apt-get update
apt-get install -y kubectl
```
  

#### b)  install `kops`
https://github.com/kubernetes/kops/blob/master/docs/install.md

mac:  
`brew install kops`

linux:
```
wget -O kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x ./kops
sudo mv ./kops /usr/local/bin/
```

#### c) install awscli

`pip install awscli`  

Make sure you are in the correct region

`aws configure`

Generally N. Virginia is the best region for us:  `us-east-1`

## 2)  Set up kops permission group and user

```
aws configure

aws iam create-group --group-name kops

aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonRoute53FullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/IAMFullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonVPCFullAccess --group-name kops

aws iam create-user --user-name kops
aws iam add-user-to-group --user-name kops --group-name kops
aws iam create-access-key --user-name kops

# Because "aws configure" doesn't export these vars for kops to use, we export them now
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
```


## 3)  Configure DNS

If domains are already registered with AWS, then nothing needs to be done.

`example.com` would look like `etcd-us-east-1c.internal.clustername.example.com`

else: https://github.com/kubernetes/kops/blob/master/docs/aws.md#configure-dns

## 4)  Create Cluster

#### a)  Set up environment variables for simplicity

```
# Domain name that is hosted in AWS Route 53
export DOMAIN_NAME="domain.io"

# Friendly name to use as an alias for your cluster
export CLUSTER_ALIAS="kubernetes-cluster"

# Full DNS name of you cluster
export CLUSTER_FULL_NAME="${CLUSTER_ALIAS}.${DOMAIN_NAME}"

# AWS availability zone where the cluster will be created
export CLUSTER_REGION="us-east-1"
export CLUSTER_AWS_AZ="us-east-1a"

# S3 state storage for k8 cluster
export STATE_NAME=${CLUSTER_FULL_NAME}-state
export KOPS_STATE_STORE="s3://${STATE_NAME}"

# Go to AWS VPC and get the VPC id.
export VPC="vpc-123"
```

#### b)  Create S3 Store

Create bucket:
```
aws s3api create-bucket --bucket ${STATE_NAME} --region ${CLUSTER_REGION}

# enable versioning
aws s3api put-bucket-versioning --bucket ${STATE_NAME}  --versioning-configuration Status=Enabled
```


#### c)  Create cluster

```
# aws ec2 describe-availability-zones --region ${CLUSTER_REGION}

kops create cluster \
    --name=${CLUSTER_FULL_NAME} \
    --state=${KOPS_STATE_STORE} \
    --zones=${CLUSTER_AWS_AZ} \
    --kubernetes-version 1.10.0 \
    --master-size="t2.xlarge" \
    --node-size="t2.xlarge" \
    --node-count="5" \
    --dns-zone=${DOMAIN_NAME} \
    --ssh-public-key="~/.ssh/id_rsa.pub" \
    --topology=private \
    --networking=weave \
    --associate-public-ip=false \
    --cloud=aws \
    --vpc $VPC
```

#### d) Configure Cluster

If we need to edit some configuration (for example update version)
```
# export EDITOR=nano
# kops edit cluster ${CLUSTER_FULL_NAME}
```

Edit subnets if there is a conflict:  
https://github.com/kubernetes/kops/issues/2294

```
kops get clusters ${CLUSTER_FULL_NAME} --state ${KOPS_STATE_STORE} -o yaml > cluster-config.yaml

# replace conflicting IP ranges.  Eg:

#  subnets:
#  - cidr: 172.31.32.0/19
#  ...
#  - cidr: 172.31.0.0/22

#  subnets:
#  - cidr: 172.31.224.0/19
#  ...
#  - cidr: 172.31.128.0/22

kops replace -f cluster-config.yaml --state ${KOPS_STATE_STORE}
export NEW_FULL_NAME="${CLUSTER_ALIAS}.${DOMAIN_NAME}"
kops update cluster --state ${KOPS_STATE_STORE} --name ${CLUSTER_FULL_NAME} --yes
```

#### e)  Build Cluster

This builds the actual cluster
```
kops update cluster ${CLUSTER_FULL_NAME} --yes
```

To check if it is online:
```
kops validate cluster
```

#### f)  Create context for kubeconfig file

```
export CLUSTER_ALIAS=kubernetes-cluster

kops export kubecfg --name ${CLUSTER_FULL_NAME} \
  --state=${KOPS_STATE_STORE}

kubectl config use-context ${CLUSTER_ALIAS}

```

#### g)  Deploy Kubernetes dashboard

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/alternative/kubernetes-dashboard.yaml
```

Run the dashboard:
```kubectl proxy```
And go to

http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy


## 5)  Use Cluster

Once the cluster is up, then we can start using the cluster.

### Connect to it if you did not create it:

```
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
export CLUSTER_ALIAS=kubernetes-cluster

kubectl config set-context ${CLUSTER_ALIAS} \
    --cluster=${CLUSTER_FULL_NAME} \
    --user=${CLUSTER_FULL_NAME}

kubectl config use-context ${CLUSTER_ALIAS}

kops export kubecfg --name ${CLUSTER_FULL_NAME} \
  --state=${KOPS_STATE_STORE}
```

The old one (for kops 1.8.1), the export config command:
```
kops export cluster --name ${CLUSTER_FULL_NAME} \
  --region=${CLUSTER_REGION} \
  --state=${KOPS_STATE_STORE}
```

`kubectl` is the "Kubernetes Control" package.  Using `kubectl get nodes` will show us our master and 3 worker nodes we created.


## Deleting cluster

If we are not using it then it should be shut down to minimize costs:

```
kops delete cluster --name ${CLUSTER_FULL_NAME}  --yes
```




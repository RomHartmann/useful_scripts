# Databricks restful api

## Create access token

https://docs.databricks.com/api/latest/authentication.html

Add the `DBR_USER` and `DBR_PASS` envs.

```
export DBR_USER=token
export DBR_PASS=<access token>
export DBR_DOMAIN=https://dbc-1234-0d74.cloud.databricks.com
```

## Api calls

https://docs.databricks.com/api/latest/index.html

### list clusters

```
curl -u $DBR_USER:$DBR_PASS GET $DBR_DOMAIN/api/2.0/clusters/list
```

or, in python:

```requests.get(url, auth=(DBR_USER, DBR_PASS))```

### start job

POST this object to `https://dbc-1234-0d74.cloud.databricks.com/api/2.0/jobs/runs/submit`

```

```
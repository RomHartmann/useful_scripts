"""Functions for working with google dataproc.

Installs:
    pip install google-api-python-client
"""
import logging

import googleapiclient.discovery

DATAPROC = googleapiclient.discovery.build('dataproc', 'v1')

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)


def create_cluster(project_id, cluster_name, zone):
    uri = 'https://www.googleapis.com/compute/v1/projects/{}/zones/{}'.format(
        project_id, zone
    )
    cluster_data = {
        'projectId': project_id,
        'clusterName': cluster_name,
        'config': {
            'gceClusterConfig': {
                'zoneUri': uri
            }
        }
    }

    result = DATAPROC.projects().regions().clusters().create(
        projectId=DATAPROC,
        region=DATAPROC,
        body=cluster_data).execute()

    return result



def delete_cluster():
    pass


def start_cluster():
    pass


def stop_cluster():
    pass


def submit_pyspark_job():
    pass


def monitor_job():
    pass


if __name__ == '__main__':
    PROJECT_ID = 'scoop-24-dev'
    ZONE = 'europe-west1-d'
    CLUSTER_NAME = 'test-cluster'

    result = create_cluster(PROJECT_ID, CLUSTER_NAME, ZONE)

    logger.info(result)







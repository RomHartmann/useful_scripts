"""Create image instance, start and stop instance, start zap."""
import logging
import os
import time

import googleapiclient.discovery

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

COMPUTE = googleapiclient.discovery.build('compute', 'v1')
PROJECT_ID = "bidvest-alice"
ZONE = "europe-west1-d"
MACHINE_TYPE = "n1-standard-4"
SOURCE_IMAGE = "owasp-zap-image"

STARTUP_PATH = os.path.join(os.path.dirname(__file__), "compute_startup.sh")


def create_instance(name):
    """Create a compute instance from an existing disk image.

    :param name: Name of the new compute instance
    :type name: str
    :return: All metadata related to the created image
    :rtype: dict
    """
    logger.info("Creating Google Cloud Compute instance.".format(name))

    logger.debug("getting base image...")
    image_response = COMPUTE.images().get(
        project=PROJECT_ID,
        image=SOURCE_IMAGE
    ).execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/{}/machineTypes/{}".format(ZONE, MACHINE_TYPE)

    startup_script = open(STARTUP_PATH, 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow access to all cloud APIs
        'serviceAccounts': [{
            'email': 'default',
            'scopes': ["https://www.googleapis.com/auth/cloud-platform"]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed upon startup.
                'key': 'startup-script',
                'value': startup_script
            }]
        }
    }

    logger.debug("creating instance...")
    return COMPUTE.instances().insert(
        project=PROJECT_ID,
        zone=ZONE,
        body=config
    ).execute()


def delete_instance(name):
    """Delete cloud instance.

    :param name: Name of instance we are deleting.
    :type name: str
    :return: Metadata for deleted instance.
    :rtype: dict
    """
    logger.info("deleting Google Cloud Compute instance {}".format(name))
    return COMPUTE.instances().delete(
        project=PROJECT_ID,
        zone=ZONE,
        instance=name
    ).execute()


def start_instance(name):
    """Start a stopped instance.

    :param name: Name of instance we are starting.
    :type name: str
    :return: Metadata for started instance.
    :rtype: dict
    """
    logger.info("Starting Google Cloud Compute instance {}".format(name))
    return COMPUTE.instances().start(
        project=PROJECT_ID,
        zone=ZONE,
        instance=name
    ).execute()


def stop_instance(name):
    """Stop a running instance.

    :param name: Name of instance we are stopping.
    :type name: str
    :return: Metadata for stopped instance.
    :rtype: dict
    """
    logger.info("stopping Google Cloud Compute instance {}".format(name))
    return COMPUTE.instances().stop(
        project=PROJECT_ID,
        zone=ZONE,
        instance=name
    ).execute()


def wait_for_operation(operation):
    """Wait for the operation to finish.

    :param operation: Operation ID = ret_metadata['name']
      eg. start_instance('name')['name']
    :type operation: 
    :return: Operation result
    :rtype: dict
    """
    logger.info('Waiting for operation to finish...')
    while True:
        result = COMPUTE.zoneOperations().get(
            project=PROJECT_ID,
            zone=ZONE,
            operation=operation
        ).execute()

        if result['status'] == 'DONE':
            logger.info("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(2)


if __name__ == '__main__':
    instance_info = create_instance("test-zapper")

    print(instance_info)

    print(delete_instance("test-zapper"))




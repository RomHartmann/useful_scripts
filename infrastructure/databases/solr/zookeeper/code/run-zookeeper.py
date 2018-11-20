#!/usr/bin/env python3

"""Configure Zookeeper Config Files and Start Zookeeper.

This script VERY specifically sets Zookeeper up to run as a petset in a
Kubernetes cluster. As such, the following assumptions are made:

1 - The name of the node will have the form of name-ordinal where the name is
the name provided in the petset config and the ordinal is an integer increasing
to the size of the defined replica set, starting at 0
2 - The nodes will be discoverable using the format pod_name.service_name

All config options must be provided to the startup script as environment
variables, however, sensible defaults are provided to many of the config
options. Available options, with defaults, are as follows:

bin_dir: defaults to /opt/zookeeper/bin/
conf_dir defaults to /opt/zookeeper/conf/
conf_file_name defaults to zoo.cfg
data_dir defaults to /opt/zookeeper/data
log_dir defaults to /opt/zookeeper/logs'
replica_set defaults to 1
pod_name defaults to localhost
service_name with no default

If the pod_name is not provided as an environment variable OR if the pod_name
does not match the pattern described above, this script will assume that
Zookeeper is running in standalone maode and will configure the system
accordingly, for example, providing 'localhost' as the hostname config to
Zookeeper.
"""
import logging
import os
import re
import subprocess
import time

from jinja2 import Template

# Setup Logging
logging.basicConfig()
logger = logging.getLogger('zookeeper-runner')
logger.setLevel(os.environ.get('log_level', 'INFO'))


def main():
    """Setup Zookeeper Configuration files and start Zookeeper

    Steps:
    1 - Get environment variables
    2 - Make sure locations exists for logs and data
    2 - Setup zoo.cfg file with all members of the replica set
    2 - write id to myid file - note, this is the ordinal number NOT the name
    3 - start Zookeeper
    """

    # Get host_prefix and node ordinal
    pod_name_parts = re.findall(r"(.*)-(\d+)",
                                os.environ.get('pod_name', 'localhost'))

    if not pod_name_parts:
        stateful_set_ordinal = 0
        host_prefix = os.environ.get('pod_name', 'localhost')
    else:
        stateful_set_ordinal = int(pod_name_parts[0][1])
        host_prefix = pod_name_parts[0][0]

    logger.debug('host_prefix: {}'.format(host_prefix))
    logger.debug('stateful_set_ordinal: {}'.format(stateful_set_ordinal))

    # Set Defaults
    logger.info('Getting environment variables....')
    conf_vars = {
        'bin_dir': os.environ.get('bin_dir', '/opt/zookeeper/bin/'),
        'conf_dir': os.environ.get('conf_dir', '/opt/zookeeper/conf/'),
        'conf_file_name': os.environ.get('conf_file_name', 'zoo.cfg'),
        'data_dir': os.environ.get('data_dir', '/opt/zookeeper/data'),
        'log_dir': os.environ.get('log_dir', '/opt/zookeeper/logs'),
        'replica_set': int(os.environ.get('replica_set', 1)),
        'pod_name': os.environ.get('pod_name', 'localhost'),
        'service_name': os.environ.get('service_name'),
        'host_prefix': host_prefix
    }

    # Log out the vars
    for key, value in conf_vars.items():
        logger.debug('{} set to {}'.format(key, value))

    # Check that we need have everything we need to succeed!

    # Scenario should never play out where host_prefix == localhost AND
    # replica_set > 1
    assert (host_prefix != 'localhost') or \
           (host_prefix == 'localhost' and conf_vars['replica_set'] == 1)

    # The node ordinal can't be bigger than the number of pods in the replica
    # set.
    assert stateful_set_ordinal < conf_vars['replica_set']

    # if we are provided a pod_name env, we must be provided a service_name env
    if os.environ.get('pod_name'):
        assert os.environ.get('service_name')

    # Make sure directories exist
    logger.info('Creating directories....')

    logger.debug(conf_vars['data_dir'])
    os.makedirs(conf_vars['data_dir'], exist_ok=True)

    logger.debug(conf_vars['log_dir'])
    os.makedirs(conf_vars['log_dir'], exist_ok=True)

    # Render zoo.cfg from jinja template and write out config
    with open('zoo.jinja2', 'r') as f:
        template = Template(f.read())

    conf_path = os.path.join(conf_vars['conf_dir'],
                             conf_vars['conf_file_name'])

    logger.info('Rendering template to {}'.format(conf_path))
    with open(conf_path, 'w') as conf:
        conf.write(template.render(**conf_vars))

    my_id_path = os.path.join(conf_vars['data_dir'], 'myid')

    # The ordinal from the pod_name MUST be an integer
    logger.debug('my_id_path: {}'.format(my_id_path))
    logger.debug('stateful_set_ordinal: {}'.format(stateful_set_ordinal))
    if not isinstance(stateful_set_ordinal, int):
        stateful_set_ordinal = 1

    logger.info('Setting myid to {} in file {}'.format(stateful_set_ordinal,
                                                       my_id_path))
    with open(my_id_path, 'w') as my_id_file:
        my_id_file.write(str(stateful_set_ordinal))

    with open(conf_path, 'r') as f:
        logger.debug('zookeeper conf file:')
        logger.debug(f.read())

    # Run Zookeeper (wait a little bit for the other pods to come up)
    time.sleep(90)
    zk_script = os.path.join(conf_vars['bin_dir'], 'zkServer.sh')
    subprocess.call([zk_script, 'start-foreground'])


if __name__ == '__main__':
    main()

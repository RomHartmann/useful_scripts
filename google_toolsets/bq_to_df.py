"""
We require python 3 for the google cloud python API
    mkvirtualenv --python `which python3` env3
And our dependencies:
    pip install pandas
    pip install google-cloud-bigquery
    pip install google-cloud-storage

http://google-cloud-python.readthedocs.io/en/latest/search.html?q=dataproc&check_keywords=yes&area=default

"""
import os
import time
import uuid

from google.cloud import bigquery
from google.cloud import storage
import pandas as pd


def bq_to_df(project_id, dataset_id, table_id, storage_uri, local_data_path):
    """Pipeline to get data from BigQuery into a local pandas dataframe.
    
    :param project_id: Google project ID we are working in.
    :type project_id: str
    :param dataset_id: BigQuery dataset id.
    :type dataset_id: str
    :param table_id: BigQuery table id.
    :type table_id: str
    :param storage_uri: Google Storage uri where data gets dropped off.
    :type storage_uri: str
    :param local_data_path: Path where data should end up.
    :type local_data_path: str
    :return: Pandas dataframe from BigQuery table.
    :rtype: pd.DataFrame
    """
    bq_to_storage(project_id, dataset_id, table_id, storage_uri)

    storage_to_local(project_id, storage_uri, local_data_path)

    data_dir = os.path.join(local_data_path, "test_data")
    df = local_to_df(data_dir)

    return df


def bq_to_storage(project_id, dataset_id, table_id, target_uri):
    """Export a BigQuery table to Google Storage.
    
    :param project_id: Google project ID we are working in.
    :type project_id: str
    :param dataset_id: BigQuery dataset name where source data resides.
    :type dataset_id: str
    :param table_id: BigQuery table name where source data resides.
    :type table_id: str
    :param target_uri: Google Storage location where table gets saved.
    :type target_uri: str
    :return: The random ID generated to identify the job.
    :rtype: str
    """
    client = bigquery.Client(project=project_id)

    dataset = client.dataset(dataset_name=dataset_id)
    table = dataset.table(name=table_id)

    job = client.extract_table_to_storage(
        str(uuid.uuid4()),  # id we assign to be the job name
        table,
        target_uri
    )
    job.destination_format = 'CSV'
    job.write_disposition = 'WRITE_TRUNCATE'

    job.begin()  # async execution

    if job.errors:
        print(job.errors)

    while job.state != 'DONE':
        time.sleep(5)
        print("exporting '{}.{}' to '{}':  {}".format(
            dataset_id, table_id, target_uri, job.state
        ))
        job.reload()

    print(job.state)

    return job.name


def storage_to_local(project_id, source_uri, target_dir):
    """Save a file or folder from google storage to a local directory.
    
    :param project_id: Google project ID we are working in.
    :type project_id: str
    :param source_uri: Google Storage location where file comes form.
    :type source_uri: str
    :param target_dir: Local file location where files are to be stored.
    :type target_dir: str
    :return: None
    :rtype: None
    """
    client = storage.Client(project=project_id)

    bucket_name = source_uri.split("gs://")[1].split("/")[0]
    file_path = "/".join(source_uri.split("gs://")[1].split("/")[1::])
    bucket = client.lookup_bucket(bucket_name)

    folder_name = "/".join(file_path.split("/")[0:-1]) + "/"
    blobs = [o for o in bucket.list_blobs() if o.name.startswith(folder_name)]

    # get files if we wanted just files
    blob_name = file_path.split("/")[-1]
    if blob_name != "*":
        print("Getting just the file '{}'".format(file_path))
        our_blobs = [o for o in blobs if o.name.endswith(blob_name)]
    else:
        print("Getting all files in '{}'".format(folder_name))
        our_blobs = blobs

    print([o.name for o in our_blobs])

    for blob in our_blobs:
        filename = os.path.join(target_dir, blob.name)

        # create a complex folder structure if necessary
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'wb') as f:
            blob.download_to_file(f)


def local_to_df(data_path):
    """Import local data files into a single pandas dataframe.
    
    :param data_path: File or folder path where csv data are located.
    :type data_path: str
    :return: Pandas dataframe containing data from data_path.
    :rtype: pd.DataFrame
    """
    # if data_dir is a file, then just load it into pandas
    if os.path.isfile(data_path):
        print("Loading '{}' into a dataframe".format(data_path))
        df = pd.read_csv(data_path, header=1)
    elif os.path.isdir(data_path):
        files = [os.path.join(data_path, fi) for fi in os.listdir(data_path)]
        print("Loading {} into a single dataframe".format(files))
        df = pd.concat((pd.read_csv(s) for s in files))
    else:
        raise ValueError(
            "Please enter a valid path.  {} does not exist.".format(data_path)
        )

    return df


if __name__ == '__main__':
    PROJECT_ID = "scoop-24-live"
    DATASET_ID = "articles"
    TABLE_ID = "subject_validation_set"
    STORAGE_URI = "gs://scoop-live-misc/test_data/*"
    LOCAL_DATA_PATH = "/Users/romanhartmann/work/dotmodus/playground/"

    bq_to_df(PROJECT_ID, DATASET_ID, TABLE_ID, STORAGE_URI, LOCAL_DATA_PATH)

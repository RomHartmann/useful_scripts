def create_dataframe(sQuery, sProjectID, bLargeResults=False):
    "takes a BigQuery sql query and returns a Pandas dataframe"
    
    if bLargeResults:
        oService = create_service()
        dDestinationTable = run_query(sQuery, oService, sProjectID)
        df = pandas_get_table(dDestinationTable)
    else:
        df = pandas_query(sQuery, sProjectID)
    
    return df
    






def pandas_query(sQuery, sProjectID):
    "go into bigquery and get the table with sql query and return dataframe"
    from pandas.io import gbq
    df = gbq.read_gbq(sQuery, sProjectID)
    
    return df 



def pandas_get_table(dTable):
    "fetch a table and return dataframe"
    from pandas.io import gbq
    
    sProjectID = dTable['projectId']
    sDatasetID = dTable['datasetId']
    sTableID = dTable['tableId']
    sQuery = "SELECT * FROM [{}.{}]".format(sDatasetID, sTableID)
    
    df = gbq.read_gbq(sQuery, sProjectID)
    
    return df 




def create_service():
    "create google service"
    from oauth2client.client import GoogleCredentials
    from apiclient.discovery import build
    credentials = GoogleCredentials.get_application_default()
    oService = build('bigquery', 'v2', credentials=credentials)
    return oService



def run_query(sQuery, oService, sProjectID):
    "runs the bigquery query"
    
    dQuery = {
        'configuration': {
            'query': {
                'writeDisposition': 'OVERWRITE',
                'useQueryCache': False,
                'allowLargeResults': True,
                'query': sQuery,
                'destinationTable': {
                    'projectId': sProjectID,
                    'datasetId': 'sandbox',
                    'tableId': 'api_large_result_dropoff',
                },
            }
        }
    }
    
    job = oService.jobs().insert(projectId=sProjectID, body=dQuery).execute()
    
    
    return job['configuration']['query']['destinationTable']
    
    















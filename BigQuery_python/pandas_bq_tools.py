class PandasBQ:

    def __init__(self):
        """tools for working with pandas and BigQuery"""
        pass



    def bq_to_df(self, sProjectID, sDatasetID, sTableID, sQuery=None, bAllowLargeResults=True, sInterimDatasetID=None, sInterimTableID=None):
        """returns a pandas dataframe from an existing table"""
        from pandas.io import gbq
        import pandas as pd

        if sQuery is None:
            sQuery = "SELECT * FROM {}.{}".format(sDatasetID, sTableID)

        if bAllowLargeResults:
            oService = self.create_service()

            if sInterimDatasetID is None:
                sInterimDatasetID = 'tmp'

            if sInterimTableID is None:
                sInterimTableID = '{}_large_result_dropoff'.format(sTableID)

            self.run_query(sQuery, oService, sProjectID, sInterimDatasetID, sInterimTableID)

            sInterimQuery = "SELECT * FROM {}.{}".format(sInterimDatasetID, sInterimTableID)

            bDone = False
            while not bDone:
                try:
                    df = gbq.read_gbq(sInterimQuery, sProjectID)
                    bDone = True
                except pd.io.gbq.GenericGBQException as e:
                    if 'Response too large' in e.message:
                        return None
                    else:
                        import time
                        time.sleep(5)

            return df
        else:
            return gbq.read_gbq(sQuery, self.sProjectID)




    @staticmethod
    def create_service():
        """create google service"""
        from oauth2client.client import GoogleCredentials
        from apiclient.discovery import build
        credentials = GoogleCredentials.get_application_default()
        oService = build('bigquery', 'v2', credentials=credentials)
        return oService



    @staticmethod
    def run_query(sQuery, oService, sProjectID, sInterimDataset, sIntermiTable):
        """runs the bigquery query to make an intermim table to make large results possible"""

        dQuery = {
            'configuration': {
                'query': {
                    'writeDisposition': 'OVERWRITE',
                    'useQueryCache': False,
                    'allowLargeResults': True,
                    'query': sQuery,
                    'destinationTable': {
                        'projectId': sProjectID,
                        'datasetId': sInterimDataset,
                        'tableId': sIntermiTable,
                    },
                }
            }
        }

        oService.jobs().insert(projectId=sProjectID, body=dQuery).execute()





    @staticmethod
    def df_to_bq(df, sTargetDataset, sTargetTable, sProjectID):
        """upload dataframe to BQ using pandas"""
        import pandas as pd
        sTable = "{}.{}".format(sTargetDataset, sTargetTable)
        pd.io.gbq.to_gbq(df, sTable, sProjectID, if_exists='replace')
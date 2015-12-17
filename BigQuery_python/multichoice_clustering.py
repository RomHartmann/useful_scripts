#import numpy as np
#import pandas as pd

#from sklearn import cluster, externals
#from sklearn.preprocessing import scale
#from stats import serviceBigQuery, getJob
##from stats import setUpLogging, getDelta, getQueryResults, getSchema, updateDelta, isfloat

#import logging.config
#log = logging.getLogger()


import bigquerytools


def main():
    "do clustering over different variables"
    
    #log.info('Script started')
    
    # get data
    #bq = serviceBigQuery()
    
    sProjectID = "multichoice-insights"
    
    sQuery = '''
        SELECT 
            c_subnum_i, c_title_s, c_firstname_s, c_surname_s,
            c_dateofbirth_dt, c_language_description_s, c_gender_s, 
            c_post_code_i, c_ethnicity_s, c_surname_indicator_s, c_city_s, a_active_i

        FROM [index_items.customer_items]
        limit 500
    '''
    
    df = bigquerytools.create_dataframe(
        sQuery, 
        sProjectID, 
        bLargeResults=True
    )
    
    print df[::len(df)/10]
    print "==="
    print len(df)








if __name__ == '__main__':
    main()
    
    
    
    















#roman@dotModus.com
#does a multivariate regression on a dataset

import csv
sIn = "/home/roman/dotModus/Data/MTN/flatfile/segment1.csv"


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm



def plot_plane(x,y,est, s1,s2):
    "plot plane given OLS"
    from mpl_toolkits.mplot3d import Axes3D

    ## Create the 3d plot
    xx1, xx2 = np.meshgrid(np.linspace(x[s1].min(), x[s1].max(), 100), 
                        np.linspace(x[s2].min(), x[s2].max(), 100))
    # plot the hyperplane by evaluating the parameters on the grid
    Z = est.params[0] + est.params[1] * xx1 + est.params[2] * xx2


    # create matplotlib 3d axes
    fig = plt.figure(figsize=(12, 8))
    ax = Axes3D(fig, azim=-115, elev=15)

    # plot hyperplane
    surf = ax.plot_surface(xx1, xx2, Z, cmap=plt.cm.RdBu_r, alpha=0.6, linewidth=0)

    # set axis labels
    ax.set_xlabel('voice')
    ax.set_ylabel('data')
    ax.set_zlabel('Spend')

    plt.show()


def MVR(sIn):
    oCSV = pd.read_csv(sIn, index_col=0)
    lHeaders = [
        ###'msisdn_kit_sim', 
        ###'pp_sbm_tenure_in_days', 
        ###'cluster_base', 
        'SMS_TotalSpend_Last30days', 
        'VOICE_TotalSpend_Last30days', 
        'DATA_TotalSpend_Last30days', 
        ###'PrimaryUsage_Previous30days', 
        'VAS_TotalSpend_Last30Days', 
        'TotalSpend_Last30days', 
        ###'Recharge_last_30d', 
        #'SMS_TotalSpend', 
        #'VOICE_TotalSpend', 
        #'DATA_TotalSpend', 
        #'TotalSpend', 
        'VAS_TotalSpend', 
        'VOICE_UserType', 
        'CallersInbound', 
        'CallersOutbound',
        ###'AVG_Recharge_Value'
    ]
    
    x = oCSV[lHeaders]
    y = oCSV['TotalSpend']

    #plt.plot(x,y)
    #plt.show()

    x = sm.add_constant(x)
    est = sm.OLS(y, x).fit()

    print est.summary()
    #plot_plane(x,y,est, 'VOICE_TotalSpend_Last30days','DATA_TotalSpend_Last30days')






#----------------------------------------------
MVR(sIn)









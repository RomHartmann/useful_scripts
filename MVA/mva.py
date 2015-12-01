#roman@dotModus.com
#does a multivariate regression on a dataset

import csv
sIn = "/home/roman/dotModus/Data/MTN/flatfile/selection10k.csv"


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





def str2list(s, sDel=","):
    'csv line string cleaned in list format'
    l=s.strip().split(sDel)
    try:
        import json
        return [json.loads(s) if s.strip()!="null" else None for s in l]
    except ValueError:
        return [s.strip() if s.strip()!="null" else None for s in l]



def csv2data(sIn):
    "read csv into numpy array in order to work on it first "
    lData = []

    with open(sIn, 'r') as f:
        sHeadings = f.readline()
        lHeadings = str2list(sHeadings)
        
        
        lWanted = [
            'cluster_name',
            'VOICE_UserType', 
            'PrimaryUsage_Previous30days', 
            'pp_sbm_tenure_in_days', 
            'SMS_TotalSpend_Last30days', 
            'VOICE_TotalSpend_Last30days', 
            'DATA_TotalSpend_Last30days', 
            'VAS_TotalSpend_Last30Days', 
            'TotalSpend_Last30days', 
            'Recharge_last_30d', 
            'SMS_TotalSpend', 
            'VOICE_TotalSpend', 
            'DATA_TotalSpend', 
            'VAS_TotalSpend', 
            'TotalSpend', 
            'VOICE_MinsTalked',
            'CallersInbound', 
            'CallersOutbound',
        ]
        
        
        #get lHeadings
        for sLine in f:
            lLine = str2list(sLine)
            dLine = dict(zip(lHeadings, lLine))
            
            lClusterVals = [0.0337,-0.279,-0.013,0.308,-0.336,-0.011,0.429,-0.170,-0.059]  #from pca
            #lClusterVals = [26.0, -32.4, -5.45, 57.4, -50.8, 6.30, 57.1, -38.8, -23.0]  #from mvr coeffs 10k
            #lClusterVals = [33.4693, -33.2963, -5.6164, 58.3299, -51.2927, 5.7932, 58.8850, -39.5981, -22.3072]     #from mvr coeffs 1M
                #1M  r2: [0.03, 0.04, 0.002, 0.078, 0.071, 0.001, 0.120, 0.026, 0.001]
            
            #lClusterVals = [0 for i in range(9)]
            #lClusterVals[8] = 10
            
            if dLine['cluster_name']=='new age': dLine['cluster_name']=lClusterVals[0]               
            elif dLine['cluster_name']=='budget conscious': dLine['cluster_name']=lClusterVals[1]    
            elif dLine['cluster_name']=='broadcasters': dLine['cluster_name']=lClusterVals[2]        
            elif dLine['cluster_name']=='VAS users': dLine['cluster_name']=lClusterVals[3]           
            elif dLine['cluster_name']=='receivers': dLine['cluster_name']=lClusterVals[4]           
            elif dLine['cluster_name']=='data converters': dLine['cluster_name']=lClusterVals[5]     
            elif dLine['cluster_name']=='telemetry': dLine['cluster_name']=lClusterVals[6]           
            elif dLine['cluster_name']=='low-end': dLine['cluster_name']=lClusterVals[7]              
            elif dLine['cluster_name']=='mobile warrior': dLine['cluster_name']=lClusterVals[8]       
            
            
            if dLine['VOICE_UserType']=='INBOUND': dLine['VOICE_UserType']=-0.190      #-0.19093736690618129
            elif dLine['VOICE_UserType']=='MIXED': dLine['VOICE_UserType']=0.010        #0.010991888470893434
            elif dLine['VOICE_UserType']=="OUTBOUND": dLine['VOICE_UserType']=0.147     #0.14735872614051032
            
            if dLine['PrimaryUsage_Previous30days']=='NA': dLine['PrimaryUsage_Previous30days']=-0.414    #-0.41465399296257249
            if dLine['PrimaryUsage_Previous30days']=='VOICE': dLine['PrimaryUsage_Previous30days']=0.405  #0.40552462994901067
            if dLine['PrimaryUsage_Previous30days']=='SMS': dLine['PrimaryUsage_Previous30days']=-0.046   #-0.046296024054576904
            if dLine['PrimaryUsage_Previous30days']=='DATA': dLine['PrimaryUsage_Previous30days']=-0.077  #-0.077664116058754742
            
            
            lData.append([ float(dLine[s]) for s in lWanted ])

    aData = np.array(lData)
    
    aDataReshape = aData.reshape((-1,len(lWanted)))
    dDataReshaped = dict(zip(lWanted, np.array([aDataReshape[:,i] for i in range(len(lWanted)) ])))
    
    df = pd.DataFrame( dDataReshaped )
    
    return aData, df




def MVR(sIn):
    #oDF = pd.read_csv(sIn, index_col=0)
    
    
    lHeaders = [
        'cluster_name',
        #'VOICE_UserType', 
        #'PrimaryUsage_Previous30days', 
        #'pp_sbm_tenure_in_days', 
        #'SMS_TotalSpend_Last30days', 
        #'VOICE_TotalSpend_Last30days', 
        #'DATA_TotalSpend_Last30days', 
        #'VAS_TotalSpend_Last30Days', 
        #'TotalSpend_Last30days', 
        #'Recharge_last_30d', 
        #'SMS_TotalSpend', 
        #'VOICE_TotalSpend', 
        #'DATA_TotalSpend', 
        #'VAS_TotalSpend', 
        #'TotalSpend', 
        #'VOICE_MinsTalked',
        #'CallersInbound', 
        #'CallersOutbound',
    ]
    
    aData, oDF = csv2data(sIn)
    
    
    x = oDF[lHeaders]
    y = oDF['TotalSpend']
    
    #plotting
    if True:
        plt.figure(1)
        ax = plt.subplot(111)
        for i in range(len(lHeaders)):
            xi = oDF[lHeaders[i]]
            xNorm = xi/max(abs(xi))
            yNorm = y/max(y)
            
            ax.scatter(xi, yNorm, alpha=0.4, label=lHeaders[i], marker='.......sssssssxxxxxxxooooooo'[i], color='rbgycmkrbgycmkrbgycmkrbgycmk'[i])
        
        plt.xlabel('Dep Vars')
        plt.ylabel('TotalSpend')
        #label:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                fancybox=True, shadow=True, ncol=5)
        plt.show()

    x = sm.add_constant(x)
    est = sm.OLS(y, x).fit()

    print est.summary()
    #plot_plane(x,y,est, 'VOICE_TotalSpend_Last30days','DATA_TotalSpend_Last30days')






#----------------------------------------------
MVR(sIn)









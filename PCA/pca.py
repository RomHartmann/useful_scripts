#does principal component analysis on a dataset
#roman@dotModus.com

import csv
sIn = "/home/roman/dotModus/Data/MTN/flatfile/selection10k.csv"


lWanted = [
    #'cluster_name',
    #'VOICE_UserType', 
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



import matplotlib.pyplot as plt
import numpy as np

import pandas as pd


def str2list(s, sDel=","):
    'csv line string cleaned in list format'
    l=s.strip().split(sDel)
    try:
        import json
        return [json.loads(s) if s.strip()!="null" else None for s in l]
    except ValueError:
        return [s.strip() if s.strip()!="null" else None for s in l]



def print_dict(d):
    'print dict nicely and in desc order'
    lt = [(s, d[s]) for s in sorted(d, key=d.get, reverse=True)]
    print("\n------------------------------------")
    for tup in lt:
        print("{0}:  {1}".format(tup[0], tup[1]))
    print("------------------------------------")





def biplot(plt, pca, labels=None, xpc=1, ypc=2, scale=1, bPoints=False):
    """Generate biplot from the result of pcasvd of statsmodels.
    Parameters
    ----------
    plt : object
        An existing pyplot module reference.
    pca : tuple
        The result from statsmodels.sandbox.tools.tools_pca.pcasvd.
    labels : array_like, optional
        Labels for each observation.
    xpc, ypc : int, optional
        The principal component number for x- and y-axis. Defaults to
        (xpc, ypc) = (1, 2).
    scale : float
        The variables are scaled by lambda ** scale, where lambda =
        singular value = sqrt(eigenvalue), and the observations are
        scaled by lambda ** (1 - scale). Must be in [0, 1].
    Returns
    -------
    None.
    """
    xreduced, factors, evals, evecs = pca
    singvals = np.sqrt(evals)
    
    if bPoints:
        #Plots the data points
        # data
        xs = factors[:, xpc] * singvals[xpc]**(1. - scale)
        ys = factors[:, ypc] * singvals[ypc]**(1. - scale)

        if labels is not None:
            for i, (t, x, y) in enumerate(zip(labels, xs, ys)):
                c = 'k'
                plt.text(x, y, t, color=c, ha='center', va='center')
            xmin, xmax = xs.min(), xs.max()
            ymin, ymax = ys.min(), ys.max()
            xpad = (xmax - xmin) * 0.1
            ypad = (ymax - ymin) * 0.1
            plt.xlim(xmin - xpad, xmax + xpad)
            plt.ylim(ymin - ypad, ymax + ypad)
        else:
            colors = 'k' 
            plt.scatter(xs, ys, c=colors, marker='.')

    # variables
    tvars = np.dot(np.eye(factors.shape[0], factors.shape[1]),
                   evecs) * singvals**scale
    
    lX = []
    lY = []
    for i, col in enumerate(xreduced.columns.values):
        x, y = tvars[i][xpc], tvars[i][ypc]
        lX.append(x)
        lY.append(y)
        plt.arrow(0, 0, x, y, color='r',
                  width=0.0015, head_width=0.02)
        plt.text(x* 1.2, y * 1.2, col, color='k', ha='center', va='center', fontsize=10)

    plt.xlabel('PC{}'.format(xpc))
    plt.ylabel('PC{}'.format(ypc))
    
    return lX,lY



def csv2np(sIn):
    "read csv into numpy array in order to work on it first"
    lData = []

    with open(sIn, 'r') as f:
        sHeadings = f.readline()
        lHeadings = str2list(sHeadings)
        
        sComponent = "PrimaryUsage_Previous30days"
        sValue = "DATA"
        
        #get lHeadings
        for sLine in f:
            lLine = str2list(sLine)
            dLine = dict(zip(lHeadings, lLine))
            
            
            #if dLine['cluster_name']=='new age': dLine['cluster_name']=10                #0.033759415925477598
            #elif dLine['cluster_name']=='budget conscious': dLine['cluster_name']=0     #-0.27922707897897081
            #elif dLine['cluster_name']=='broadcasters': dLine['cluster_name']=0         #-0.013175807456775795
            #elif dLine['cluster_name']=='VAS users': dLine['cluster_name']=0            #0.30878679045731117
            #elif dLine['cluster_name']=='receivers': dLine['cluster_name']=0            #-0.33607132025675324
            #elif dLine['cluster_name']=='data converters': dLine['cluster_name']=0      #-0.011152080713308928
            #elif dLine['cluster_name']=='telemetry': dLine['cluster_name']=0            #0.42991492995093794
            #elif dLine['cluster_name']=='low-end': dLine['cluster_name']=0              #-0.17057362008866914
            #elif dLine['cluster_name']=='mobile warrior': dLine['cluster_name']=0       #-0.059600860532992746
            
            
            #if dLine['VOICE_UserType']=='INBOUND': dLine['VOICE_UserType']=0        #-0.19093736690618129
            #elif dLine['VOICE_UserType']=='MIXED': dLine['VOICE_UserType']=0        #0.010991888470893434
            #elif dLine['VOICE_UserType']=="OUTBOUND": dLine['VOICE_UserType']=0     #0.14735872614051032
            
            #if dLine['PrimaryUsage_Previous30days']=='NA': dLine['PrimaryUsage_Previous30days']=0    #-0.41465399296257249
            #if dLine['PrimaryUsage_Previous30days']=='VOICE': dLine['PrimaryUsage_Previous30days']=0  #0.40552462994901067
            #if dLine['PrimaryUsage_Previous30days']=='SMS': dLine['PrimaryUsage_Previous30days']=0   #-0.046296024054576904
            #if dLine['PrimaryUsage_Previous30days']=='DATA': dLine['PrimaryUsage_Previous30days']=0  #-0.077664116058754742
            
            if dLine[sComponent]==sValue: dLine[sComponent] = 10
            else: dLine[sComponent] = 0
            
            lData.append([ float(dLine[s]) for s in lWanted ])

    aData = np.array(lData)
    
    return aData, sComponent, sValue

    

def pca_coeffs(sIn, lWanted):
    'returns list of coeffs'
    aData = csv2np(sIn)

    from sklearn.decomposition import PCA
    pca = PCA(n_components = len(lWanted))
    pca.fit(aData)
    
    
    #print and plot shit
    dVariance = dict(zip(lWanted, pca.explained_variance_ratio_))
    print("========================================================")
    print("Variance ratio (percent variance explained by each component):  ")
    print_dict(dVariance) 
    
    lComponents = pca.components_
    dComponents = dict(zip(lWanted, lComponents))
    print("========================================================")
    
    plt.figure(1)
    ax = plt.subplot(111)
    for i in range(len(lWanted)):
        ax.plot(lComponents[i], label="{0}:  {1}".format(i,lWanted[i]), marker='.o+,v^<>sp*hxd1.o+,v^<>sp*hxd1'[i])
    plt.suptitle("Principal axes in feature space")
    plt.title("representing the directions of maximum variance in the data.")
    ax.axis([-0.5,len(lWanted)-0.5,-1.1,1.1])
    #label:
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=5)
    ax.grid()
    plt.show()




def create_biplot(sIn, lWanted):
    """Run a PCA on state.x77 from R and generate its biplot. Color
    observations by k-means clustering."""
    from scipy.cluster.vq import kmeans, vq
    from statsmodels.sandbox.tools.tools_pca import pcasvd
    
    aData, sComponent, sValue = csv2np(sIn)
    aDataReshape = aData.reshape((-1,len(lWanted)))
    dDataReshaped = dict(zip(lWanted, np.array([aDataReshape[:,i] for i in range(len(lWanted)) ])))
    
    df = pd.DataFrame( dDataReshaped )
    #df = pd.io.parsers.read_csv(sIn, ',')
    
    #print df.describe()
    #print df.head()

    data = df[lWanted]
    
    data = (data - data.mean()) / data.std()
    pca = pcasvd(data, keepdim=0, demean=False)
    
    #import pdb; pdb.set_trace()
    
    plt.figure(2)
    lX,lY = biplot(plt, pca, labels=data.index, xpc=0, ypc=1, bPoints=False)
    
    if True:
        "get dot product for a variable - investigative tool for categorical units"
        #sComponent = "PrimaryUsage_Previous30days"
        iIndex1 = lWanted.index(sComponent)
        xVar = lX[iIndex1]
        yVar = lY[iIndex1]
        print('{}:  {}, {}'.format(sComponent,xVar, yVar))
        
        sTot = "TotalSpend"
        iIndex2 = lWanted.index(sTot)
        xTot = lX[iIndex2]
        yTot = lY[iIndex2]
        print('{}:  {}, {}'.format(sTot, xTot, yTot))
        
        rDotProd = (xVar * xTot) + (yVar * yTot)
        print("Dot product = ", rDotProd)
    
    plt.axis([-1.2,1.2,-1.2,1.2])
    plt.suptitle('"{}"  for ({} . {})'.format(sValue, sComponent, sTot))
    plt.title("Dot product = {}".format(round(rDotProd, 4)))
    plt.show()



#pca_coeffs(sIn, lWanted)
create_biplot(sIn, lWanted)

















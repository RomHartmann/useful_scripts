#does principal component analysis on a dataset
#roman@dotModus.com

import csv
sIn = "/home/roman/dotModus/Data/MTN/flatfile/segment1.csv"


lWanted = [
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
    'SMS_TotalSpend', 
    'VOICE_TotalSpend', 
    'DATA_TotalSpend', 
    'TotalSpend', 
    'VAS_TotalSpend', 
    'VOICE_UserType', 
    'CallersInbound', 
    'CallersOutbound',
    ###'AVG_Recharge_Value'
]


import matplotlib.pyplot as plt
import numpy as np

import pandas as pd


def str2list(s):
    'csv line string cleaned in list format'
    l=s.strip().split(",")
    return [s.strip() if s.strip()!="null" else None for s in l]


def print_dict(d):
    'print dict nicely and in desc order'
    lt = [(s, d[s]) for s in sorted(d, key=d.get, reverse=True)]
    print("\n------------------------------------")
    for tup in lt:
        print("{0}:  {1}".format(tup[0], tup[1]))
    print("------------------------------------")





def biplot(plt, pca, labels=None, colors=None, xpc=1, ypc=2, scale=1):
    """Generate biplot from the result of pcasvd of statsmodels.
    Parameters
    ----------
    plt : object
        An existing pyplot module reference.
    pca : tuple
        The result from statsmodels.sandbox.tools.tools_pca.pcasvd.
    labels : array_like, optional
        Labels for each observation.
    colors : array_like, optional
        Colors for each observation.
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
    xpc, ypc = (xpc - 1, ypc - 1)
    xreduced, factors, evals, evecs = pca
    singvals = np.sqrt(evals)

    ##Plots the data points
    ## data
    #xs = factors[:, xpc] * singvals[xpc]**(1. - scale)
    #ys = factors[:, ypc] * singvals[ypc]**(1. - scale)

    #if labels is not None:
        #for i, (t, x, y) in enumerate(zip(labels, xs, ys)):
            #c = 'k' if colors is None else colors[i]
            #plt.text(x, y, t, color=c, ha='center', va='center')
        #xmin, xmax = xs.min(), xs.max()
        #ymin, ymax = ys.min(), ys.max()
        #xpad = (xmax - xmin) * 0.1
        #ypad = (ymax - ymin) * 0.1
        #plt.xlim(xmin - xpad, xmax + xpad)
        #plt.ylim(ymin - ypad, ymax + ypad)
    #else:
        #colors = 'k' if colors is None else colors
        #plt.scatter(xs, ys, c=colors, marker='.')

    # variables
    tvars = np.dot(np.eye(factors.shape[0], factors.shape[1]),
                   evecs) * singvals**scale

    for i, col in enumerate(xreduced.columns.values):
        x, y = tvars[i][xpc], tvars[i][ypc]
        plt.arrow(0, 0, x, y, color='r',
                  width=0.002, head_width=0.05)
        plt.text(x* 1.4, y * 1.4, col, color='k', ha='center', va='center')

    plt.xlabel('PC{}'.format(xpc + 1))
    plt.ylabel('PC{}'.format(ypc + 1))
#------------


def pca_coeffs(sIn, lWanted):
    'returns list of coeffs'
    lData = []

    with open(sIn, 'r') as f:
        sHeadings = f.readline()
        lHeadings = str2list(sHeadings)
        
        
        #print lHeadings
        for sLine in f:
            lLine = str2list(sLine)
            dLine = dict(zip(lHeadings, lLine))
            
            lData.append([ dLine[s] for s in lWanted ])

    aData = np.array(lData)
    #print aData

    from sklearn.decomposition import PCA
    pca = PCA(n_components = len(lWanted))
    pca.fit(aData)
    dResults = dict(zip(lWanted, pca.explained_variance_ratio_))
    print_dict(dResults) 




def create_biplot(sIn, lWanted):
    """Run a PCA on state.x77 from R and generate its biplot. Color
    observations by k-means clustering."""
    from scipy.cluster.vq import kmeans, vq
    from statsmodels.sandbox.tools.tools_pca import pcasvd

    df = pd.io.parsers.read_csv(sIn)
    print df.describe()
    #print df.head()


    data = df[lWanted]
    data = (data - data.mean()) / data.std()
    pca = pcasvd(data, keepdim=0, demean=False)

    values = data.values
    centroids, _ = kmeans(values, len(lWanted))
    idx, _ = vq(values, centroids)

    colors = ['gbycrmkgbycrmk'[i] for i in idx]

    plt.figure(1)
    biplot(plt, pca, labels=data.index, colors=colors,
           xpc=1, ypc=2)
    plt.show()


pca_coeffs(sIn, lWanted)
create_biplot(sIn, lWanted)



























"""Least sqares inversion
m... is a matrix
l... is a list
a... is a numpy array (it obeys matrix calculations)
i... is an integer/float
t... is a tuple
d... is a dictionary
o... is an object which does not belong to the above

#------------------
"""

from fatiando import mesher, gridder
from fatiando.gravmag import prism, imaging
from fatiando.vis import mpl, myv

import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

oTimeBeforeSetup = datetime.now()


def calc_misfit(aObserved, aCalculated):
    """
    calculates the misfit between the observed and calculated signals and returns a scalar
    """
    iMisfit = 0
    for i in range(len(aObserved)):
        iMisfit += (aObserved[i] - aCalculated[i])**2
    return iMisfit



#---------------create test data------------------
#   --------model specific parameters-------

#load signal
mWitsSignal = np.loadtxt("Gravport_Reduced.csv", delimiter=",")
mObservedSignal = mWitsSignal[100:200, 200:300]      #original signal



#inversion specific variables:
iIterations     = 4     #number of iterations to be done
iReferenceHeight = 1    #reference height above ground in meters
iDeltaZ = 1             #original depth displacement in meters to create change matrix (mFmodelDiff -> mMetricChange)iInvDampFact    = 1e-9  #used in M-P inversion when inverse of M is unitary (d.n.e)
iMinDepth = 0.001       #minimum non zero depth in meters a prism can have


#x and y shape and borders of signal
tSignalSize = (100, 100)
tSignalBorders = (0, 100000, 0, 100000)

iNrSignalPoints = tSignalSize[0] * tSignalSize[1]

#x and y widths of prisms
iXPrismSpacing = 5000
iYPrismSpacing = 5000

iXNrPrisms = (tSignalBorders[1] - tSignalBorders[0])/iXPrismSpacing
iYNrPrisms = (tSignalBorders[3] - tSignalBorders[2])/iYPrismSpacing
iNrPrisms = iXNrPrisms * iYNrPrisms

#Reshape observed data
aObservedSignal = np.reshape(mObservedSignal, iNrSignalPoints)     #reshaped vredefort data into array


#array of depths of each prism
aDepths = np.ones(iNrPrisms) *1000    #preallocate depths in meters of prisms

#constant density in kg/m3 for each prism
iDensity = -800
#-------------------------------------


#preallocate inversion matrices and arrays
aMetricChange = np.zeros(iNrPrisms)                             #determines change of metric (eg depth)
mFmodelDiff = np.zeros((len(aObservedSignal), iNrPrisms))       #determines error matrix
lMisfit = []                                                    #for misfit curve
lIterations = []




#create initial model - array of prisms
lModel = []
for i in range(len(aDepths)):
    iXStart = tSignalBorders[0] + (i%iXNrPrisms)*iXPrismSpacing
    iXEnd = tSignalBorders[0] + iXPrismSpacing + (i%iXNrPrisms)*iXPrismSpacing
    iYStart = tSignalBorders[2] + (np.floor(i/iYNrPrisms))*iYPrismSpacing
    iYEnd = tSignalBorders[2] + iYPrismSpacing + (np.floor(i/iYNrPrisms))*iYPrismSpacing
    iZStart = 0
    iZEnd = aDepths[i]
    dProperties = {'density': iDensity, 'depth': iZEnd}
    
    lModel.append(
        mesher.Prism(iXStart, iXEnd, iYStart, iYEnd, iZStart, iZEnd, dProperties)
    )

#create grid for signal
aXGridCoords, aYGridCoords, aZGridCoords = gridder.regular(tSignalBorders, tSignalSize, z=iReferenceHeight)


#---Plot the Original Signal---
#mpl.figure(figsize=(8,7))
#mpl.contourf(aYGridCoords, aXGridCoords, aObservedSignal, tSignalSize, 50)  #last arg is number of contours
#mpl.show()

oTimeAfterSetup = datetime.now()
print("-----Setup Time", oTimeAfterSetup - oTimeBeforeSetup)
oTimeBeginTot = datetime.now()


#-----Start Inversion
for iIter in range(iIterations):
    """
    in each iteration:
        calculate mFmodelDiff from forward modelling current prisms
        use mFmodelDiff to calculate aSignalError and aMetricChange
    """
    oTimeBeginIteration = datetime.now()
    
    aCalcSignal = np.zeros(iNrSignalPoints)   #preallocate and zero forward modelled signal
    
    iVoxelCount = 0
    
    oTimeBeforeMapping = datetime.now()
    for oVoxel in lModel:       #NOTE each oVoxel can be sent to a different mapper
        #for each prism:
            #calculate forward model for each prism and create mFmodelDiff
                #mFmodelDiff contains all prisms' forward modelled vectors
            #also return superposition of all prisms' signals in form of lCalc1
            #Each one of these calcs could be done by a mapreduce task
        
        oVoxel.z2 += aMetricChange[iVoxelCount]     #update the voxel metric by the residual vector from the inversion
        oVoxel.z2 = iMinDepth if oVoxel.z2 < 0 else oVoxel.z2   #make sure depths are non negative
        
        #calculate first forward model
        aPrismCalc1 = prism.gz(aXGridCoords, aYGridCoords, aZGridCoords, [oVoxel])
        oVoxel.z2 += iDeltaZ
        
        #calculate second forward model
        aPrismCalc2 = prism.gz(aXGridCoords, aYGridCoords, aZGridCoords, [oVoxel])
        
        #compare computed signal change due to the model change and store for each prism
        mFmodelDiff[:, iVoxelCount] = (aPrismCalc2 - aPrismCalc1)/iDeltaZ
        
        iVoxelCount += 1
        
        
        #superimpose the signal for each prism into an array for the whole area
        aCalcSignal += aPrismCalc1      #NOTE this would be done in the reducer
        
        #--- end forward modelling each voxel
    oTimeAfterMapping = datetime.now()
    
    #------ Mathematical notes-----
    #X.dot(Y) does matrix multiplication  X * Y or dot product for vectors
    #pseudoinverse x = np.linalg.pinv(A).dot(b)   where Ax = b;   A is matrix, x,b array
        #pseudoinverse because A may be singular, and thus has no inverse
    #aSignalError is the residual vector and is responsible for updating the metric
    
    
    aSignalError = aObservedSignal - aCalcSignal
    
    
    oTimeBeforeInversion = datetime.now()
    #----------Inversion----------
        #TODO if matrices get much larger, look for better ways to invert mFmodelDiff
    aMetricChange = np.linalg.pinv(mFmodelDiff).dot(aSignalError)
    
    oTimeAfterInversion = datetime.now()
    
    print("1)-  Forward modelling time", oTimeAfterMapping-oTimeBeforeMapping)
    print("2) - time per voxel = ", (oTimeAfterMapping-oTimeBeforeMapping)/iVoxelCount)
    print("3)  -Inversion time", oTimeAfterInversion-oTimeBeforeInversion)
    
    lMisfit.append(calc_misfit(aObservedSignal, aCalcSignal))
    lIterations.append(iIter)
    
    
    
    oTimeEndIteration = datetime.now()
    print("-----Iteration number:", iIter, oTimeEndIteration-oTimeBeginIteration)
    #--- end iterations
    

    oTimeEndTot = datetime.now()
    oTimeEndIteration = datetime.now()
    print("~~~~~~~~~~Total Time:", oTimeEndTot-oTimeBeginTot)

    oTimeBeforePlotting = datetime.now()


    #-----Drawing-----
    #Plot the model
    myv.figure()
    myv.prisms(lModel, 'density', style='surface')
    axes = myv.axes(myv.outline())
    myv.wall_bottom(axes.axes.bounds)
    myv.wall_north(axes.axes.bounds)
    myv.title("Geological Model")


    # Plot the forward modelled signal
    mpl.figure(figsize=(16,5))
    mpl.subplot(121)
    mpl.title("Original signal")
    mpl.axis('scaled')
    mpl.contourf(aYGridCoords, aXGridCoords, aObservedSignal, tSignalSize, 50)  #last arg is number of contours
    mpl.colorbar()
    mpl.xlabel('East (km)')
    mpl.ylabel('North (km)')
    mpl.m2km()

    mpl.subplot(122)
    mpl.title("Forward modelled signal")
    mpl.axis('scaled')
    mpl.contourf(aYGridCoords, aXGridCoords, aCalcSignal, tSignalSize, 50)  #last arg is number of contours
    mpl.colorbar()
    mpl.xlabel('East (km)')
    mpl.ylabel('North (km)')
    mpl.m2km()

    plt.figure()
    plt.plot(lIterations, lMisfit)
    plt.xlabel('Iterations')
    plt.ylabel('Arbitrary misfit')
    plt.title("Misfit Curve")

    myv.show()
    mpl.show()
    plt.show()


    oTimeAfterPlotting = datetime.now()
    print("Plotting Time", oTimeAfterPlotting-oTimeBeforePlotting)








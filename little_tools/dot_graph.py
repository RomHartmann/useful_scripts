

def dot_graph(lData, iHeight=5):
    """take a list of values and plot a graph in terminal"""
    
    lData = [float(i) for i in lData]
    rRange = max(lData)-min(lData)
    rRange = rRange if rRange!=0 else 1     #stop divide by zero
    lPlotBins = []
    for i in range(len(lData)):
        rDiff = lData[i] - min(lData)
        iBin = int((iHeight-1) *(rDiff/rRange))
        lPlotBins.append(iBin)

    sPlot = ""
    for j in range(iHeight+1):
        sPlot += "|"
        for i in range(len(lPlotBins)):
            sPlot += "=" if j==(iHeight) else "*" if (((iHeight-1)-lPlotBins[i])==j) else " "
        sPlot += "\n"

    print sPlot





v = [6,2,4,8,9,3,5,1,4,7,20,26,32,31,22,12,5,6,5,5,4,7,8,9,6,2,3]

dot_graph(v)



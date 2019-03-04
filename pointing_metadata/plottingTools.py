import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import pandas as pd

def makeStamps(name,objectList,imagePath,numCols=5):
    """Generate postage stamps of an MPC object in the Lori Allen Dataset.
    
    INPUT-
        name: This is the name of the object for which to find the image.
            Names come from the query_MPC notebook that pulls data down from
            the Minor Planets Center.
        objectList: A pandas dataframe as generated by query_MPC.
        imagePath: The path to the stack of images from which to make stamps.
        numCols: The number of columns in the postage stamp subplot.
    """
    
    # Desired stamp size.
    stampSize = [31,31]
    # Make a dataframe of a single object so that we can plot the stamps for only this object
    singleObject = objectList[objectList['name']==name]
    singleObject.reset_index(inplace=True)

    # Find the number of subplots to make. Add one for the coadd.
    numPlots = len(singleObject.index)+1
    # Compute number of rows for the plot
    numRows = numPlots // numCols
    # Add a row if numCols doesn't divide evenly into numPlots
    if (numPlots % numCols):
        numRows+=1
    # Add a row if numRows=1. Avoids an error caused by ax being 1D.
    if (numRows==1):
        numRows+=1
    # Generate the subplots, setting the size with figsize
    fig,ax = plt.subplots(nrows=numRows,ncols=numCols,figsize=[3*numCols,3.5*numRows])
    objectMag = np.max(singleObject['v_mag'])
    fig.suptitle(name+'\nv_mag='+str(objectMag),fontsize=16)
    # Turn off all axes. They will be turned back on for proper plots.
    for row in ax:
        for column in row:
            column.axis('off')
    # Set the axis indexes. These are needed to plot the stamp in the correct subplot
    axi=0
    axj=1
    for i,row in singleObject.iterrows():
        # Get the Lori Allen visit id from the single object list
        visit_id = row['visit_id']
        # Get the x and y values from the first object in the cut list. Round to an integer.
        objectLoc = np.round([row['x_pixel'],row['y_pixel']])
        # Open up the fits file of interest using the pre-defined filepath string
        hdul = fits.open(imagePath+str(visit_id)+'.fits')

        # Generate the minimum and maximum pixel values for the stamps using stampSize
        xmin = int(objectLoc[0]-(stampSize[0]-1)/2)
        xmax = int(objectLoc[0]+(stampSize[0]-1)/2)
        ymin = int(objectLoc[1]-(stampSize[1]-1)/2)
        ymax = int(objectLoc[1]+(stampSize[1]-1)/2)

        im_dims = np.shape(hdul[1].data)
        # Plot the stamp
        stampData = hdul[1].data[ymin:ymax,xmin:xmax]
        if i==0:
            coaddData=stampData
        else:
            coaddData+=stampData
        im = ax[axi,axj].imshow(stampData,cmap=plt.cm.bone)
        ax[axi,axj].set_title('visit='+str(visit_id))
        ax[axi,axj].axis('on')
        # Compute the axis indexes for the next iteration
        if axj<numCols-1:
            axj+=1
        else:
            axj=0
            axi+=1
    im = ax[0,0].imshow(coaddData,cmap=plt.cm.bone)
    ax[0,0].axis('on')
    _=ax[0,0].set_title('Coadd')

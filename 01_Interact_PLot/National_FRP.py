""" This script is a compilation of many useful tools needed to
format data for use with ANUGA
"""

import sys
import os
import glob
import os.path
from easygui import *
from os.path import *
import anuga
from anuga.utilities import plot_utils
from numpy import array, float, resize
from anuga.geospatial_data.geospatial_data import Geospatial_data


# ---- FUNCTIONS USED -------------------------
def View_GTiff(filename):
    """
    Will allow the viewing of a Geotiff.....
    
    """
    from osgeo import gdal
    import sys 
    gdal.UseExceptions()
    ds=gdal.Open(filename) 
    band= ds.getRasterBand(1)
    return()

def Create_Hazard_Map(filename,quantities,output_dir,timeSlices):
    """
    This Function Takes reads a SWW file and processes them to create the Hazard MAP Layer based on 2016 procedure
    
    Use tips from:
    https://gis.stackexchange.com/questions/125202/gdal-clipping-a-raster-with-another-raster
    GDAL_Calc.py -A Mask.tif -B CutBigImageToClip.tif --outfile=SmallerFile.tif --NoDataValue=0 --Calc="B*(A>0)"
       
    """
    print filename
    print output_dir
    VxDtif = os.path.join(output_dir,os.path.basename(filename[:-4]+'_'+quantities[0]+'_'+timeSlices+'.tif'))
    DEPtif = os.path.join(output_dir,os.path.basename(filename[:-4]+'_'+quantities[1]+'_'+timeSlices+'.tif'))
    VELtif = os.path.join(output_dir,os.path.basename(filename[:-4]+'_'+quantities[2]+'_'+timeSlices+'.tif'))
    os.chdir(output_dir)
    
    # Set Up Criteria for Filtering Hazard
    Haz_list = []
    Haz_list.append(['H1','<=0.3','<=0.3','<=2.0',1]) # Hazard, VxD, D, V, layer number
    Haz_list.append(['H2','<=0.6','<=0.5','<=2.0',2])
    Haz_list.append(['H3','<=0.6','<=1.2','<=2.0',3])
    Haz_list.append(['H4','<=1.0','<=2.0','<=2.0',4])
    Haz_list.append(['H5','<=4.0','<=4.0','<=4.0',5])
    Haz_list.append(['H6','>=0.1','>=0.1','>=0.1',6])
    
    Param_list = ['VxD','DEP','VEL']
    File_list = [VxDtif,DEPtif,VELtif]
    
    for i in range(len(Haz_list)): # Loop Through Criteria to Filter
        for j in range(len(Param_list)): # Loop through Parameters
            os.system('gdal_calc.py -A ' + File_list[j]+' --outfile='+Haz_list[i][0]+'_'+Param_list[j]+'.tif --calc="A*(A'+Haz_list[i][j+1]+')" --NoDataValue=0') #create individual VxD, D and V based on Haz_list
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'_'+Param_list[0]+'.tif -B '+Haz_list[i][0]+'_'+Param_list[1]+'.tif -C '+Haz_list[i][0]+'_'+Param_list[2]+'.tif --outfile='+Haz_list[i][0]+'temp.tif --calc="A+B+C " --NoDataValue=0')
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'temp.tif --outfile='+Haz_list[i][0]+'.tif --calc="'+str(Haz_list[i][4])+'*(A>0.001)" --NoDataValue=0')  #Combined Layers VxD, D, V

    # Merge to Create a Single tiff
    os.system('gdal_merge.py H6.tif H5.tif H4.tif H3.tif H2.tif H1.tif -o HAZARDsingleband.tif')
    # Now Apply Color Relief based on values 0 - 6
    # Color table values..(Value, R, G,B, Opacity)
    color_table_file = open('color_haz.txt', 'w')

    color_table_file.write('0,white,0\n')
    color_table_file.write('1,blue\n')
    color_table_file.write('2,0,255,255\n') 
    color_table_file.write('3,green\n')
    color_table_file.write('4,0,255,0\n')
    color_table_file.write('5,yellow\n')
    color_table_file.write('6,red\n')
    color_table_file.close()
    
    # Merge to M_FRP and H_FRP files to create a Single tiff (THIS DOES NOT WORK)   
    #os.system('gdaldem color-relief HAZARDsingleband.tif color_haz.txt '+filename[:-4]+'_HAZARD.tif')

    # Clean up Temp Files
    for i in range(len(Haz_list)):
        command_txt = 'rm '+Haz_list[i][0]+'temp.tif'
        print command_txt
        os.system(command_txt)
        for j in range(len(Param_list)):
            command_txt ='rm '+Haz_list[i][0]+'_'+Param_list[j]+'.tif'
            print command_txt
            os.system(command_txt)  
    os.system('rm color_haz.txt')
    os.system('rm HAZARDsingleband.tif')
    os.system('rm ' + VxDtif)
    os.system('rm ' + DEPtif)
    os.system('rm ' + VELtif)
    
    return()
    
def Extract_geotiff_from_SWW(filename):
    """
     INPUTS: swwFile -- name of sww file, OR a 3-column array with x/y/z
                    #points. In the latter case x and y are assumed to be in georeferenced
                    #coordinates.  The output raster will contain 'z', and will have a name-tag
                    #based on the name in 'output_quantities'.
                output_quantities -- list of quantitiies to plot, e.g.
                                #['depth', 'velocity', 'stage','elevation','depthIntegratedVelocity','friction']
                myTimeStep -- list containing time-index of swwFile to plot (e.g. [0, 10, 32] ) or 'last', or 'max', or 'all'
                CellSize -- approximate pixel size for output raster [adapted to fit lower_left / upper_right]
                lower_left -- [x0,y0] of lower left corner. If None, use extent of swwFile.
                upper_right -- [x1,y1] of upper right corner. If None, use extent of swwFile.
                EPSG_CODE -- Projection information as an integer EPSG code (e.g. 3123 for PRS92 Zone 3, 32756 for UTM Zone 56 S, etc). 
                             #Google for info on EPSG Codes
                proj4string -- Projection information as a proj4string (e.g. '+init=epsg:3123')
                 #Google for info on proj4strings. 
                velocity_extrapolation -- Compute velocity assuming the code extrapolates with velocity (instead of momentum)?
                min_allowed_height -- Minimum allowed height from ANUGA
                output_dir -- Write outputs to this directory
                bounding_polygon -- polygon (e.g. from read_polygon) If present, only set values of raster cells inside the bounding_polygon
                k_nearest_neighbours -- how many neighbours to use in interpolation. If k>1, inverse-distance-weighted interpolation is used
                creation_options -- list of tif creation options for gdal, e.g. ['COMPRESS=DEFLATE']    
    
    """
    timeSlices = 'max' # this can be time step number eg timestep 5, not the timestep in seconds
    min_allowed_height=0.01
    EPSG_CODE=28356 #EPSG_CODE=28356 is for UTM -56, codes for other locations search for EPSG_CODE on the web
    
    head, file = os.path.split(filename)
    print 'Opening  :', file

    CellSize=float(enterbox(msg='Enter Grid Size (m) to export'))
    print 'Grid (m) :', CellSize
    
    output_quantities=['depthIntegratedVelocity','depth', 'velocity']

    for i in output_quantities:
        print 'Quantity :', i
        # If Geotif Exists Could skip... else just do it !!!
        output_dir = os.path.join(os.path.dirname(filename),filename[:-4]+'_Flood_Hazard')
        #md = output_dir
        plot_utils.Make_Geotif(
		    swwFile=filename, 
		    output_quantities=[i], 
		    myTimeStep=timeSlices, 
		    CellSize=CellSize, 
		    velocity_extrapolation=True, 
		    min_allowed_height=min_allowed_height, 
            output_dir=output_dir,
		    EPSG_CODE=EPSG_CODE, 
		    verbose=False, 
		    k_nearest_neighbours=3)
    Create_Hazard_Map(filename,output_quantities,output_dir,timeSlices)
    
    return()


title = 'Select 100y sww file' 
default='/home/wcc/models/'
filename=fileopenbox(title, default=default, filetypes= '*.sww')    
Extract_geotiff_from_SWW(filename)


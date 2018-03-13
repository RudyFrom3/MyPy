""" This script is a compilation of many useful tools needed to
format data for use with ANUGA
"""

import sys
import os
import glob
import os.path
from easygui import *
from os.path import *
from anuga.utilities import plot_utils
from numpy import array, float, resize
from anuga.geospatial_data.geospatial_data import Geospatial_data


def Create_L_FRP_Map(pmffilename,quantities,output_dir,timeSlices):
    """
    This Function Takes reads a SWW file and processes them to create the Hazard MAP Layer based on 2016 procedure
    
    Use tips from:
    https://gis.stackexchange.com/questions/125202/gdal-clipping-a-raster-with-another-raster
    GDAL_Calc.py -A Mask.tif -B CutBigImageToClip.tif --outfile=SmallerFile.tif --NoDataValue=0 --Calc="B*(A>0)"
       
    """
    #print pmffilename
    #print output_dir
    VxDtif = os.path.join(output_dir,os.path.basename(pmffilename[:-4]+'_'+quantities[0]+'_'+timeSlices+'.tif'))
    DEPtif = os.path.join(output_dir,os.path.basename(pmffilename[:-4]+'_'+quantities[1]+'_'+timeSlices+'.tif'))
    VELtif = os.path.join(output_dir,os.path.basename(pmffilename[:-4]+'_'+quantities[2]+'_'+timeSlices+'.tif'))
    os.chdir(output_dir)

    # Set Up Criteria for Filtering Hazard
    Haz_list = []
    Haz_list.append(['L_FRP','>=0.1','>=0.1','>=0.1',1]) # Hazard, VxD, D, V, layer number

    Param_list = ['VxD','DEP','VEL']
    File_list = [VxDtif,DEPtif,VELtif]
    
    for i in range(len(Haz_list)): # Loop Through Criteria to Filter
        for j in range(len(Param_list)): # Loop through Parameters
            os.system('gdal_calc.py -A ' + File_list[j]+' --outfile='+Haz_list[i][0]+'_'+Param_list[j]+'.tif --calc="A*(A'+Haz_list[i][j+1]+')" --NoDataValue=0') #create individual VxD, D and V based on Haz_list
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'_'+Param_list[0]+'.tif -B '+Haz_list[i][0]+'_'+Param_list[1]+'.tif -C '+Haz_list[i][0]+'_'+Param_list[2]+'.tif --outfile='+Haz_list[i][0]+'temp.tif --calc="A+B+C " --NoDataValue=0')
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'temp.tif --outfile='+Haz_list[i][0]+'.tif --calc="'+str(Haz_list[i][4])+'*(A>0.001)" --NoDataValue=0')  #Combined Layers VxD, D, V

    # Merge to Create a Single tiff
    os.system('gdal_merge.py  L_FRP.tif -o HAZARDsingleband.tif')

    # Color table values..(Value, R, G,B, Opacity)
    color_table_file = open('color_haz_yellow.txt', 'w')
    color_table_file.write('0,white,0\n')
    color_table_file.write('1,yellow\n')
    color_table_file.close()
       
    os.system('gdaldem color-relief HAZARDsingleband.tif color_haz_yellow.txt L_FRP.tif')

    # Clean up Temp Files
    for i in range(len(Haz_list)):
        command_txt = 'rm '+Haz_list[i][0]+'temp.tif'
        print command_txt
        os.system(command_txt)
        for j in range(len(Param_list)):
            command_txt ='rm '+Haz_list[i][0]+'_'+Param_list[j]+'.tif'
            print command_txt
            os.system(command_txt)  
    os.system('rm color_haz_yellow.txt')
    os.system('rm HAZARDsingleband.tif')
    os.system('rm ' + VxDtif)
    os.system('rm ' + DEPtif)
    os.system('rm ' + VELtif)
    return()


def Create_M_FRP_Map(hundredyfilename,quantities,output_dir,timeSlices):
    """
    This Function Takes reads a SWW file and processes them to create the Hazard MAP Layer based on 2016 procedure
    
    Use tips from:
    https://gis.stackexchange.com/questions/125202/gdal-clipping-a-raster-with-another-raster
    GDAL_Calc.py -A Mask.tif -B CutBigImageToClip.tif --outfile=SmallerFile.tif --NoDataValue=0 --Calc="B*(A>0)"
       
    """
    #print hundredyfilename
    #print output_dir
    VxDtif = os.path.join(output_dir,os.path.basename(hundredyfilename[:-4]+'_'+quantities[0]+'_'+timeSlices+'.tif'))
    DEPtif = os.path.join(output_dir,os.path.basename(hundredyfilename[:-4]+'_'+quantities[1]+'_'+timeSlices+'.tif'))
    VELtif = os.path.join(output_dir,os.path.basename(hundredyfilename[:-4]+'_'+quantities[2]+'_'+timeSlices+'.tif'))
    os.chdir(output_dir)

    # Set Up Criteria for Filtering Hazard
    Haz_list = []
    Haz_list.append(['M_FRP','>=0.05','>=0.05','>=0.05',1]) # Hazard, VxD, D, V, layer number

    Param_list = ['VxD','DEP','VEL']
    File_list = [VxDtif,DEPtif,VELtif]
    
    for i in range(len(Haz_list)): # Loop Through Criteria to Filter
        for j in range(len(Param_list)): # Loop through Parameters
            os.system('gdal_calc.py -A ' + File_list[j]+' --outfile='+Haz_list[i][0]+'_'+Param_list[j]+'.tif --calc="A*(A'+Haz_list[i][j+1]+')" --NoDataValue=0') #create individual VxD, D and V based on Haz_list
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'_'+Param_list[0]+'.tif -B '+Haz_list[i][0]+'_'+Param_list[1]+'.tif -C '+Haz_list[i][0]+'_'+Param_list[2]+'.tif --outfile='+Haz_list[i][0]+'temp.tif --calc="A+B+C " --NoDataValue=0')
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'temp.tif --outfile='+Haz_list[i][0]+'.tif --calc="'+str(Haz_list[i][4])+'*(A>0.001)" --NoDataValue=0')  #Combined Layers VxD, D, V
   
    # turn M_FRP into M_FRPsingleband file
    os.system('gdal_merge.py  M_FRPtemp.tif -o M_FRPsingleband.tif')  
    # Create orange color table..(Value, R, G,B, Opacity)  
    color_table_file = open('color_haz_orange.txt', 'w')
    color_table_file.write('0,white,0\n')
    color_table_file.write('1,orange\n')
    color_table_file.close()      
    #change color of M_FRPsingleband file to orange 
    os.system('gdaldem color-relief M_FRPsingleband.tif color_haz_orange.txt M_FRP.tif')    
    
    # Clean up Temp Files
    for i in range(len(Haz_list)):
        command_txt = 'rm '+Haz_list[i][0]+'temp.tif'
        print command_txt
        os.system(command_txt)
        for j in range(len(Param_list)):
            command_txt ='rm '+Haz_list[i][0]+'_'+Param_list[j]+'.tif'
            print command_txt
            os.system(command_txt)  
    os.system('rm color_haz_orange.txt')
    os.system('rm M_FRPsingleband.tif')
    os.system('rm ' + VxDtif)
    os.system('rm ' + DEPtif)
    os.system('rm ' + VELtif)
    
    return()


def Create_H_FRP_Map(hundredyfilename,quantities,output_dir,timeSlices):
    """
    This Function Takes reads a SWW file and processes them to create the Hazard MAP Layer based on 2016 procedure
    
    Use tips from:
    https://gis.stackexchange.com/questions/125202/gdal-clipping-a-raster-with-another-raster
    GDAL_Calc.py -A Mask.tif -B CutBigImageToClip.tif --outfile=SmallerFile.tif --NoDataValue=0 --Calc="B*(A>0)"
       
    """
    #print hundredyfilename
    #print output_dir
    VxDtif = os.path.join(output_dir,os.path.basename(hundredyfilename[:-4]+'_'+quantities[0]+'_'+timeSlices+'.tif'))
    DEPtif = os.path.join(output_dir,os.path.basename(hundredyfilename[:-4]+'_'+quantities[1]+'_'+timeSlices+'.tif'))
    VELtif = os.path.join(output_dir,os.path.basename(hundredyfilename[:-4]+'_'+quantities[2]+'_'+timeSlices+'.tif'))
    os.chdir(output_dir)

    # Set Up Criteria for Filtering Hazard
    Haz_list = []
    Haz_list.append(['H_FRP','>=0.30','>=0.80','>=2.00',1])

    Param_list = ['VxD','DEP','VEL']
    File_list = [VxDtif,DEPtif,VELtif]
    
    for i in range(len(Haz_list)): # Loop Through Criteria to Filter
        for j in range(len(Param_list)): # Loop through Parameters
            os.system('gdal_calc.py -A ' + File_list[j]+' --outfile='+Haz_list[i][0]+'_'+Param_list[j]+'.tif --calc="A*(A'+Haz_list[i][j+1]+')" --NoDataValue=0') #create individual VxD, D and V based on Haz_list
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'_'+Param_list[0]+'.tif -B '+Haz_list[i][0]+'_'+Param_list[1]+'.tif -C '+Haz_list[i][0]+'_'+Param_list[2]+'.tif --outfile='+Haz_list[i][0]+'temp.tif --calc="A+B+C " --NoDataValue=0')
        os.system('gdal_calc.py -A '+Haz_list[i][0]+'temp.tif --outfile='+Haz_list[i][0]+'.tif --calc="'+str(Haz_list[i][4])+'*(A>0.001)" --NoDataValue=0')  #Combined Layers VxD, D, V

    # turn H_FRP into H_FRPsingleband file
    os.system('gdal_merge.py  H_FRPtemp.tif -o H_FRPsingleband.tif')      
    # Create a red color table..(Value, R, G,B, Opacity)
    color_table_file = open('color_haz_red.txt', 'w')
    color_table_file.write('0,white,0\n')
    color_table_file.write('1,red\n')
    color_table_file.close()
    #change color of H_FRPsingleband file to red 
    os.system('gdaldem color-relief H_FRPsingleband.tif color_haz_red.txt H_FRP.tif')     
    
    # Clean up Temp Files
    for i in range(len(Haz_list)):
        command_txt = 'rm '+Haz_list[i][0]+'temp.tif'
        print command_txt
        os.system(command_txt)
        for j in range(len(Param_list)):
            command_txt ='rm '+Haz_list[i][0]+'_'+Param_list[j]+'.tif'
            print command_txt
            os.system(command_txt)  
    os.system('rm color_haz_red.txt')
    os.system('rm H_FRPsingleband.tif')
    os.system('rm ' + VxDtif)
    os.system('rm ' + DEPtif)
    os.system('rm ' + VELtif)
    
    return()
    
    
def Extract_L_geotiff_from_SWW(pmffilename):
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
    
    head, file = os.path.split(pmffilename)
    print 'Opening  :', file
    
    output_quantities=['depthIntegratedVelocity','depth', 'velocity']

    for i in output_quantities:
        print 'Quantity :', i
        # If Geotif Exists Could skip... else just do it !!!
        output_dir = os.path.join(os.path.dirname(pmffilename),'Flood_Risk_Precincts')
        #md = output_dir
        plot_utils.Make_Geotif(
		    swwFile=pmffilename, 
		    output_quantities=[i], 
		    myTimeStep=timeSlices, 
		    CellSize=CellSize, 
		    velocity_extrapolation=True, 
		    min_allowed_height=min_allowed_height, 
            output_dir=output_dir,
		    EPSG_CODE=EPSG_CODE, 
		    verbose=False, 
		    k_nearest_neighbours=3)
    Create_L_FRP_Map(pmffilename,output_quantities,output_dir,timeSlices)
    
    return()
    
            
def Extract_M_geotiff_from_SWW(hundredyfilename):
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
    
    head, file = os.path.split(hundredyfilename)
    print 'Opening  :', file
    
    output_quantities=['depthIntegratedVelocity','depth', 'velocity']

    for i in output_quantities:
        print 'Quantity :', i
        # If Geotif Exists Could skip... else just do it !!!
        output_dir = os.path.join(os.path.dirname(hundredyfilename),'Flood_Risk_Precincts')
        #md = output_dir
        plot_utils.Make_Geotif(
		    swwFile=hundredyfilename, 
		    output_quantities=[i], 
		    myTimeStep=timeSlices, 
		    CellSize=CellSize, 
		    velocity_extrapolation=True, 
		    min_allowed_height=min_allowed_height, 
            output_dir=output_dir,
		    EPSG_CODE=EPSG_CODE, 
		    verbose=False, 
		    k_nearest_neighbours=3)
    Create_M_FRP_Map(hundredyfilename,output_quantities,output_dir,timeSlices)
    return()

def Extract_H_geotiff_from_SWW(hundredyfilename):
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
    
    head, file = os.path.split(hundredyfilename)
    print 'Opening  :', file

    output_quantities=['depthIntegratedVelocity','depth', 'velocity']

    for i in output_quantities:
        print 'Quantity :', i
        # If Geotif Exists Could skip... else just do it !!!
        output_dir = os.path.join(os.path.dirname(hundredyfilename),'Flood_Risk_Precincts')
        #md = output_dir
        plot_utils.Make_Geotif(
		    swwFile=hundredyfilename, 
		    output_quantities=[i], 
		    myTimeStep=timeSlices, 
		    CellSize=CellSize, 
		    velocity_extrapolation=True, 
		    min_allowed_height=min_allowed_height, 
            output_dir=output_dir,
		    EPSG_CODE=EPSG_CODE, 
		    verbose=False, 
		    k_nearest_neighbours=3)
    Create_H_FRP_Map(hundredyfilename,output_quantities,output_dir,timeSlices)
    return()

hundredyfilename=fileopenbox(title = 'Select 100y sww file' , default='/home/wcc/models/', filetypes= '*.sww')    
pmffilename=fileopenbox(title='Select PMF sww file' , default='/home/wcc/models/', filetypes= '*.sww')    
CellSize = float(enterbox(msg='Enter Grid Size (m) to export')) 
Extract_L_geotiff_from_SWW(pmffilename)
Extract_M_geotiff_from_SWW(hundredyfilename)
Extract_H_geotiff_from_SWW(hundredyfilename)
  

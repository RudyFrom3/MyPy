"""

Attempt to build GENERAL Tool to plot and extract ANUGA results:
Built on code developed by 
Gareth Davies, Hydrodynamic Modeller, Community Safety Group
Community Safety and Earth Monitoring Division;GEOSCIENCE AUSTRALIA

Example code to plot sww file interactively

Ideally this may one day have a GUI with richer features, but for now easygui is being used.

Consider how to plot Current Hazard maps:

H6 VxD > 4.0
H5 D < 4.0 & V < 4.0 & VxD <= 4.0
H4 D < 2.0 & V < 2.0 & VxD <= 1.0
H3 D < 1.2 & V < 2.0 & VxD <= 0.6
H2 D < 0.5 & V < 2.0 & VxD <= 0.6
H1 D < 0.3 & V < 2.0 & VxD <= 0.3
To do this need three Grids in Numpy Arrays
H6 = VxD > 4.0
Union of D array, V array and vxD array for:



"""
MainMenulistChoices = ["1a_Get_SWW_FILE1",
                   "1b_Get_SWW_FILE2",
                   "2_Get_SWW_FILES_DIR",
                   "3_Get_Point_Location_FILE",
                   "4_Get_Gauge_Locations_FILE",
                   "5_Get_XS_Files_DIR",
                   "6_Get_Profile_Poly_file",
                   "7_Set_Plot_Format_png_svg",
 
 
                   "A_Plot_Elevation",
                   "B_Plot_Elevation_2_Range",
                   "C_Plot_Stage_Max for all loaded SWWs",
                   "D_Plot_Stage_Difference_ for SWW1 and SWW2",
                   "E_Plot_VEL_at_Time_seconds(Not vectors)",
                   "F_Plot_VEL_Vectors_at_Time",
                   "G_Add_Max_VEL_To_Plot",
                   "H_Plot_Water_VOL_over_time",
                   "I_Plot_timeseries_at_point",
                   "J_Plot_timeseries_at_pts",
                   "K_Plot_muliple_SWW_TS_at_pts",
                   "L_Plot_Stage_Along_Poly",
                   "M_Plot_Q_at_ALL_Cross Section_Polys_in_DIR",
                   "N_MAKE_GEOTIFF",
                   
                   
                   "Z-EXIT"]
# =================  IMPORT OTHER MODULES ===========================================
import os
import glob
from easygui import *
from anuga.utilities import plot_utils as util
import scipy
import numpy
from matplotlib import pyplot as pyplot
from anuga.geometry.polygon import read_polygon, plot_polygons, polygon_area


# ============ DEFINE CLASS TO STORE PERSISTENT SETTINGS======================================
class Settings(EgStore):

    def __init__(self, filename):  # filename is required
        #-------------------------------------------------
        # DEFINE THE VARIABLES TO STORE
        #-------------------------------------------------
        self.Last_SWW_File1_Used = ""
        self.Last_SWW_File2_Used = ""
        self.Last_SWW_DIR = ""
        self.Last_Point_Loc_File = ""
        self.Last_Gauge_File_Used = ""        
        self.Last_XSFilesDIR_Used = ""
        self.Last_Profile_Line_Used = ""
        self.Last_Plot_format_used = ""

        #-------------------------------------------------
        # For subclasses of EgStore, these must be
        # the last two statements in  __init__
        #-------------------------------------------------
        self.filename = filename  # this is required
        self.restore()            # restore values from the storage file if possible
# ============ DEFINE CLASS TO STORE PERSISTENT SETTINGS======================================

# ----------------------------------------------------------------------------------------   

def BearingDistance(dX,dY):
    """
    This Routine gets distances in X and Y and Calculates the Bearing Distance
    """
    import math
    if dX == 0.0 and dY == 0.0:
        Bearing = 0.0
        Dist = 0.0
        direction = 'Same Point'
    elif dX == 0 and dY > 0:
        direction = 'S-N'
        Bearing = 360.0
        Dist = math.sqrt(dX**2+dY**2)
    elif dX == 0 and dY < 0:
        direction = 'N-S'
        Bearing = 180.0
        Dist = math.sqrt(dX**2+dY**2)
    elif dX > 0 and dY == 0:
        direction = 'W-E'
        Bearing = 90.0
        Dist = math.sqrt(dX**2+dY**2)
    elif dX < 0 and dY == 0:
        direction = 'E-W'
        Bearing = 270.0
        Dist = math.sqrt(dX**2+dY**2)
    elif dX > 0 and dY > 0:
        direction = 'Q1'
        Bearing = 90-math.degrees(math.atan(dY/dX))
        Dist = math.sqrt(dX**2+dY**2)
    elif dX > 0 and dY < 0:
        direction = 'Q2'
        Bearing = 90-math.degrees(math.atan(dY/dX))
        Dist = math.sqrt(dX**2+dY**2)
    elif dX < 0 and dY < 0:
        direction = 'Q3'
        Bearing = 270-math.degrees(math.atan(dY/dX))
        Dist = math.sqrt(dX**2+dY**2)
    elif dX  < 0 and dY > 0:
        direction = 'Q4'
        Bearing = 270-math.degrees(math.atan(dY/dX))
        Dist = math.sqrt(dX**2+dY**2)
    return(Bearing,Dist)

# ----------------------------------------------------------------------------------------
def check_SWW_with_ncdump(swwFile):
    """
    Identifies the contents of a SWW file...
    
    Can also do it with the "p=util.get_output" method to read in the sww, 
    you can then look at the dimensions of each variable to see if they are time dependent.
    For example, p.elev.shape will give the dimensions of elevation [1 dimensional], 
    and this will differ from p.stage.shape [2 dimensional]
    Note that "shape" is a basic numpy operation.....
    
    Try googling:
    scipy tutorial
    or
    python for scientists
    or
    numpy tutorial
        
    """
    import subprocess
    import re
    
    cmd_req = "ncdump "+"-c "+swwFile
    print cmd_req
    proc = subprocess.Popen([cmd_req], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print "program output:", out
    TS_search_Start = out.find('number_of_timesteps')
    TS_search_End =  out.find('variables:')
    s1 = out[TS_search_Start:TS_search_End]
    print s1
    #print int(re.match(r'\d+', s).group())
    s2 = ''.join(x for x in s1 if x.isdigit())
    print s2
    Num_TS = int(s2)-1
    Ver_search_Start = out.find('revision_number')
    Ver_search_End =  out.find(':starttime ')
    print out[Ver_search_Start:Ver_search_End]
    # Check for friction_c  on Centroids
    try:
        Fric_C_search = out.find('friction_c')
        print 'Found Centroid friction'
        Fric_C = True
    except:
        print 'No Centroid friction Found'
        Fric_C = False
    # Check for friction on Vertices
    try:
        Fric_search =  out.find('friction')
        print 'Found friction on vertices'
        Fric_V = True
    except:
        print 'No Vertex friction Found'
        Fric_V = False
    return(Num_TS,Fric_C,Fric_V)
#-------------------------------------------------------------------------

def Select_TS(Time_step_List):
    # Little function to select Time Step
    message = "Select a Time Step to determine what time to plot the Variable."
    TS_Selected = choicebox(message,"SELECT a Time Step for Plotting...", Time_step_List)
    TS_Selected = float(TS_Selected)
    print 'Selected Time Step'
    print TS_Selected
    return(TS_Selected)
#-------------------------------------------------------------------------

def Select_Plot_Format():
    """
    MatPlot Lib can save in several formats
    including
    ['eps','jpg','pdf','png','ps','svg']
    
    """
    # Little function to select Time Step
    message = "Select the preferred format for saving the Plotted output."
    Plot_formats_Avail = ['.eps','.jpg','.pdf','.png','.ps','.svg']
    Plot_Format = choicebox(message,"SELECT PLOT FORMAT...", Plot_formats_Avail)
    print 'Selected Plot Format to use...'
    print Plot_Format
    return(Plot_Format)
#--------------------------------------------------------------------------

def get_plot_variable(p,p2 ):
    """
    This function will select the variable name to be plotted
    
    """
    # Let user select what to plot ....

    plotChoices = ["A_Plot_Elevation",
       "B_Plot_Stage_Max",
       "C_Plot_Velocity",
       "D_Plot_Depth",          
       "E_Plot_Momentum",     
       "F_Plot_Friction",     
       "G_Plot_Froude",     
       "H_Velocity_and_Direction",
       "I_Momentum_and_Direction",
       "Z-EXIT"]
    
    message = "Select the Variable to Export from to time series File."
    plotreply = choicebox(message,"SELECT EXPORT Variable(s)...", plotChoices)
    select_plot = True
    if plotreply == "A_Plot_Elevation":
        #plot_variable = p2.elev #Elevation   Why does it not plot elevation  using p2 ???? Remember to set to domain.set_quantities_to_be_stored({'elevation': 2,.....
        plot_variable = p.elev #Elevation   Why does it not plot elevation ???? Remember to set to domain.set_quantities_to_be_stored({'elevation': 2,.....
        plot_type = 'PLOT ELEVATION at '
        plt_file_nm = 'elev_'
        y_axis_label = 'Ground Elevation (m AHD)'
        color = 'sienna'
        linewidth = 3.0
    elif plotreply == "B_Plot_Stage_Max":
        plot_variable = p2.stage #,max(axis=0) #Stage
        plot_type = 'PLOT STAGE at '
        plt_file_nm = 'stage_'
        y_axis_label = 'Stage {Flood Level} (m AHD)'
        color = 'blue'
        linewidth = 2.0
    elif plotreply == "C_Plot_Velocity":
        plot_variable = p2.vel #Velocity
        plot_type = 'PLOT VELOCITY at '
        plt_file_nm = 'vel_'
        y_axis_label = 'Velocity (m2/s)'
        color = 'orange'
        linewidth = 3.0
    elif plotreply == "D_Plot_Depth":
        plot_variable = p2.stage-p2.elev #Depth
        plot_type = 'PLOT DEPTH at '
        plt_file_nm = 'depth_'
        y_axis_label = 'Flood Depth (m)'              
        color = 'teal'
        linewidth = 4.0
    elif plotreply == "E_Plot_Momentum":
        plot_variable = (p2.xmom**2 + p2.ymom**2)**0.5 #Momentum   '(xmomentum**2 + ymomentum**2)**0.5'
        plot_type = 'PLOT MOMENTUM at '       
        plt_file_nm = 'Mom_'
        y_axis_label = 'Momentum (m2/s)'
        color = 'purple'
        linewidth = 3.0
    elif plotreply == "F_Plot_Friction":
        plot_variable = p2.friction #Friction
        plot_type = 'PLOT FRICTION at '       
        plt_file_nm = 'fric_'
        y_axis_label = 'Friction (Manning)'
        color = 'grey'
        linewidth = 2.0
    elif plotreply == "G_Plot_Froude":
        plot_variable = (p2.xmom**2 + p2.ymom**2)**0.5/(p2.stage-p2.elev+1.e-30)/(9.81*(p2.stage-p2.elev+1.e-4))**0.5  #Froude Number
        plot_type = 'PLOT FROUDE at '       
        plt_file_nm = 'Fr_'
        y_axis_label = 'Froude'
        color = 'magenta'
        linewidth = 2.0
    elif plotreply == "H_Velocity_and_Direction":
        plot_variable = p2.vel #Velocity
        plot_type = 'PLOT Velocity and Direcion at '       
        plt_file_nm = 'VelD_'
        y_axis_label = 'Velocity and Direction'    
        color = 'magenta'
        linewidth = 2.0
    elif plotreply == "I_Momentum_and_Direction":
        plot_variable = p2.vel #Velocity
        plot_type = 'PLOT Momentum and Direcion at '       
        plt_file_nm = 'MomD_'
        y_axis_label = 'Momentum and Direction'    
        color = 'purple'
        linewidth = 2.0
    elif plotreply == "Z-EXIT":
        plot_variable = ''
        plot_type = ''       
        plt_file_nm = ''
        y_axis_label = ''
        select_plot = False
        color='black'
        linewidth = 1.0
    # END IF
    return(plotreply,plot_variable,plot_type,plt_file_nm,y_axis_label,select_plot,color,linewidth)
    
#-----------------------------------------------------------------------------------------    

def get_gauge_loc_and_labels(Gauge_file):
    #Gauge_file =fileopenbox(msg="Select Gauge File\n\nPick File with Location Data."   # HERE IS THE FILE OPEN BOX FOR GUI
    #        ,title="Select Gauge location file to Extract Results to Timeseries"
    #        ,filetypes = ["*.csv" ],default = Last_dir_used+'/*.csv') 
    infid = open(Gauge_file,'r')

    """   GAUGE FILE FORMAT LOOKS LIKE THIS
    name,easting,northing,elevation
    Roadway,307085.917,6189077.542,13
    
    """
    print 'This routine Expects a Header in the File.... NAME, X,Y,Z... etc'
    lines = infid.readlines()[1:] # Skip Header Line.... Or read it to use as part of LAbel ...
    infid.close()
    try:
        Last_Gaug_used_Ptr = open('01_Gauge_Last_Used.csv','w')
        Last_Gaug_used_Ptr.write(Gauge_file)
        Last_Gaug_used_Ptr.close()
    except:
        print 'No File found...'
        
    #raw_input('File now Open...Continue..') 
    # Format is: Label, X, Y... Z optional
    x0s = []
    y0s=[]
    labels = []
    # There is a p.xllcorner and p.yllcorner -- add those to the p.x,p.y coords in the sww to get the georef coords 
    for line in lines:
        print line
        fields = line.split(',')
        x0s.append(float(fields[1])-p2.xllcorner) # Ensure reads Local Co-ords
        y0s.append(float(fields[2])-p2.yllcorner)
        labels.append(fields[0])
    print x0s
    print y0s
    print labels    
    return(x0s,y0s,labels)

#-------------------------------------------------------------

def get_XS_loc_and_labels(Last_dir_used):
    XS_file =fileopenbox(msg="Select XS File\n\nPick File with Location Data."   # HERE IS THE FILE OPEN BOX FOR GUI
            ,title="Select XS location file to Extract Results to Hydrograh"
            ,filetypes = ["*.csv" ],default = Last_dir_used+'/*.csv') 
    infid = open(XS_file,'r')

    """   GAUGE FILE FORMAT LOOKS LIKE THIS
    easting,northing,name,elevation
    307085.917,6189077.542,Roadway,13
    """
    lines = infid.readlines()[1:] # Skip Header Line.... Or read it to use as part of LAbel ...
    infid.close()
    try:
        Last_Gaug_used_Ptr = open('01_XS_Last_Used.csv','w')
        Last_Gaug_used_Ptr.write(XS_file)
        Last_Gaug_used_Ptr.close()
    except:
        print 'No File found...'
        
    #raw_input('File now Open...Continue..') 
    
    XS_label = os.path.basename(XS_file)
    
    return(XS_file,XS_label)

#------------------------------------------------------------------   

def Extract_SWW_Data(swwFile):
    #import numpy
    # ========= EXTRACT DATA FROM AN SWW FILE=====================
    print 'Now extract data...'          
    p=util.get_output(swwFile)  # Gets Output including elevations (time series if set to 2)
    print 'Centroid Array...'
    print p.stage.shape
    p2=util.get_centroids(p,velocity_extrapolation=True) # gets Centroid Output....
    print 'Vertices Array ....'
    print p2.stage.shape
    print 'Got SWW and Centroid data...'
    Model_TS = p.time[1]
    Num_TS,Fric_C,Fric_V = check_SWW_with_ncdump(swwFile)
    print 'Total Model Time = '+str(Model_TS*Num_TS)
    print 'Number of time steps = ',str(Num_TS)
    Time_step_List = []
    for TS in xrange(Num_TS):
        Time_step_List.append(Model_TS*TS)
    return(p,p2,Model_TS,Num_TS,Fric_C,Fric_V,Time_step_List)
    
    
# ============ DEFINE FUNCTIONS FOR USE IN THIS SCRIPT ======================================
def plot_Q_at_XS(time,Q,SWW_file,Location):

    """
    
    """
    #from pylab import ion, plot
    from os.path import basename
    from numpy import argmax

    if abs(min(Q)) > max(Q): Q =[i * -1.0 for i in Q]
    # Ole How can we also Print this info into a Text File so we get a two Columns.... Time, Q
    #outfile = open('test.txt', 'w')
    #outfile.write(time,Q)
    #hybrid_filename=
    
    #outfile_name= SWW_file[0:-4]+'_'+basename(XS_Location_file[0:-4])
    outfile_name= SWW_file[0:-4]+'_'+Location

    #Time at MaxQ  if an array use numpy.argmax .... if a list use index(max(Q))
    flow_index = argmax(Q)
    #pyplot.ion()
    pyplot.clf() # Clear any Previous Plots...
    pyplot.suptitle('Flow at '+basename(outfile_name))
    pyplot.title('Max Q = %7.3f(m3/s) at T: %10.1f(sec)' %(max(Q),time[flow_index]))
    pyplot.ylabel('Flow over Cross Section (m3/s)')
    pyplot.xlabel('Model Time (Seconds)')
    pyplot.plot(time, Q,color = 'darkblue', linewidth = 2.5)  # Plot the Time Series
    pyplot.savefig(outfile_name+'_Qplot'+Last_Plot_format_used )
    #raw_input('Plot done  Check location !!') 
    return() 


def read_XSdir_plot(swwfile,XS_directory, filepattern='*.csv'):
    """
    """
    from anuga.shallow_water.sww_interrogate import get_flow_through_multiple_cross_sections
    pattern = os.path.join(XS_directory, filepattern)
    files = glob.glob(pattern)    
    result = []  
    count = 0
    #print 'Open Location Files....'
    locations = []
    for f in files:  
        count+=1
        result.append(read_polygon(f))
        locations.append(os.path.basename(f).split('.')[0]) # List of Location Labels
    polylines=result # All the Poly Lines
    time, Qlist = get_flow_through_multiple_cross_sections(swwfile, polylines, verbose=True)
    # Time is recorded once and the Q is stored for each Poly in a list (so its a list of list)
    #print Qlist[0]
    #print time
    #raw_input('check...')	
    for i in range(count):
        outname = "Q_extract_%s.csv"% str(locations[i])
        f = open(outname, 'w')
        f.write('time,Q\n')
        #print 'Write output to file '+outname
        #for (t,Q) in zip(time,Qarray):
        #for (t,Q) in zip(time,Qlist):
        #    f.write('%s,%s\n' % (str(t), str(Q)))
        #print 'Elements...'+str(len(time))  # Number of time steps.....
        for t in range(len(time)):
            #print t
            f.write('%s,%s\n' % (str(time[t]), str(Qlist[i][t])))   # Check which element counter to use...
        plot_Q_at_XS(time,Qlist[i],swwfile,locations[i])
        f.close()
    return()
    
    
# =============================== MAIN LINE CODE =============================================    

print 'Start INTERACTIVE ROUTINES....'
#-----------------------------------------------------------------------
#  DEFINE SETTINGS FILE and RESTORE DEFINED VARIABLES FOR USE
#-----------------------------------------------------------------------
settingsFile = "01_Interactive_Plotting_Settings.txt"
settings = Settings(settingsFile)
settings.restore() # Read from the Settings File...



#-----------------------------------------------------------------------

# Set plotting to 'interactive'
pyplot.ion()

Keep_Plotting = True
DATA1_EXTRACTED = False
GAUGES_DATA1_EXTRACTED = False
while Keep_Plotting:
    # Check Last used files ???
    settings.restore()
    Last_SWW_File1_Used = settings.Last_SWW_File1_Used 
    Last_SWW_File2_Used = settings.Last_SWW_File2_Used 
    Last_SWW_DIR = settings.Last_SWW_DIR
    Last_Point_Loc_File = settings.Last_Point_Loc_File
    Last_Gauge_File_Used = settings.Last_Gauge_File_Used
    Last_XSFilesDIR_Used = settings.Last_XSFilesDIR_Used
    Last_Profile_Line_Used = settings.Last_Profile_Line_Used
    Last_Plot_format_used  = settings.Last_Plot_format_used 
    
    if Last_Gauge_File_Used == None:Last_Gauge_File_Used = 'None'
    
    print Last_SWW_File1_Used
    print Last_SWW_File2_Used
    print Last_SWW_DIR
    print Last_Point_Loc_File
    print Last_Gauge_File_Used
    print Last_XSFilesDIR_Used
    print Last_Profile_Line_Used 
    print '-----------------------------'
    mess0 = ' PREVIOUS FILES AND PARAMETERS USED and SET by the Last User....\n'
    mess01= ' ---------------------------------------------------------------\n'
    mess1 = 'Last SWW file1 Used: '+Last_SWW_File1_Used +'\nLast SWW file2 Used: '+Last_SWW_File2_Used +'\nLast Multi-SWW DIR: '+Last_SWW_DIR+'\nLast 1 Point File: '+Last_Point_Loc_File+'\n'
    mess2 = 'Last Multi-Pt Gauge file: '+Last_Gauge_File_Used+'\nLast XS FileDIR Used :'+Last_XSFilesDIR_Used+'\nLast Profile Files Used :'+Last_Profile_Line_Used+'\n'
    mess3 = 'Last Plot Format Used: '+Last_Plot_format_used 
    message = mess0+mess01+mess1+mess2+mess3
       
    reply = choicebox(message,"A N U G A   O U T P U T   E X T R A C T I O N   T O O L   M E N U", MainMenulistChoices) # THIS IS MAIN MENU !!!!
    print reply, Keep_Plotting
    #raw_input('Check reply...')
    Last_single_SWW_dir_used = os.path.basename(Last_SWW_File1_Used )
    if reply == None: pass
    else:
        if reply == 'Z-EXIT':  # exit
            Keep_Plotting = False
        elif reply == "1a_Get_SWW_FILE1":
            print 'Go get a sww.... open a file....'
            Last_SWW_File1_Used = fileopenbox(msg="OPEN ANUGA SWW file for Depth Integrate "   # HERE IS THE FILE OPEN BOX FOR GUI
                                             ,title="Get SWW FiLE (need centroid and vertex ?)"
                                             ,filetypes = ["*.sww" ],default = settings.Last_SWW_File1_Used )
            settings.Last_SWW_File1_Used  = Last_SWW_File1_Used                                  
            settings.store()
            # GO EXTRACT SWW DATA--------------------------------------------------------
            p,p2,Model_TS,Num_TS,Fric_C,Fric_V,Time_step_List = Extract_SWW_Data(Last_SWW_File1_Used )
            DATA1_EXTRACTED = True
            # GOT EXTRACTED  DATA--------------------------------------------------------
            
        elif reply == "1b_Get_SWW_FILE2":
            print 'Go get a sww.... open a file....'
            Last_SWW_File2_Used = fileopenbox(msg="OPEN ANUGA SWW file for Depth Integrate "   # HERE IS THE FILE OPEN BOX FOR GUI
                                             ,title="Get SWW FiLE (need centroid and vertex ?)"
                                             ,filetypes = ["*.sww" ],default = settings.Last_SWW_File1_Used )
            settings.Last_SWW_File2_Used  = Last_SWW_File2_Used                                  
            settings.store()
            # GO EXTRACT SWW 2 DATA--------------------------------------------------------
            # This is for a 2nd SWW file
            #p,p2,Model_TS,Num_TS,Fric_C,Fric_V,Time_step_List = Extract_SWW_Data(Last_SWW_File2_Used )
            DATA2_EXTRACTED = True
            # GOT EXTRACTED  DATA--------------------------------------------------------
        elif reply == "2_Get_SWW_FILES_DIR":
            print 'Go get a SWW DIR....'
        elif reply == "3_Get_Point_Location_FILE":
            print 'Go get a Point Location File'
        elif reply == "2_Get_SWW_FILES_DIR":
            print 'Go get a SWW DIR....'
        elif reply == "4_Get_Gauge_Locations_FILE":
            print 'Go get a Gauge Location file....'
            msg = "Select Gauge File\n\nPick File with Location Data."
            title="Select Gauge location file to Extract Results to Timeseries"
            default = settings.Last_Gauge_File_Used
            
            Gauge_file =fileopenbox(msg=msg,title=title,filetypes = ["*.csv" ],default = default)
            #x0s,y0s,labels,Gauge_file = get_gauge_loc_and_labels(os.path.basename(Last_Gauge_File_Used))
            #GAUGES_DATA1_EXTRACTED = True
            settings.Last_Gauge_File_Used = Gauge_file
            settings.store()
        elif reply == "5_Get_XS_Files_DIR":
            print 'Go get a XS Files DIR....'
            title = "Go get a XS Files DIR...."
            msg = "Pick the directory that you wish to open."
            default = settings.Last_XSFilesDIR_Used
            Last_XSFilesDIR_Used = diropenbox(msg, title,default)
            settings.Last_XSFilesDIR_Used = Last_XSFilesDIR_Used
            settings.store()
    
        elif reply == "6_Profile_Poly_file":
            print 'Go get a Profile Poly file...'            


        elif reply == "7_Set_Plot_Format_png_svg":
            settings.Last_Plot_format_used = Select_Plot_Format()




        elif reply == "A_Plot_Elevation":
            ## Plot of elevation data -- can zoom around 
            # ADJUST COORDINATES TO SPATIAL COORDINATE SYSTEM
            print 'About to "Plot_Elevation'
            # Scale Dots based on the length of the diagonal 
            diag_len = ((max(p2.x)-min(p2.x))**2 +(max(p2.y)-min(p2.y)**2))**0.5
            print 'Diagonal Length = '+str(diag_len)
            s = diag_len/100
            pyplot.title('ELEVATION PLOT')
            pyplot.scatter(p2.x+p.xllcorner,p2.y+p.yllcorner,
                           c=p2.elev,edgecolors='none', s=s)  # s was 100
            pyplot.gca().set_aspect('equal') # Aspect ratio = 1
            pyplot.colorbar()
            
        elif reply == "B_Plot_Elevation_2_Range":
            # Change the display of elevation to be between -100 and + 100
            newElev=p2.elev*(p2.elev> - 100.) + (-100.)*(p2.elev <= -100.)
            newElev=newElev*(newElev < 100.) + 100.*(newElev >=100.)
            .0
            # Plot
            pyplot.clf()
            pyplot.scatter(p2.x+p.xllcorner,p2.y+p.yllcorner,
                           c=newElev,edgecolors='none', s=100)
            pyplot.gca().set_aspect('equal') # Aspect ratio = 1
            pyplot.colorbar()
            
        elif reply == "C_Plot_Stage_Max":
            # Change to display Maximum stage 
            
            stageAfterEq=p2.stage.max(axis=0) - p2.elev
            #stageAfterEq=p2.stage[10,:]*(p2.elev<0.)
            pyplot.clf()
            pyplot.scatter(p2.x+p.xllcorner,p2.y+p.yllcorner,
                           c=stageAfterEq,edgecolors='none', s=5) # Pixel Sise = s
            pyplot.gca().set_aspect('equal') # Aspect ratio = 1
            pyplot.colorbar()
        elif reply == "D_Plot_Stage_Difference_ for SWW1 and SWW2":
            # Change to display Maximum stage 
            p1b = util.get_centroids(Last_SWW_File1_Used)
            p2b = util.get_centroids(Last_SWW_File2_Used)
            p1b_max = p1b.stage.max(axis = 0)
            p2b_max = p2b.stage.max(axis = 0)
            peak_stage_diff = p1b_max - p2b_max
            
            #stageAfterEq=p2.stage[10,:]*(p2.elev<0.)
            pyplot.clf()
            pyplot.scatter(p2b.x+p2b.xllcorner,p2b.y+p2b.yllcorner,
                           c=peak_stage_diff,edgecolors='none', s=5) # Pixel Sise = s
            pyplot.gca().set_aspect('equal') # Aspect ratio = 1
            pyplot.colorbar()
            
        elif reply == "E_Plot_VEL_at_Time_seconds(Not vectors)":
            # Change to plot velocity at chosen timestep
            keep_running = True    
            
            while keep_running == True: # ===== OPTION TO PROCESS MORE DIRECTORIES ======================================
                print 'Get TS...'
                TS_User = Select_TS(Time_step_List)
                #TS_User = int(Select_TS(Time_step_List))/Model_TS
                print TS_User
                
                myInd=(p2.time==TS_User).nonzero()
                pyplot.clf()
                pyplot.scatter(p2.x+p.xllcorner,p2.y+p.yllcorner,
                           c=p2.vel[myInd,:],edgecolors='none', s=10)
                pyplot.gca().set_aspect('equal') # Aspect ratio = 1
                pyplot.colorbar()
                
                title = "Run AGAIN"
                msg = "Select another Time Step to Plot?"
                keep_running = ynbox(msg, title)
            
        elif reply == "F_Plot_VEL_Vectors_at_Time":
            ## Vector plot of velocity on top of elevation data
            #
            keep_running = True    
            while keep_running == True: # ===== OPTION TO PROCESS MORE DIRECTORIES ======================================
                TS_User = int(Select_TS(Time_step_List))/Model_TS   # Time Step not in Time but Steps
                print TS_User
                pyplot.clf() # Clear plot
                # Scatterplot -- larger s = larger points
                pyplot.scatter(p2.x+p.xllcorner,p2.y+p.yllcorner,
                               c=p2.elev,edgecolors='none',s=30)
                pyplot.gca().set_aspect('equal') # Aspect ratio = 1
                
                # Velocity vector plot -- smaller scale == larger arrows
                pyplot.quiver(p2.x+p.xllcorner,p2.y+p.yllcorner,
                              p2.xvel[TS_User,:], p2.yvel[TS_User,:], 
                              scale=0.1, scale_units='xy',
                              color='black')
                """
                ts=45 
                # Velocity vector plot -- smaller scale == larger arrows
                pyplot.quiver(p2.x+p.xllcorner,p2.y+p.yllcorner,
                              p2.xvel[ts,:], p2.yvel[ts,:], 
                              scale=0.0006, scale_units='xy',
                              color='red')
                """
                title = "Run AGAIN"
                msg = "Select another Time Step to Plot?"
                keep_running = ynbox(msg, title)

        elif reply == "G_Add_Max_VEL_To_Plot":
            ## Get max velocity, and add this to the plot
            #
            velMaxInd=p2.vel.argmax(axis=0) # Index of max velocity
            # Extract max velocity using a loop
            xvelMax=velMaxInd*0. 
            yvelMax=velMaxInd*0.
            for i in range(len(velMaxInd)):
                xvelMax[i]=p2.xvel[velMaxInd[i],i]
                yvelMax[i]=p2.yvel[velMaxInd[i],i]
            
            pyplot.clf()
            pyplot.scatter(p2.x+p.xllcorner,p2.y+p.yllcorner,
                           c=p2.elev,edgecolors='none',s=30)
            pyplot.gca().set_aspect('equal') # Aspect ratio = 1
            pyplot.quiver(p2.x+p.xllcorner, p2.y+p.yllcorner,
                          xvelMax, yvelMax,scale=0.001, scale_units='xy',
                          color='blue')
            pyplot.gca().set_aspect('equal') # Aspect ratio = 1
            # Add triangles to plot (can be slow)
            #util.plot_triangles(p, adjustLowerLeft=True)
            
        elif reply == "H_Plot_Water_VOL_over_time":
            ## Get the volume of water in the domain over time
            waterVol=util.water_volume(p,p2)
            pyplot.clf()
            pyplot.suptitle('TOTAL WATER VOLUME ON THE DOMAIN',fontsize=20)
            pyplot.title('Max: '+str(max(waterVol)),fontsize=14)
            pyplot.plot(p.time, waterVol)
            pyplot.xlabel('Time (s)')
            pyplot.ylabel('Water Volume (m^3)')
            
        elif reply == "I_Plot_timeseries_at_point":
            ## Plot a timeseries at a point
            # x0, y0 in 'INTERNAL ANUGA COORDINATE SYSTEM'
            x0=205000.
            y0=28000.
            # Find index of centroid nearest this point
            myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
            pyplot.clf()
            pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
            # Compare with a point 2000m north
            myInd=( (p2.x-x0)**2+(p2.y-(y0+2000.))**2).argmin()
            pyplot.plot(p2.time, p2.stage[:, myInd], '-o',color='red')
            # What are it's neighbouring triangle indices?
            util.find_neighbours(p,myInd)
            
        elif reply == "J_Plot_timeseries_at_pts":
            ## Batch plotting get the file containing multiple gauge points
            
            output_dir = os.path.dirname(Last_SWW_File1_Used )
            print output_dir
            if DATA1_EXTRACTED == False:
                # Extract Data from SWW
                p,p2,Model_TS,Num_TS,Fric_C,Fric_V,Time_step_List = Extract_SWW_Data(Last_SWW_File1_Used )
                DATA1_EXTRACTED == True
            if GAUGES_DATA1_EXTRACTED == False:
                #settings.Last_Gauge_File_Used = Gauge_file
                print 'Gauge File : '+Last_Gauge_File_Used
                x0s,y0s,labels= get_gauge_loc_and_labels(Last_Gauge_File_Used)
                print 'Labels: '
                print labels
                GAUGES_DATA1_EXTRACTED = True    
            # Let user select what to plot ....
            select_plot = True
            while select_plot:
                plotreply ,plot_variable,plot_type,plt_file_nm,y_axis_label,select_plot,color,linewidth = get_plot_variable(p,p2)
                print plotreply
                print x0s
                if plotreply == "Z-EXIT" : pass
                
                else: # WANT TO PLOT SOMETHING.....
					
                    for i in range(len(x0s)): # Multiple location points in 1 sww
                        print 'Gauge Number and Total Number of Gauge Locations..'
                        print y_axis_label
                        print i, len(x0s),labels[i]
                        pyplot.clf()
                        
                        if  plt_file_nm == 'elev_': # Plot the Time Chnaginig elevation  Need an error trap if elevation only singular ??
                            myInd = ((p.x-x0s[i])**2+(p.y-y0s[i])**2).argmin()
                            maxy = max(plot_variable[:, myInd])
                            indexy = plot_variable[:, myInd].tolist().index(maxy) # i will return index of 2
                            peak_time =p.time[indexy]
                            pyplot.plot(p.time, plot_variable[:, myInd], '-', color=color,linewidth = linewidth)
                        else:
                            myInd=((p2.x-x0s[i])**2+(p2.y-y0s[i])**2).argmin()
                            maxy = max(plot_variable[:, myInd])
                            indexy = plot_variable[:, myInd].tolist().index(maxy) # i will return index of 2
                            peak_time =p2.time[indexy]
                            pyplot.plot(p2.time, plot_variable[:, myInd], '-', color=color,linewidth = linewidth)
                        if plt_file_nm == 'VelD_':
                            # Add arrows
                            print 'Try to plot Quiver Plot... on time series'
                            print 'Plot time..'
                            # Normalise the Arrow Scale ???
                            #N = numpy.sqrt(U**2+V**2)  # there may be a faster numpy "normalize" function
                            #U2, V2 = U/N, V/N
                            N = numpy.sqrt(p2.xvel[:, myInd]**2+p2.yvel[:, myInd]**2) # Normalising
                            UN2 = p2.xvel[:, myInd]/N
                            VN2 = p2.yvel[:, myInd]/N   
                            # SCALE THE ARROWS ???                         
                            Scale_F = maxy*0.5
                            UN2 *= Scale_F
                            VN2 *= Scale_F
                            # Try to Calculate Vector Angl of Velocity..... or  MOMENTUM ?????
                            print len(p2.yvel[:, myInd])
                            for counter in range(len(p2.yvel[:, myInd])):
                                print counter
                                print p2.xvel[counter, myInd], p2.yvel[counter, myInd]
                                print BearingDistance(p2.xvel[counter, myInd], p2.yvel[counter, myInd] )
                            #print vAngle
                            # Now Plot Arrows
                            pyplot.quiver(p2.time, plot_variable[:, myInd],UN2,VN2,scale=1.0, scale_units='xy', color='red',linewidth = 0.5)                            
                            #pyplot.quiver(p2.time, plot_variable[:, myInd],
                            #p2.xvel[:, myInd], p2.yvel[:, myInd],scale=1.0, scale_units='xy', color='red')
                        if plt_file_nm == 'MomD_':
                            # Add arrows
                            print 'Try to plot Quiver Plot... on time series'
                            print 'Plot time..'
                            # Normalise the Arrow Scale ???
                            #N = numpy.sqrt(U**2+V**2)  # there may be a faster numpy "normalize" function
                            #U2, V2 = U/N, V/N
                            N = numpy.sqrt(p2.xmom[:, myInd]**2+p2.ymom[:, myInd]**2) # Normalising
                            UN2 = p2.xmom[:, myInd]#/N
                            VN2 = p2.ymom[:, myInd]#/N   
                            # SCALE THE ARROWS ???                         
                            Scale_F = maxy*5.0
                            UN2 *= Scale_F
                            VN2 *= Scale_F
                            # Try to Calculate Vector Angl of Velocity..... or  MOMENTUM ?????
                            print len(p2.ymom[:, myInd])
                            for counter in range(len(p2.ymom[:, myInd])):
                                print counter
                                print p2.xmom[counter, myInd], p2.ymom[counter, myInd]
                                print BearingDistance(p2.xmom[counter, myInd], p2.ymom[counter, myInd] )
                            #print vAngle
                            # Now Plot Arrows
                            pyplot.quiver(p2.time, plot_variable[:, myInd],UN2,VN2,scale=1.0, scale_units='xy', color='red',linewidth = 0.5)                            
                        
                        
                        #indexy = plot_variable[:, myInd].index(maxy)
                        print maxy,plot_variable[:, myInd]
                        #raw_input('Ready 2 Plot')
                        #pyplot.plot(p2.time, p2.stage[:, myInd], 'o-', color='green')
                        
                        # ---- Draw Limit Lines on the Vx D plot at 0.4 and 1.0
                        if plt_file_nm == 'Mom_':
                            print p2.time[0]
                            print myInd
                            print p2.time[-1]
                            if maxy > 0.4:
                                x04 = []
                                t04 =[]
                                x04.append(0.4)
                                x04.append(0.4)
                                t04.append(p2.time[0])
                                t04.append(p2.time[-1])
                                pyplot.plot(t04, x04, '-', color='green')
                            if maxy > 1.0:
                                x1p0 = []
                                t1p0 =[]
                                x1p0.append(1.0)
                                x1p0.append(1.0)
                                t1p0.append(p2.time[0])
                                t1p0.append(p2.time[-1])
                                pyplot.plot(t1p0,x1p0, '-', color='red')
                        pyplot.suptitle(plot_type+labels[i], fontsize=20)
                        pyplot.title(os.path.basename(Last_SWW_File1_Used )[0:-4]+' Max. value: '+str(maxy)+' @ time:'+str(peak_time), fontsize=14)
                        pyplot.xlabel('Time (s)')
                        pyplot.ylabel(y_axis_label)
                        
                        figName = os.path.basename(Last_SWW_File1_Used )[0:-4]+'_Plot_'+plt_file_nm+labels[i]+str(i)+Last_Plot_format_used 
                        pyplot.savefig(output_dir+os.sep+figName)
                        """
                        l = [1,2,3,4,5] #python list
                        a = numpy.array(l) #numpy array
                        i = a.tolist().index(2) # i will return index of 2
                        print i
                        """
                # END IF
            # END While
 
        elif reply == "K_Plot_muliple_SWW_TS_at_pts":
            # For many points, open many SWW's and plot time series ot get Maximum values
            output_dir = os.path.dirname(swwFile)
            print output_dir
            x0s,y0s,labels = get_gauge_loc_and_labels(Last_dir_used)
            swwFile_list = []
            print 'Labels are...'
            print labels
            for i in range(len(x0s)):
                print 'i = : '+str(i)
                ## Batch plotting with multiple models, first get list of sww's
                filecount = 0 
                print labels[filecount]
                p2SC2 =[]
                select_plot = True
                while select_plot:
                    plotreply ,plot_variable,plot_type,plt_file_nm,y_axis_label,select_plot  = get_plot_variable( )  # Needs to Pass p and p2 ?? for Multiple sww s ??
        
                    getmoresww = True
                    pyplot.clf()
                    while getmoresww:
                        title = "Append SWW Files to Process ?"
                        msg = "Select another SWW file Plot?"
                        getmoresww = ynbox(msg, title)
                        if getmoresww:
                            swwFile =fileopenbox(msg="OPEN additional ANUGA SWW  "   # HERE IS THE FILE OPEN BOX FOR GUI
                              ,title="Get SWW FiLE (need centroid and vertex ?)"
                              ,filetypes = ["*.sww" ],default = Last_dir_used+'/*.sww')
                              
                            swwFile_list.append(swwFile)
                            
                            p1SC2=util.get_output(swwFile)
                            p2SC2=util.get_centroids(p1SC2,velocity_extrapolation=True)
                            myInd=((p2SC2.x-x0s[i])**2+(p2SC2.y-y0s[i])**2).argmin()
                            pyplot.plot(p2SC2.time, plot_variable[:, myInd], '-', color='red')
                # 
                # 
                            filecount +=1
                pyplot.savefig(sww_basename+labels[filecount]+Last_Plot_format_used) 
                
        elif reply == "L_Plot_Stage_Along_Poly":
            ## Get indices near a transect (within 50m), and plot their stage
            ## at an instant in time in local co-ords
            """
            Poly_file =fileopenbox(msg="Select polyline File\n\nPick File with Location Data."   # HERE IS THE FILE OPEN BOX FOR GUI
                     ,title="Select Poly line file to Extract Results"
                     ,filetypes = ["*.csv" ],default="c:\BALANCE_RnD\2010\*.csv" )
            infid = open(Poly_file,'r')
            output_dir = os.path.dirname(Poly_file)
            print output_dir
            lines = infid.readlines()[1:] # Skip Header Line.... Or read it to use as part of LAbel ...
            raw_input('File now Open...Continue..') 
            x0s = []
            y0s=[]
            """
            # Can Plot friction, stage, vel
            p0=[min(p2.x), min(p2.y)] # start point on transect
            p1=[max(p2.x), max(p2.y)] # end point on transect
            neartrans=util.near_transect(p2, p0, p1, tol=5.)
            # Contains the indices of the points + the 'distance' along the transect
            print len(neartrans)
            pyplot.clf()
            
            #k=(p2.elev[neartrans[0]]<0.) # Indices of nearTrans[0] which have bed below MSL
            k=(p2.elev[neartrans[0]]>0) # Indices of nearTrans[0] which have bed below MSL
            # Pick index closest to 1000s
            # Or allow to pick a time....
            myInd=abs(p.time-1000.).argmin()
            #pyplot.scatter(neartrans[1][k], p2.stage[myInd,neartrans[0][k]])
            #pyplot.scatter(neartrans[1], (p2.stage-p2.elev)[myInd,neartrans[0]] ,color = 'blue', s = 2)  # p2.stage-p2.elev
            pyplot.scatter(neartrans[1], p2.elev[neartrans[0]] ,color = 'black', s = 2) 
            #pyplot.scatter(neartrans[1], p2.friction[myInd,neartrans[0]],color = 'green', s= 2)
            pyplot.scatter(neartrans[1], p2.stage[myInd,neartrans[0]],color = 'blue', s = 2)
            #pyplot.scatter(neartrans[1], p2.vel[myInd,neartrans[0]],color = 'red',s = 2)
            """
            pyplot.clf()
            pyplot.scatter(p2.x, p2.y, c=p2.elev,edgecolors='none')
            pyplot.gca().set_aspect('equal')
            """
            #j=neartrans[0]
            #pyplot.quiver(p2.x,p2.y,p2.xvel[myInd,], p2.yvel[myInd,],
            #              color='blue',scale=0.006, scale_units='xy')
                         
        elif reply == "M_Plot_Q_at_ALL_Cross Section_Polys_in_DIR":
            read_XSdir_plot(settings.Last_SWW_File1_Used,settings.Last_XSFilesDIR_Used, filepattern='*.csv')
            """
            for XS_File_Name in glob.glob(os.path.join(settings.Last_XSFilesDIR_Used, '*.csv')):      
                polyline = read_polygon(XS_File_Name)#[[17., 0.], [17., 5.]]
                extract_plot_hydrograph(settings.Last_SWW_File1_Used ,polyline,XS_File_Name)
            """    
            for XS_File_Name in glob.glob(os.path.join(settings.Last_XSFilesDIR_Used, '*.mif')):      
            # Should this also deal with MID/MIF's ???
            #if XS_Location_file.endswith('.mif') or XS_Location_file.endswith('.MIF'):
                # Process MID/MIF to Extract XS lines
                """
                Pline 2
                304936.193662921 6188784.36068247
                304931.314436293 6188730.68918956
                Pen (2,2,16711935)
                """
                # Open the 1D MID/MIF Files  Needs the MID for the XS label.... "XS_1","State Highway","53.889 m",186.3948
                try:
                    fhMID = open(XS_File_Name[:-4]+'.MID',"r") #   Could check if os.path.isfile(fileref_1D):
                except:  
                    fhMID = open(XS_File_Name[:-4]+'.mid',"r") # Sometimes MID/MIF files are upper or lower case
                try:
                    fhMIF = open(XS_File_Name[:-4]+'.MIF',"r") #   Could check if os.path.isfile(fileref_1D):
                except:  
                    fhMIF = open(XS_File_Name[:-4]+'.mif',"r") # Sometimes MID/MIF files are upper or lower case
                MIDlines = fhMID.readlines() # <<<----- XS labels etc
                MIFlines = fhMIF.readlines() # <<<----- UTM Position DATA
                midlinecount = 0
                Read_pline = False
                for lineMif in MIFlines:
                    if lineMif.startswith('Pline'): # get PolyLine Data
                        Pts_for_XS = int(lineMif.split(' ')[1])
                        Read_pline = True
                        polyline = []
                    elif lineMif.strip().startswith('Pen'):
                        # End of Pline and line data
                        Read_pline = False
                        print MIDlines[midlinecount].split(',')[0].strip('"')
                        
                        XS_Label_Name = XS_File_Name[:-4]+'_'+MIDlines[midlinecount].split(',')[0].strip('"')+'.MIF'
                        print XS_Label_Name
                        extract_plot_hydrograph(settings.Last_SWW_File1_Used ,polyline,XS_Label_Name)
                        midlinecount +=1
                    elif Read_pline:
                        X = lineMif.split(' ')[0]
                        Y = lineMif.split(' ')[1]
                        pt = [X,Y]
                        polyline.append(pt)
                        
        
        elif reply == "N_MAKE_GEOTIFF":
            ###########################################################
            ## Make GeoTiff
            # Best to specify the bounding polygon if the plot is large scale (don't have
            # it in my example)
            #
            print 'About to create Geotiffs..'
            util.Make_Geotif(Last_SWW_File1_Used,
                             output_quantities=['depth', 'depthIntegratedVelocity','stage','velocity', 'elevation'],
                             myTimeStep='max',
                             EPSG_CODE=28356,  #32756,
                             CellSize=1.0,
                             #lower_left=[680000., 9.05e+06],
                             #upper_right=[695000, 9.07e+06],
                             output_dir = os.path.join(os.path.dirname(Last_SWW_File1_Used),'TIFS'),
                             bounding_polygon=None)
            print 'Geotiffs Created !!!!'
        # ENF IF reply SOMETHING
        print 'Keep Plotting = ' + str(Keep_Plotting)
    # END IF reply == none
    
    settings.store()
# END WHILE    

# OTHER POSSIBLE TOOLS......
"""

def get_interpolated_quantities_at_polyline_midpoints(filename,
                                                      quantity_names=None,
                                                      polyline=None,
                                                      verbose=False):
    return segments, I
    
def get_interpolated_quantities_at_multiple_polyline_midpoints(filename,
                                                      quantity_names=None,
                                                      polylines=None,
                                                      verbose=False):
    return mult_segments, I
    

def get_energy_through_cross_section(filename,
                                     polyline,
                                     kind='total',
                                     verbose=False):
                                         
    return time, E                                                                                                    
                                                              

def get_flow_through_cross_section(filename, polyline, verbose=False):
    return time, Q

def get_flow_through_multiple_cross_sections(filename, polylines, verbose=False):
    return time, mult_Q


"""


    
# OTHER STUFF .............    
"""
    
## Extreme north point
x0=200000.; y0=160000.; 
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

## Eastern Edge
x0=400000.; y0=100000.; 
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

## Over initial perturbation
x0=200000.; y0=70000.; 
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

## Seaward edge of bay
x0=210000.; y0=50000.;
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

## Deeper in the bay
x0=208000.; y0=45000.
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

## In the constriction
x0=207000.; y0=39000.
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

##  Offshore of Bima
x0=207000.; y0=36000.
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')

## South part of Bay
x0=205000; y0=28000.
#myInd=( (p2.x-x0)**2+(p2.y-y0)**2).argmin()
#pyplot.clf()
#pyplot.plot(p2.time, p2.stage[:, myInd], '-o', color='green')
pyplot.scatter(x0,y0,s=200,color='black')
"""






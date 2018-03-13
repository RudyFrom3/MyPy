"""

Open File and Convert format....
Extracted from Water Ride....


Time(hrs),Date,"(100y120m_0il_0cl_unblocked) Flow [m3s]",WL
0.00,0.000,0.0000,0.00
0.02,"0.017 hours",0.0000,0.00
0.03,"0.033 hours",0.0000,0.00
0.05,"0.050 hours",0.0001,6.69


Time (seconds), Q 


"""
from easygui import *
import os
import glob

#------------------------------------------------------------------------------------------       
def Process_QFile(File_Used):
    """
    
    """
    print "Processing..."
    Time_Step = 60.0  # make option to ask for time step.... as data appears to be rounded.... hence not correct !!
    infid = open(File_Used,'r')
    outfid = open(File_Used[:-4]+"_Convertd.csv",'w')
    #output_dir = os.path.dirname(Poly_file)

    #print output_dir
    t = 0.0
    lines = infid.readlines()#[1:] # Skip Header Line.... Or read it to use as part of LAbel ...
    for line in lines[1:]:
        print line
        #t = float(line.split(',')[0])*3600.0
     
        Q = float(line.split(',')[2])  
        s = '%7.1f,%7.3f \n' %(t,Q)
        outfid.write(s)    
        t = t+Time_Step
    
    outfid.close()
    infid.close()
    # Complete
    return()
#------------------------------------------------------------------------------------------


Choice = raw_input('Get Dir of File (D F) ?')
print Choice

if Choice in ['D','d']:
    print ' Get DIR...'
    title = "Go get DIR...."
    msg = "Pick the directory that you wish to open."
    default = '*.*'
    DIR_Used = diropenbox(msg, title,default)    
    pattern = os.path.join(DIR_Used, '*Q.csv')
    files = glob.glob(pattern)    
    count = 0
    for f in files:  
        print f
        count+=1
        Process_QFile(f)
    # End of Loop
    

elif Choice in ['F','f']:
    print 'Go get a Locations.... open a file....'
    File_Used = fileopenbox(msg="OPEN file"   # HERE IS THE FILE OPEN BOX FOR GUI
        ,title="Get file to convert"
        ,filetypes = ["*.csv" ],default = '*.csv') 

 
    
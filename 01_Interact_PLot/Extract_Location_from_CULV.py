"""
Script to Read multiple (ANUGA)Culvert Data Files and extract locations to plot



description=CC10_0001_C
label =CC10_0001_C
manning=0.015
invert_elevations=[0.53, 0.53]
losses =3.0
barells = 2
diameter = 0.53
structure_type='boyd_pipe'
end_points=[[306654.72, 6191281.3], [306654.21, 6191267.15]]
exchange_lines=None,
#Notes: "Details from Puckey Avenue Survey"

Get Files DIR
Get all files
Search for Location Data
Extract
"""

from easygui import *
import os
import glob

#------------------------------------------------------------------------------------------       
def Process_CulvFile(File_Used):
    """
    Look for:
    end_points=[[306654.72, 6191281.3], [306654.21, 6191267.15]]
    or
    exchange_lines=[[306174.09,6191074.17],[306243.4,6191061.28]],[[306266.03,6191064.06],[306285.76,6191061.41]]
    """
    print "Processing..."
    Time_Step = 60.0  # make option to ask for time step.... as data appears to be rounded.... hence not correct !!
    infid = open(File_Used,'r')
    outfid = open(File_Used[:-4]+"_Ext_LOC.txt",'w')
    #output_dir = os.path.dirname(Poly_file)

    #print output_dir
    t = 0.0
    lines = infid.readlines()#[1:] # Skip Header Line.... Or read it to use as part of LAbel ...
    for line in lines[1:]:
        print line
        #t = float(line.split(',')[0])*3600.0
        if line.startswith('end_points'):
            Bits = line.split('=')[1].translate(None,"[]").split(',')
            print Bits
            if Bits[0] == "None":
                pass
            else:
                print Bits[0],Bits[1]
                print Bits[2],Bits[3]
                #name.translate(None, "(){}<>")
                s = '%10.3f,%10.3f \n' %(float(Bits[0]),float(Bits[1]))
                outfid.write(s)    
                s = '%10.3f,%10.3f \n' %(float(Bits[2]),float(Bits[3]))
                outfid.write(s)    
        elif line.startswith('exchange_lines=[['):
            Bits = line.split('=')[1].translate(None,"[]").split(',')
            print len(Bits)
            for i in range(len(Bits)/2):
                s = '%10.3f,%10.3f \n' %(float(Bits[i*2]),float(Bits[i*2+1]))
                print s
                outfid.write(s)    
  
            raw_input('Check')
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
    pattern = os.path.join(DIR_Used, '*.csv')
    files = glob.glob(pattern)    
    count = 0
    for f in files:  
        print f
        count+=1
        Process_CulvFile(f)
    # End of Loop
    

elif Choice in ['F','f']:
    print 'Go get a Locations.... open a file....'
    File_Used = fileopenbox(msg="OPEN file"   # HERE IS THE FILE OPEN BOX FOR GUI
        ,title="Get file to convert"
        ,filetypes = ["*.csv" ],default = '*.csv') 
    Process_CulvFile(File_Used)
print " ALL DONE !!"    
 

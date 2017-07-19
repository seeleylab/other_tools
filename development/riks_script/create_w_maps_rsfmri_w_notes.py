#JD--what a w-score is:
#JD--you have 1 patient and a group containing multiple matched HCs
#JD--you regress GM against covariates in the HC group to get a map containing beta values and residuals at each voxel
#JD--you take the regression model derived from the HCs and plug in the covariate values of your patient to get their predicted
#JD--GM value at each voxel.

#JD--w-score at each voxel is calculated as
#JD--(patient's predicted value at that voxel from the HC regression equation) -
#JD--(observed value at that voxel from the patient's image)
#JD--divided by the residuals from the HC regression equation
#JD--so a positive w-score means the subject has more atrophy than normal.

from glob import glob
import pandas
import numpy as np #I don't think numpy is used in the script at all?
import os

### Type either 'W' for W Map, or 'GMA' for % Gray Matter Atrophy map ### 
processing_type = 'W' 

### MASK MUST BE USED FOR SCRIPT TO WORK.  
### usually you want to use the one from the HC-model directory
#mask = '/data2/mridata2/Suzee/studies/GRN_rsfMRI/1SampT/NKI_GenPop_demo_matched/1ST_no_TIV/masks/pfwe01/PostCen/L_R_PostCen_unified_subcor_cer_ICVgm02_binary_91x109x91.nii'
#mask = '/data2/mridata2/Suzee/studies/GRN_rsfMRI/1SampT/NKI_GenPop_demo_matched/1ST_no_TIV/masks/pfwe01/FI/R_FI_pfwe01p001_binarized.nii'

mask = raw_input('Enter the path of the mask.\n')
while not os.path.isfile(mask):
    mask = raw_input('Specified mask is not a valid file path. Enter the path of the mask.\n')

### Enter path and filename of ResMs file derived from the SPM model in controls
#JD--first have to run a regression model on your control group (picked from Ana's w-score spreadsheet)
#JD--don't choose the option of "covariates centered around mean" when doing this in SPM
#ResMS = '/data2/mridata2/Suzee/studies/W-score_multiple_regressions/rsfmri_multiple_regressions/GRN_seeds/L_PCG/ResMS.nii'
ResMS = '/data2/mridata2/Suzee/studies/W-score_multiple_regressions/rsfmri_multiple_regressions/GRN_seeds/R_FI/ResMS.nii'

HC_regr = raw_input('Enter the path of the mask.\n')
while not os.path.isdir(HC_reg):
    HC_regr = raw_input('Specified HC regression model is not a valid directory. Enter the directory of the HC regression model.\n')

### im_dir is the directory containing the different patient group directories
#JD--you have to copy and move all the patient images into this directory, which is inconvenient. Would be easier if the script could
#JD--directly draw from the patient images where they originally exist
#JD--needs the forward slash at the end of "scans" to work
#im_dir = '/data2/mridata2/Suzee/studies/GRN_rsfmri/12GRNps_w_maps/L_PCG/scans/'
im_dir = '/data/mridata/jdeng/w_score_sandbox/R_FI/scans/'

###ctrl_dir is the name of your control directory.  If your control directory is with your patient directories,
###type the path to your control directory here.  If you *want* your controls to be included in the analysis, or if they are in a
###separate directory, type 'none' 
#JD--Ana says she's never used this
ctrl_dir = 'none'

###bmapdir should be the directory where your beta maps are located
#JD--it's the same directory where your ResMS files are located
#bmapdir = '/data2/mridata2/Suzee/studies/W-score_multiple_regressions/rsfmri_multiple_regressions/GRN_seeds/L_PCG/'
bmapdir = '/data2/mridata2/Suzee/studies/W-score_multiple_regressions/rsfmri_multiple_regressions/GRN_seeds/R_FI'

###xl_f should be the file path where your excel file is located
#JD--this file contains the study IDs and covariates for the patients. It might be useful to put a column containing the patient
#JD--image paths in here, which would solve the problem with having to make the 'im_dir'.
xl_f = '/data2/mridata2/Suzee/studies/GRN_rsfmri/12GRNps_w_maps/12GRNps_w-score_sheet.xlsx'

###opdir is where you want to put all of your output. 
#opdir = '/data2/mridata2/Suzee/studies/GRN_rsfmri/12GRNps_w_maps/L_PCG/'
opdir = '/data/mridata/jdeng/w_score_sandbox/R_FI/'

###in regressors, please print the names of each variable you will be using as a regressor.
###use the following format: ['var1', 'var2', 'var3']
###make sure these match the columns of your spreadsheet
###make ABSOLUTELY SURE that you enter these variables in the exact same order as your beta maps.  e.g. the first variable in
###the list should be the variable for betam0001
regressors = ['CalcAge', 'Sex', 'Handedness', 'Education']

#########DO NOT EDIT BELOW THIS LINE#################################



if os.path.isfile(ResMS):
    print 'ResMS map: %s'%(ResMS)
else:
    raise IOError('specified ResMS map, %s is not a valid filepath'%(ResMS))

if os.path.isdir(im_dir):
    print 'image directory: %s'%(im_dir)
else:
    raise IOError('specified image directory, %s is not a valid directory'%(im_dir))

if ctrl_dir == 'none':
    print 'no control directory specified'
else:
    if os.path.isdir(ctrl_dir):
        print 'excluding control directory: %s'%(ctrl_dir)
    else: 
        raise IOError('specified control directory, %s is not a valid directory'%(ctrl_dir))

if os.path.isdir(bmapdir):
    print 'beta map directory: %s'%(bmapdir)
else:
    raise IOError('specified beta map directory, %s is not a valid directory'%(bmapdir))

if os.path.isfile(xl_f):
    print 'excel file: %s'%(xl_f)
else:
    raise IOError('specified excel file, %s is not a valid filepath'%(xl_f))

print 'initiating'

### computing residual maps using the ResMS
os.system('fslmaths %s -sqrt %ssqrt_res.nii.gz'%(ResMS, opdir))
stdv_map = '%ssqrt_res.nii.gz'%(opdir)

### imdir is the directory containing the different patient group directories

globstr = im_dir+'*/'
alldirs = sorted(glob(globstr))

#### following part to be adapted to ensure that we are only looking at patients directories (=getting rid of the 'controls' directory).
if ctrl_dir == 'none':
    pass
else:
    alldirs.remove(ctrl_dir)

print alldirs
user_input = raw_input('The directories listed above will be used in your script. If this seems right, type y. Otherwise, type n.\n')

if user_input != 'y' and user_input != 'n': #it was returning an error because 'or' was used instead of 'and'
    user_input = raw_input('You didn\'t type y or n.  Please type y if you\'re happy with the directories, or n if you are not.\n')
else: 
    pass

if user_input == 'n':
    raise ValueError('Please adjust your directories and try running the script again.')
elif user_input == 'y':
    pass
else:
    raise ValueError('Figure out how to type y or n, bozo. When you figure it out, try running the script again.')

    

#alldirs.remove(alldirs[-1])

### following line has to be editable (move it at the beginning of the script?)

bmapstr = 'beta_000'
dnames = []
for d in alldirs:
    pth,dname = os.path.split(d)
    rpth, rdname = os.path.split(pth)
    dnames.append(rdname)

xl_tabs = pandas.ExcelFile(xl_f).sheet_names
if sorted(dnames) == sorted(xl_tabs):
    pass
else:
    xlmiss = set(xl_tabs) - set(dnames)
    dnmiss = set(dnames) - set(xl_tabs)
    raise IOError('the tabs in your excel sheet %s do not match your image directories %s.  Tabs and directory names must match.'%(xlmiss,dnmiss))

for tab in xl_tabs:
    df = pandas.ExcelFile(xl_f).parse(tab)
    cols = df.columns.tolist()
    for regr in regressors:
        if regr in cols:
            continue
        else:
            raise IOError('column name %s is missing from the %s tab of your excel sheet.  Please ensure all column names match those you input in the regressors field'%(regr,tab))



### should be edited (move it at the beginning of the script?)

for dname in dnames:
    print 'copying files for '+dname
    ### following should be editable (and moved in earlier lines of this script) to indicate where to put the data
    ndir = opdir+dname+'_scans/'
    odir = opdir+dname+'_output_NKIPostCenUnified/'
    os.system('mkdir '+ndir)
    os.system('mkdir '+odir)
    idir = im_dir+dname
    globstr = idir+'/con*' 
    scans = sorted(glob(globstr))
    for scan in scans:
        os.system('cp '+scan+' '+ndir)
    globstr = ndir+'con*' #took out the '/' infront of smwc
    scans = sorted(glob(globstr))
    no_scans = len(scans)
    
    df = pandas.ExcelFile(xl_f).parse(dname)
    subs = df[:]['Study ID#'].tolist()
    no_subs = len(subs)
    print 'checking for homogeneity between project files and spreadsheet for '+dname
    if no_subs == no_scans:
        pass
    else:
        xl_subids = {}
        for i,sub in enumerate(subs):
            sublets = []
            for s in sub:
                sublets.append(s)
            id = sublets[-2]+sublets[-1]
            xl_subids.update({id: i})
        scan_subids = {}
        for i,scan in enumerate(scans):
            pth,sid = os.path.split(scan)
            sid,jnk = sid.split('.')
            sidlist = []
            for si in sid:
                sidlist.append(si)
            sid = sidlist[-2]+sidlist[-1]
            scan_subids.update({sid: i})
        
            mismatches = set(xl_subids.keys()) - set(scan_subids.keys())
        print 'mismatches between spreadsheet and project files'
        print mismatches
        for mm in mismatch:
            mmval = xl_subids[mm]
            nmm = int(mmval)
            df.drop(df.index[nmm])
        subs = df[:]['NEW ID#']
    
   
    df.index = subs
    vcols = {}
### editable : you should check the order of these beta maps. 
    for i,regr in enumerate(regressors):
        vcols.update({str(i): regr})
    #vkeys = vcols.keys()
    vkeys = ['0','1','2','3'] #THIS WILL NEED TO BE ADJUSTED DEPENDING ON THE NUMBER OF COVARIATES THAT ARE INCLUDED
    #JD--this calculates the number of covariates based on the excel sheet xl_f. It currently does not work.
    for subj,jnk in df.iterrows():
        print 'creating images for '+subj
        if processing_type == 'W':
             f_outfile = odir+'con'+subj+'_wMap.nii'
        elif processing_type == 'GMA':
             f_outfile = odir+'smwc1'+subj+'_pGMA_Map.nii'
        else:
            raise ValueError('please open script and make sure processing_type = either W or GMA, and make sure this value is surrounded by single quotes.')  
        for col in vkeys:
            colint = int(col)+1
            val = df.ix[subj,colint]
            val = str(val)
            infile = bmapdir+bmapstr+str(colint+1)+'.nii'
            if ' ' in col:
                cols = col.rsplit()
                col = cols[0]
            outfile = odir+'con'+subj+'_d'+str(colint)+'.nii' #changed col to colint
            os.system('fslmaths '+infile+' -mul '+val+' '+outfile+'.gz')
        pmap = odir+'con'+subj+'_dPredicted'+'.nii.gz' 
        os.system('fslmaths '+odir+'con'+subj+'_d%s.nii.gz -add '%(str(int(vkeys[0])+1))+odir+'con'+subj+'_d%s.nii.gz -add '%(str(int(vkeys[1])+1))+odir+'con'+subj+'_d%s.nii.gz -add '%(str(int(vkeys[2])+1))+odir+'con'+subj+'_d%s.nii.gz -add '%(str(int(vkeys[3])+1))+bmapdir+bmapstr+'1.nii '+pmap) ### assumes that beta0006 is the intercept. Might not be true with other versions of SPM
        if processing_type == 'W':
            os.system('fslmaths '+pmap+' -sub '+ndir+'con'+subj+'.nii.gz '+odir+'con'+subj+'_dNumerator.nii')
            #os.system('fslmaths '+ndir+'smwc1'+subj+'.nii.gz -sub '+pmap+' '+odir+'smwc1'+subj+'_dNumerator.nii')
            os.system('fslmaths '+odir+'con'+subj+'_dNumerator.nii.gz -div '+stdv_map+'%s -mas '%('.nii.gz')+mask+' '+f_outfile) #reversed the order of predicted and obsevred (was precited-observed, why?)
        else:
            os.system('fslmaths '+pmap+'  -sub '+ndir+'smwc1'+subj+'.nii.gz '+odir+'smwc1'+subj+'_dNumerator.nii')
            os.system('fslmaths '+odir+'smwc1'+subj+'_dNumerator.nii.gz -mul 100 -div '+pmap+' -mas '+mask+' '+f_outfile)
        #os.system('rm '+odir+'con'+subj+'_d*')

    print 'completed image creation for '+dname     

	                    
         

####################################################### w-map script 11/30/15 ########################################################################
#DISCLAIMER: THE SEELEY LAB IS NOT RESPONSIBLE FOR ANY INACCURATE CONCLUSIONS DRAWN AS A RESULT OF USING THIS SCRIPT.

#IF A DIFFERENT HC GROUP IS DESIRED, UNCOMMENT LINES 70-74 and 93 BEFORE RUNNING SCRIPT.

#Import modules needed
import os
import glob
import pandas
import sys

########################################################### USER OPTIONS ###########################################################################
#Prompt user to choose type of w-map.
processing_type = raw_input('1. Enter FC for functional connectivity w-map or GMA for gray matter atrophy w-map.\n')

if processing_type != 'FC' and processing_type != 'GMA':
    processing_type = raw_input('Error--Specified processing type is not a valid option. Enter FC for functional connectivity w-map or GMA for gray matter atrophy w-map.\n')
else:
    pass

#If FC w-maps are wanted, prompt user for processedfmri folder name and seed folder name.
if processing_type == 'FC':
    processedfmri_folder = raw_input('\nAll subjects are assumed to have a processedfmri_TRCNnSFmDI folder. If your subjects have a processedfmri folder with a different extension, specify that folder below (e.g. processedfmri_RTCsNsSFmI). Otherwise, hit Enter.\n')
    if processedfmri_folder == '':
        processedfmri_folder = 'processedfmri_TRCNnSFmDI'
    else:
        pass
    seed_folder = raw_input('Specify the folder containing the seed results for each subject (e.g. stats_FC_L_PostCen_4--42_-20_56_roi):\n')

#Prompt user for Excel spreadsheet containing subjdir column and covariate columns.
xl_f = raw_input('\n2. Enter the path of the Excel spreadsheet containing the subjects you want w-maps for.\n')

while not os.path.isfile(xl_f):
    xl_f = raw_input('Error--Specified spreadsheet is not a valid file path. Enter the path of the Excel spreadsheet containing the subjects you want W-maps for.\n')

df = pandas.read_excel(xl_f)

#If FC w-maps are wanted, check that each subjdir directory has a seed con_0001.nii file necessary for creating the w-maps.
if processing_type == 'FC':
    print('Checking each subject for con_0001.nii image...')
    for i in df.ix[:,'subjdir']:
        if os.path.exists(i+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii'):
            pass
        else:
            print('Error--'+i+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii does not exist. Check and try again.')
    print('Finished checking.')

#If GMA w-maps are wanted, check that each subjdir directory has a smwc1* file necessary for creating the w-maps.
if processing_type == 'GMA':
    print('Checking each subject for smwc1 image...')
    for i in df.ix[:,'subjdir']:
        if len(glob.glob(os.path.split(i)[0]+'/struc/SPM12_SEG_Full/smwc1*')) == 1:
            pass
        else:
            print('Error--'+os.path.split(i)[0]+'/struc/SPM12_SEG_Full/smwc1* does not exist. Run segmentation and try again.')  
    print('Finished checking.')
    
#Prompt user for the mask.
mask = raw_input('\n3. Enter the path of the whole brain mask that the w-maps will be masked to.\n')

while not os.path.isfile(mask):
    mask = raw_input('Error--Specified mask is not a valid file path. Enter the path of the mask.\n')

#Set HC group.
if processing_type == 'FC':
    HC_model = '/data2/mridata2/Suzee/studies/W-score_multiple_regressions/rsfmri_multiple_regressions/GRN_seeds/L_PCG'
elif processing_type == 'GMA':
    HC_model = '/data/mridata/asias/W-score/GRNpresymp_288HC_mulreg_nocenter_withAmbi'

#Prompt user for the directory containing all of the HC regression model files.
#HC_model = raw_input('\nEnter the directory containing the HC regression model.\n')

#while not os.path.isdir(HC_model):
#    HC_model = raw_input('Error--Specified HC regression model is not a valid directory. Enter the directory containing the HC regression model.\n')

#Prompt user for a list of covariates
covs = eval(raw_input('\n4. Out of the following covariates--Age, Education, Gender, Handedness, Scanner, TIV--enter the covariates you are using in the following format: [\'cov1\', \'cov2\', \'cov3\']. \nYou MUST enter these in the same order as your beta maps from the HC regression model and in the same order as the columns in your spreadsheet.\n'))

while covs != list(df.columns.values)[1:]:
    covs = eval(raw_input('Error--Enter your covariates in the following format: [\'cov1\', \'cov2\', \'cov3\']. You MUST enter these in the same order as your beta maps from the HC regression model and in the same order as the columns in your spreadsheet.\n'))

covs_suffixes = {'Age': 'a', 'Education': 'e', 'Gender': 'g', 'Handedness': 'h', 'Scanner': 's', 'TIV': 't'}

suffix = ''

for c in sorted(covs):
    if c not in covs_suffixes:
        print('\nSorry, the covariate %s is not supported yet.'%(c))
        sys.exit(1)
    else:
        suffix += covs_suffixes[c]

#suffix = raw_input('\n6. Enter a concise descriptive suffix for your w-map analysis results folders. Do not use spaces.\n')

########################################################### CALCULATIONS ###########################################################################
os.system('fslmaths '+HC_model+'/ResMS.nii -sqrt '+HC_model+'/sqrt_res')        #Calculate denominator for all subjects (HC regr model residuals SD map)
denominator = HC_model+'/sqrt_res'

for index,row in df.iterrows():         #Loop through each subject and define paths for FC and GMA options. Then...
    subj = row  
    if processing_type == 'FC':
        wmapdir = subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix
        actualimage = subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii'
    elif processing_type == 'GMA':
        wmapdir = os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/wmap_'+suffix
        actualimage = glob.glob(os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/smwc1*')[0]

    if os.path.exists(wmapdir):                     #...check if they have already been run. Skip if they have, or else...
        print(os.path.split(subj['subjdir'])[0]+' has already been run! Will be skipped.')
    else:
        os.system('mkdir '+wmapdir)                 #...create a "wmap" folder for each subject to catch output
        os.chdir(wmapdir); f = open('log', 'w')     #...initiate a log file in each subject's "wmap" folder
        map_pred_for_subj = wmapdir+'/map_pred_for_subj'    #...calculate pred covariate values
        cov_images = []
        for j in range(1, len(covs)+1):
            cov_for_HC = HC_model+'/beta_000'+str(j+1)+'.nii'
            subj_value = str(subj[j])
            cov_pred_for_subj = wmapdir+'/cov_'+covs[j-1]
            os.system('fslmaths '+cov_for_HC+' -mul '+subj_value+' '+cov_pred_for_subj)
            cov_images.append(cov_pred_for_subj)
            f.write('fslmaths '+cov_for_HC+' -mul '+subj_value+' '+cov_pred_for_subj+'\n\n')     #...record commands which create cov_pred images
            
        cov_images_paths = ''                                                                    #...group all cov_pred image paths together
        for k in range(0,len(cov_images)):
            cov_images_paths += ' -add '+cov_images[k]
            
        os.system('fslmaths '+HC_model+'/beta_0001.nii'+cov_images_paths+' '+map_pred_for_subj)           #...calculate predicted map for subject
        f.write('fslmaths '+HC_model+'/beta_0001.nii'+cov_images_paths+' '+map_pred_for_subj+'\n\n')      #...record command which creates predicted map
            
        os.system('fslmaths '+map_pred_for_subj+' -sub '+actualimage+' '+wmapdir+'/numerator')            #...calculate numerator (predicted - observed)
        numerator = wmapdir+'/numerator'
        f.write('fslmaths '+map_pred_for_subj+' -sub '+actualimage+' '+wmapdir+'/numerator\n\n')          #...record command which creates numerator
        
        os.system('fslmaths '+numerator+' -div '+denominator+' -mas '+mask+' '+wmapdir+'/wmap')           #...calculate w-map
        f.write('fslmaths '+numerator+' -div '+denominator+' -mas '+mask+' '+wmapdir+'/wmap')             #...record command which creates wmap
        f.close()                                                                                         #...close each subject's log file
        
        print 'wmap created for '+subj[0]
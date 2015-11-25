###################################################### w-score script 11/24/15 #####################################################################

#Import modules needed
import os
import glob
import pandas

########################################################### USER OPTIONS ###########################################################################
#Prompt user to choose type of w-map.
processing_type = raw_input('1. Enter FC for functional connectivity W-map or GMA for gray matter atrophy W-map.\n')
if processing_type != 'FC' and processing_type != 'GMA':
    processing_type = raw_input('Error--Specified processing type is not a valid option. Enter FC for functional connectivity w-map or GMA for gray matter atrophy W-map.\n')
else:
    pass

#If FC w-maps are wanted,  prompt user for processedfmri folder name and seed folder name.
if processing_type == 'FC':
    processedfmri_folder = raw_input('\nAll subjects are assumed to have a processedfmri_TRCNnSFmDI folder. If your subjects have a processedfmri folder with a different extension, specify that folder below. Otherwise, hit Enter.\n')
    if processedfmri_folder == '':
        processedfmri_folder = 'processedfmri_TRCNnSFmDI'
    else:
        pass
    seed_folder = raw_input('Specify the folder containing the seed results for each subject:\n')

#Prompt user for Excel spreadsheet containing subjdir column and covariate columns.
xl_f = raw_input('\n2. Enter the path of the Excel spreadsheet containing the subjects you want W-maps for.\n')
while not os.path.isfile(xl_f):
    xl_f = raw_input('Error--Specified spreadsheet is not a valid file path. Enter the path of the Excel spreadsheet containing the subjects you want W-maps for.\n')

df = pandas.read_excel(xl_f)

#If FC w-maps are wanted, check that each subjdir directory has a seed con_0001.nii file necessary for creating the w-maps.
if processing_type == 'FC':
    print('Checking each subj for con_0001.nii image...')
    for i in df.ix[:,'subjdir']:
        if os.path.exists(i+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii'):
            pass
        else:
            print('Error--'+i+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii does not exist. Check and try again.')
    print('Finished checking.')

#If GMA w-maps are wanted, check that each subjdir directory has a smwc1* file necessary for creating the w-maps.
if processing_type == 'GMA':
    print('Checking each subj for smwc1 image...')
    for i in df.ix[:,'subjdir']:
        if len(glob.glob(os.path.split(i)[0]+'/struc/SPM12_SEG_Full/smwc1*')) == 1:
            pass
        else:
            print('Error--'+os.path.split(i)[0]+'/struc/SPM12_SEG_Full/smwc1* does not exist. Run segmentation and try again.')  
    print('Finished checking.')
    
#Prompt user for the mask.
mask = raw_input('\n3. Enter the path of the mask.\n')
while not os.path.isfile(mask):
    mask = raw_input('Error--Specified mask is not a valid file path. Enter the path of the mask.\n')

#Prompt user for the directory containing all of the HC regression model files.
HC_model = raw_input('\n4. Enter the directory containing the HC regression model.\n')
while not os.path.isdir(HC_model):
    HC_model = raw_input('Error--Specified HC regression model is not a valid directory. Enter the directory containing the HC regression model.\n')

#Prompt user for a list of covariates
covs = eval(raw_input('\n5. Enter the variables you will be using as covariates in the following format: [\'var1\', \'var2\', \'var3\']. You MUST enter these in the same order as your beta maps from the HC regression model and in the same order as the columns in your spreadsheet.\n'))
while covs != list(df.columns.values)[1:]:
    covs = eval(raw_input('Error--Specified covariates not entered in correct format. Enter the variables you will be using as covariates in the following format: [\'var1\', \'var2\', \'var3\']. You MUST enter these in the same order as your beta maps from the HC regression model and in the same order as the columns in your spreadsheet.\n'))

#Prompt user for a suffix which will be appended to all results folder names.
suffix = raw_input('\n6. Enter a concise descriptive suffix for your w-map analysis results folders. Do not use spaces. (e.g. 12GRNps_vs_120HC)\n')

########################################################### CALCULATIONS ###########################################################################
#Calculate denominator for all subjects (residuals SD map)
os.system('fslmaths '+HC_model+'/ResMS.nii -sqrt '+HC_model+'/sqrt_res')
denominator = HC_model+'/sqrt_res'
    
#Loop through each subject and ...
for i in range(0,len(df)):
    subj = df.ix[i,:]
    
    #check if they have already been run, and skip if they have
    if processing_type == 'FC' and os.path.exists(subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix):
        print(subj['subjdir']+' has already been run! Will be skipped.')
    elif processing_type == 'GMA' and os.path.exists(os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/wmap_'+suffix):
        print(os.path.split(subj['subjdir'])[0]+' has already been run! Will be skipped.')
    else:
        
        #...create a "wmap" folder to catch output
        if processing_type == 'FC':
            os.system('mkdir '+subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix)
        elif processing_type == 'GMA':
            os.system('mkdir '+os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/wmap_'+suffix)
            
        #...calculate covariate values and add them to the HC regression model intercept to get the predicted value
        curr_value = HC_model+'/beta_0001.nii'
        for j in range(1, len(covs)+1):
            if processing_type == 'FC':
                cov_pred_for_subj = subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix+'/cov_'+covs[j-1]
                map_pred_for_subj = subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix+'/map_pred_for_subj'
            elif processing_type == 'GMA':
                cov_pred_for_subj = os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/wmap_'+suffix+'/cov_'+covs[j-1]
                map_pred_for_subj = os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/wmap_'+suffix+'/map_pred_for_subj'
            
            column_value = j
            beta_value = j+1
            cov_for_HC = HC_model+'/beta_000'+str(beta_value)+'.nii'
            subj_value = str(subj[column_value])
            
            os.system('fslmaths '+cov_for_HC+' -mul '+subj_value+' '+cov_pred_for_subj)
            os.system('fslmaths '+cov_pred_for_subj+' -add '+curr_value+' '+map_pred_for_subj)
            curr_value = map_pred_for_subj
        
            #...calculate numerator (predicted - observed)
            if processing_type == 'FC':
                os.system('fslmaths '+map_pred_for_subj+' -sub '+subj[0]+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii '+subj[0]+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix+'/numerator')
                numerator = subj[0]+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix+'/numerator'
            elif processing_type == 'GMA':
                os.system('fslmaths '+map_pred_for_subj+' -sub '+os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full'+'/smwc*.nii '+os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full'+'/wmap_'+suffix+'/numerator')
                numerator = os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full'+'/wmap_'+suffix+'/numerator'
        
            #...calculate w-map
            if processing_type == 'FC':
                os.system('fslmaths '+numerator+' -div '+denominator+' -mas '+mask+' '+subj[0]+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix+'/wmap')
            elif processing_type == 'GMA':
                os.system('fslmaths '+numerator+' -div '+denominator+' -mas '+mask+' '+os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full'+'/wmap_'+suffix+'/wmap')
                
        print 'wmap created for '+subj[0]
         
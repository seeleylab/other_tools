####################################################### w-map script 1/29/16 ########################################################################
#THIS SOFTWARE IS PROVIDED BY THE SEELEY LAB "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE SEELEY LAB BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#Import modules needed
import os
import glob
import pandas

########################################################### USER OPTIONS ###########################################################################
#Prompt user to choose type of w-map.
processing_type = raw_input('1. Enter FC for functional connectivity w-map, GMA for gray matter atrophy w-map, or WBD for whole brain degree w-map.\n')

if processing_type != 'FC' and processing_type != 'GMA' and processing_type != 'WBD':
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

#If WBD w-maps are wanted, prompt user for processedfmri folder name.
if processing_type == 'WBD':
    processedfmri_folder = raw_input('\nAll subjects are assumed to have a processedfmri_TRCNnSFmDI folder. If your subjects have a processedfmri folder with a different extension, specify that folder below (e.g. processedfmri_RTCsNsSFmI). Otherwise, hit Enter.\n')
    if processedfmri_folder == '':
        processedfmri_folder = 'processedfmri_TRCNnSFmDI'
    else:
        pass

#Prompt user for Excel spreadsheet containing subjdir column and covariate columns.
xl_f = raw_input('\n2. Enter the path of the Excel spreadsheet containing the subjects you want w-maps for.\n')

while not os.path.isfile(xl_f):
    xl_f = raw_input('Error--Specified spreadsheet is not a valid file path. Enter the path of the Excel spreadsheet containing the subjects you want w-maps for.\n')

df = pandas.read_excel(xl_f)            #Read in spreadsheet as dataframe
covs = list(df.columns.values)[1:]      #Read in covariates

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

#If WBD w-maps are wanted, check that each subjdir directory has a whole_brain_degree.nii file necessary for creating the w-maps.
if processing_type == 'WBD':
    print('Checking each subject for whole_brain_degree.nii image...')
    for i in df.ix[:,'subjdir']:
        if os.path.exists(i+'/'+processedfmri_folder+'/whole_brain_degree/whole_brain_degree.nii'):
            pass
        else:
            print('Error--'+i+'/'+processedfmri_folder+'/whole_brain_degree/whole_brain_degree.nii does not exist. Check and try again.')
    print('Finished checking.')

#Prompt user for the directory containing all of the HC regression model files.
HC_model = raw_input('\n3. Enter the directory containing the HC regression model. Please make sure that the order of the covariate columns in your spreadsheet matches the order of the beta maps in your HC regression model. If not, press Control-C to exit.\n')

while not os.path.isdir(HC_model):
    HC_model = raw_input('Error--Specified HC regression model is not a valid directory. Enter the directory containing the HC regression model.\n')
    
#Prompt user for the mask.
mask = raw_input('\n4. Enter the path of the whole brain mask that the w-maps will be masked to. Hit Enter if you do not want to mask your w-maps.\n')

if mask != '' and os.path.isfile(mask) == False:
    mask = raw_input('Error--Specified mask is not a valid file path. Enter the path of the mask.\n')

#Prompt user for a suffix which will be appended to all results folder names.
suffix = raw_input('\n5. Enter a concise descriptive suffix for your w-map analysis results folders. Do not use spaces. (e.g. 12GRNps_vs_120HC)\n')

########################################################### CALCULATIONS ###########################################################################
os.system('fslmaths '+HC_model+'/ResMS.nii -sqrt '+HC_model+'/sqrt_res')       #Calculate denominator for all subjects (HC regr model sqrt residuals map)
denominator = HC_model+'/sqrt_res'

for index,row in df.iterrows():         #Loop through each subject and define paths for FC and GMA options. Then...
    subj = row  
    if processing_type == 'FC':
        wmapdir = subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/wmap_'+suffix
        actual_map = subj['subjdir']+'/'+processedfmri_folder+'/'+seed_folder+'/con_0001.nii'
    elif processing_type == 'GMA':
        wmapdir = os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/wmap_'+suffix
        actual_map = glob.glob(os.path.split(subj['subjdir'])[0]+'/struc/SPM12_SEG_Full/smwc1*')[0]
    elif processing_type == 'WBD':
        wmapdir = subj['subjdir']+'/'+processedfmri_folder+'/whole_brain_degree/wmap_'+suffix
        actual_map = subj['subjdir']+'/'+processedfmri_folder+'/whole_brain_degree/whole_brain_degree.nii'

    if os.path.exists(os.path.join(wmapdir, 'wmap.nii')):                     #...check if they have already been run. Skip if they have, or else...
        print(os.path.split(subj['subjdir'])[0]+' has already been run! Will be skipped.')
    else:
        os.system('mkdir '+wmapdir)                         #...create a "wmap" folder for each subject to catch output
        os.chdir(wmapdir); f = open('log', 'w')             #...open a log file in each subject's "wmap" folder
        map_pred_for_subj = wmapdir+'/map_pred_for_subj'    #...define path for map predicted for subject
        predmaps_for_covs_list = []                         #...calculate each subject's predicted maps for each covariate
        for j in range(1, len(covs)+1):
            beta_map = HC_model+'/beta_000'+str(j+1)+'.nii'
            subj_value = str(subj[j])
            predmap_for_cov = wmapdir+'/predmap_for_'+covs[j-1]
            os.system('fslmaths '+beta_map+' -mul '+subj_value+' '+predmap_for_cov)
            predmaps_for_covs_list.append(predmap_for_cov)
            f.write('fslmaths '+beta_map+' -mul '+subj_value+' '+predmap_for_cov+'\n\n')    #...record commands which create pred maps for each cov
            
        predmaps_for_covs_str = ''                                                          #...turn predicted maps for each covariate into a string
        for k in range(0,len(predmaps_for_covs_list)):
            predmaps_for_covs_str += ' -add '+predmaps_for_covs_list[k]
            
        os.system('fslmaths '+HC_model+'/beta_0001.nii'+predmaps_for_covs_str+' '+map_pred_for_subj)           #...calculate map predicted for subject
        f.write('fslmaths '+HC_model+'/beta_0001.nii'+predmaps_for_covs_str+' '+map_pred_for_subj+'\n\n')      #...record command which creates it
            
        os.system('fslmaths '+map_pred_for_subj+' -sub '+actual_map+' '+wmapdir+'/numerator')            #...calculate numerator (predicted - actual)
        numerator = wmapdir+'/numerator'
        f.write('fslmaths '+map_pred_for_subj+' -sub '+actual_map+' '+wmapdir+'/numerator\n\n')          #...record command which creates numerator
        
        if mask == '':
            os.system('fslmaths '+numerator+' -div '+denominator+' '+wmapdir+'/wmap')                   #...calculate unmasked w-map
            f.write('fslmaths '+numerator+' -div '+denominator+' '+wmapdir+'/wmap')                     #...record command which creates unmasked wmap
        else:
            os.system('fslmaths '+numerator+' -div '+denominator+' -mas '+mask+' '+wmapdir+'/wmap')     #...calculate masked w-map
            f.write('fslmaths '+numerator+' -div '+denominator+' -mas '+mask+' '+wmapdir+'/wmap')       #...record command which creates masked wmap
        f.close()                                                                                       #...close log file
        
        print 'wmap created for '+subj[0]
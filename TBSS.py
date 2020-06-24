import pathlib
from pathlib import Path
import os
import shutil



dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir)
dir_FA = dir+'/FA_images'

# insert the size of the group 1 used in the comparison
n_group1 = input("Please insert number of subjects in group 1:\n")
print(f'You entered {n_group1}')

# insert the size of the group 2 used in the comparison
n_group2 = input("Please insert number of subjects in group 2:\n")
print(f'You entered {n_group2}')

if Path(dir_FA).exists() and Path(dir_FA).is_dir():
	shutil.rmtree(Path(dir_FA))

# creation directory dir_FA
os.mkdir(dir_FA)

# for each patient create a brain mask and the FA image and move them in the new directory created
for patient_dir in os.listdir(dir):
     os.chdir(dir)
     if patient_dir != 'FA_images':
	     
	     print('-'*10 + patient_dir +'-'*10)

	     for file in os.listdir(dir+'/'+patient_dir+'/DTI'):
	             os.chdir(dir+'/'+patient_dir+'/DTI')
	             if file.endswith('preproc.nii.gz'):                        
	                print("[creazione maschera]")
	                os.system('bet '+ file + ' brain_mask.nii.gz -f .1 -F')
	                print("[creazione FA immagine]")
	                os.system('dtifit -k '+ file + ' -o dti -m brain_mask.nii.gz -r data_preproc.bvecs -b data_preproc.bvals' )
	 
	     for file in os.listdir(dir+'/'+patient_dir+'/DTI'):
	             os.chdir(dir+'/'+patient_dir+'/DTI')
	             if file.endswith('FA.nii.gz'):
	                 shutil.move(dir+'/'+patient_dir+'/DTI/'+file, dir_FA+'/'+file)
	                 os.chdir(dir_FA)
	                 os.rename('dti_FA.nii.gz','dti_'+ patient_dir + '_FA.nii.gz')    

# Preprocessing step
os.chdir(dir_FA)
print('-'*10+'Preprocessing'+'-'*10)
os.system('tbss_1_preproc *.nii.gz')

# Registration step
print('-'*10+'Registration'+'-'*10)
os.system('tbss_2_reg -T *.nii.gz')

# Post-registration step
print('-'*10+'Postregistration'+'-'*10)
os.system('tbss_3_postreg -S')

# visualization skeleton 
print('-'*10+'visualization'+'-'*10)
os.chdir(dir_FA+'/stats')
os.system('fsleyes all_FA --displayRange 0 0.8 mean_FA_skeleton --displayRange 0.2 0.8--cmap Green')

# Prestatistic step
print('-'*10+'Prestatistic'+'-'*10)
os.chdir(dir_FA)
os.system('tbss_4_prestats 0.2')

# Statistic step
os.chdir(dir_FA+'/stats')
os.system('design_ttest2 design '+ n_group1 + ' ' + n_group2)
os.system('randomise -i all_FA_skeletonised -o tbss -m mean_FA_skeleton_mask -d design.mat -t design.con -n 500 --T2')

# Results visualization step 
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm mean_FA_skeleton --cmap Green --displayRange 0.2 0.7 tbss_tfce_corrp_tstat1 --cmap Red-Yellow ')

os.system('tbss_fill tbss_tfce_corrp_tstat1 0.95 mean_FA tbss_fill')
os.system('fsleyes mean_FA --displayRange 0 0.6 mean_FA_skeleton --cmap Green --displayRange 0.2 0.7 tbss_fill --cmap Red-Yellow &')
import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs
   
fn_lis_case = 'D:/projects/025_candidate_detection/lis/lis_dcm_cancer_cases_CaseID_hologic.txt'
fn_lis_case = 'D:/projects/025_candidate_detection/lis/s3_ZWA_normal_cases_Regulatory_Quality_2000cases.txt'

b_count_case_not_on_local_only = True

fn_aws_exe = "C:/Program Files/Amazon/AWSCLI/bin/aws.exe"
dir_dbt_local = 'D:/data/Mammo/dbt/'
dir_dbt_s3 = 's3://icadmed.research/Mammo/dbt/'

# outputs:



fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

lis_case = mh.ReadLisFile(fn_lis_case)
n_case = len(lis_case)

lis_case_not_on_local = []

for n in range(n_case):
    case = mh.case2caseID(lis_case[n])
    print('[%4d/%4d] %s' % (n+1, n_case, case))
    
    mfr = mh.find_mfr_from_caseID(case)
    image_folder = '/image/'
    
    dir_recon_local = '%s%s%s%s/reconstructed_slices/' % (dir_dbt_local, mfr, image_folder, case)
    
    # special image folders
    if mfr == 'hologic':
        if not os.path.exists(dir_recon_local):
            dir_recon_local = dir_recon_local.replace(image_folder, '/longitudinal/')
            
    if not os.path.exists(dir_recon_local):
        if b_count_case_not_on_local_only:
            lis_case_not_on_local.append(case)
        else:
            print('downloading from s3...')
            dir_recon_s3 = '%s%s%s%s/reconstructed_slices/' % (dir_dbt_s3, mfr, image_folder, case)
            cmd = '"%s" s3 sync %s %s' % (fn_aws_exe, dir_recon_s3, dir_recon_local)
            #print(cmd)
            mh.run_cmd(cmd)
    #break

if b_count_case_not_on_local_only:
    print('%d cases not on local' % len(lis_case_not_on_local))   
    
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))
import os, time, sys, pydicom
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh
import truth_helper as th

import matplotlib.pyplot as plt

from skimage.draw import polygon
from pydicom.pixel_data_handlers import gdcm_handler
pydicom.config.image_handlers = ['gdcm_handler']

#==============================================================================


# inputs
   
fn_lis_case = 'D:/projects/025_candidate_detection/lis/lis_dcm_cancer_cases_CaseID_hologic.txt'

fn_aws_exe = "C:/Program Files/Amazon/AWSCLI/bin/aws.exe"
dir_dbt_local = 'D:/data/Mammo/dbt/'
dir_dbt_s3 = 's3://icadmed.research/Mammo/dbt/'
dir_tru_root= 'D:/svn/Truth_repos/branches/TomoCAD3p0/dbt/'

n_lesion_slices = int(5)

# outputs:
dir_ann_txt_cancer = 'D:/projects/025_candidate_detection/data/tomo_truth_hologic/ann_txt_cancer/'

dir_slices = 'D:/projects/025_candidate_detection/data/slices/'
dir_mask = 'D:/projects/025_candidate_detection/data/mask/'
dir_contour = 'D:/projects/025_candidate_detection/data/contour/'

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

mh.mkdir(dir_slices)
mh.mkdir(dir_mask)
mh.mkdir(dir_contour)

lis_case = mh.ReadLisFile(fn_lis_case)
n_case = len(lis_case)

for n in range(1484, n_case):
    time_stt_case = time.time()
    
    case = lis_case[n]
    print('[%4d/%4d] %s' % (n+1, n_case, case))
    
    mfr = mh.find_mfr_from_caseID(case)
    image_folder = '/image/'
    
    dir_recon_local = '%s%s%s%s/reconstructed_slices/' % (dir_dbt_local, mfr, image_folder, case)
    
    # special image folders
    if mfr == 'hologic':
        if not os.path.exists(dir_recon_local):
            dir_recon_local = dir_recon_local.replace(image_folder, '/longitudinal/')
            
    if not os.path.exists(dir_recon_local):
        print('%s does not exist' % dir_recon_local)
        break
    
    lis_view = [dir_recon_local+f+'/' for f in os.listdir(dir_recon_local)]
    for view in lis_view:       
        # (1) read dcm
        lis_fn_dcm = [view+f for f in os.listdir(view) if f.endswith('.dcm')]
        if len(lis_fn_dcm) > 1:
            print('need to handle ct type data!!!')
            sys.exit(0)
            
        fn_dcm = lis_fn_dcm[0]
        
        #ds = pydicom.dcmread(fn_dcm)
        #ds = pydicom.dcmread(fn_dcm, stop_before_pixels=True)
        #print(ds.file_meta.TransferSyntaxUID)
        ds = pydicom.read_file(fn_dcm)
        
        volume = np.asarray(ds.pixel_array)
        
        n_slice = volume.shape[0]
        n_row = volume.shape[1]
        n_col = volume.shape[2]
    
        # (2) read annotations
        fn_tru_xml = th.fn_dcm_2_fn_tru_xml(view, dir_dbt_local, dir_tru_root)      
    
        if fn_tru_xml == '':
            mh.print_log_msg(fn_log,'%s has no truth xml' % view)
            continue
            #sys.exit(0)
           
        lis_fn_ann, lis_ann_lesion_uid, lis_ann_lesion_type = th.fn_tru_xml_2_lis_fn_ann(fn_tru_xml, b_cancer_ann_only=True)    
        
        if len(lis_fn_ann) == 0:
            continue
        
        # (3) make slices/mask/contour
        for fn_ann in lis_fn_ann:
            fn_ann_txt = dir_ann_txt_cancer + fn_ann[fn_ann.rfind('/')+1:] + '.txt'
            if not os.path.exists(fn_ann_txt):
                print('%s not exist' % fn_ann_txt)
                peh.convert_ann_to_txt(fn_ann, fn_ann_txt) 

            mtx_lesion_pt = peh.get_ann_contour(fn_ann_txt)                
            
            idx_focus_slice = int(mtx_lesion_pt[0][2]+0.5)
            
            half_lesion_slices = int(n_lesion_slices / 2)
            idx_stt_slice = idx_focus_slice - half_lesion_slices
            idx_stp_slice = idx_focus_slice + half_lesion_slices
            if (idx_stt_slice < 0) or (idx_stp_slice > n_slice-1):
                print('need to take care of lesion slices out of range!!!')
                sys.exit(0)
            
            slices = volume[idx_stt_slice:idx_stp_slice+1, :, :]
            
            fn_slices = dir_slices + fn_ann[fn_ann.rfind('/')+1:] + '_%dx%dx%d.slices' % (n_col, n_row, n_lesion_slices)
            slices.tofile(fn_slices)
            
            mask = np.zeros((n_row, n_col), 'uint8')
            poly = mtx_lesion_pt
            rr, cc = polygon(poly[:,1], poly[:,0], mask.shape)
            mask[rr,cc] = 255
            
            fn_mask = dir_mask + fn_ann[fn_ann.rfind('/')+1:] + '_%dx%d.mask' % (n_col, n_row)
            mask.tofile(fn_mask)
            
            fn_contour = dir_contour + fn_ann[fn_ann.rfind('/')+1:] + '.contour'
            with open(fn_contour, 'wt') as fi:
                for n in range(len(mtx_lesion_pt)):
                    x = int(mtx_lesion_pt[n][0]+0.5)
                    y = int(mtx_lesion_pt[n][1]+0.5)
                    z = int(mtx_lesion_pt[n][2]+0.5)
                    fi.write('%4d %4d %3d\n' % (x, y, z))
                    
#            plt.imshow(mask)
#            plt.set_cmap(plt.gray())
#            plt.show()
            #break
        #break
    print('run time = %.2f sec' % (time.time() - time_stt_case))
    #break
       
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))
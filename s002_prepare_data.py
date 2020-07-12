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
   
#fn_lis_case = 'D:/projects/025_candidate_detection/lis/lis_dcm_cancer_cases_CaseID_hologic.txt'
#b_cancer_lis = True
#b_lesion_info_only = True
fn_lis_case = 'D:/projects/025_candidate_detection/lis/s3_ZWA_normal_cases_Regulatory_Quality_2000cases.txt'
b_cancer_lis = False
#normal_slice_cut_method = 'random'
normal_slice_cut_method = 'top_det'
dir_det_txt = 'D:/projects/025_candidate_detection/data/hologic_ZWA_2000_final_feat_voxel/'

fn_aws_exe = "C:/Program Files/Amazon/AWSCLI/bin/aws.exe"
dir_dbt_local = 'D:/data/Mammo/dbt/'
dir_dbt_s3 = 's3://icadmed.research/Mammo/dbt/'
dir_tru_root= 'D:/svn/Truth_repos/branches/TomoCAD3p0/dbt/'

n_target_slices = int(5)

# outputs:
dir_ann_txt_cancer = 'D:/projects/025_candidate_detection/data/tomo_truth_hologic/ann_txt_cancer/'

fn_lesion_type = 'ann_lesion_type.txt'

#dir_output = 'D:/projects/025_candidate_detection/data/hologic_cancer/'
dir_output = 'D:/projects/025_candidate_detection/data/hologic_ZWA_2000/'
dir_top_det_txt = 'D:/projects/025_candidate_detection/data/hologic_ZWA_2000_top_det_txt/'

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
def prepare_cancer_data(dir_slices, dir_mask, dir_contour, dir_recon_local, n_target_slices, b_lesion_info_only):
    
    lis_ann_lesion_type_case = []
    
    lis_view = [dir_recon_local+f+'/' for f in os.listdir(dir_recon_local)]
    for view in lis_view:       
        # (1) read annotations
        fn_tru_xml = th.fn_dcm_2_fn_tru_xml(view, dir_dbt_local, dir_tru_root)      
    
        if fn_tru_xml == '':
            mh.print_log_msg(fn_log,'%s has no truth xml' % view)
            continue
            #sys.exit(0)
           
        lis_fn_ann, lis_ann_lesion_uid, lis_ann_lesion_type = th.fn_tru_xml_2_lis_fn_ann(fn_tru_xml, b_cancer_ann_only=True)    
        
        if len(lis_fn_ann) == 0:
            continue
        
        for n in range(len(lis_fn_ann)):
            fn_ann = lis_fn_ann[n].split('/')[-1]
            lis_ann_lesion_type_case.append('%s %s' % (fn_ann, lis_ann_lesion_type[n]))
        
        if b_lesion_info_only:
            continue
        
        # (2) read dcm
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
 
        # (3) make slices/mask/contour
        for fn_ann in lis_fn_ann:
            fn_ann_txt = dir_ann_txt_cancer + fn_ann[fn_ann.rfind('/')+1:] + '.txt'
            if not os.path.exists(fn_ann_txt):
                print('%s not exist' % fn_ann_txt)
                peh.convert_ann_to_txt(fn_ann, fn_ann_txt) 

            mtx_lesion_pt = peh.get_ann_contour(fn_ann_txt)                
            
            idx_focus_slice = int(mtx_lesion_pt[0][2]+0.5)
            
            half_lesion_slices = int(n_target_slices / 2)
            idx_stt_slice = idx_focus_slice - half_lesion_slices
            idx_stp_slice = idx_focus_slice + half_lesion_slices
            if (idx_stt_slice < 0) or (idx_stp_slice > n_slice-1):
                print('need to take care of lesion slices out of range!!!')
                sys.exit(0)
            
            slices = volume[idx_stt_slice:idx_stp_slice+1, :, :]
            
            fn_slices = dir_slices + fn_ann[fn_ann.rfind('/')+1:] + '_%dx%dx%d.slices' % (n_col, n_row, n_target_slices)
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
    return lis_ann_lesion_type_case

#==============================================================================
def get_top_det_slice(fn_top_det_txt, fn_det_txt, n_target_slices):
    
    lis_line = mh.ReadLisFile(fn_det_txt)
    for line in lis_line:
        if line.find('aggregate') != -1:
            v_aggregate = np.asarray([float(i) for i in (line.split()[1:-1])])
        if line.find('x_voxel') != -1:
            v_x_voxel = np.asarray([int(float(i)+0.5) for i in (line.split()[1:-1])])
        if line.find('y_voxel') != -1:
            v_y_voxel = np.asarray([int(float(i)+0.5) for i in (line.split()[1:-1])])            
        if line.find('z_voxel') != -1:
            v_z_voxel = np.asarray([int(float(i)+0.5) for i in (line.split()[1:-1])])
        
    if len(set(v_z_voxel)) < n_target_slices:
        n_target_slices = len(set(v_z_voxel))
        
    sort_index = np.argsort(-v_aggregate)

#    print(v_aggregate[:10])
#    print(v_z_voxel[:10])
#    
#    print('\n\n')
    v_aggregate = v_aggregate[sort_index]
    v_x_voxel = v_x_voxel[sort_index]
    v_y_voxel = v_y_voxel[sort_index]
    v_z_voxel = v_z_voxel[sort_index]
    
    for n in range(n_target_slices, len(v_z_voxel)):
        if len(set(v_z_voxel[:n])) == n_target_slices:
            v_top_det_slice = list(set(v_z_voxel[:n]))
            v_top_det_slice.sort()
            
            with open(fn_top_det_txt, 'wt') as fi:
                for m in range(n):
                    fi.write('%4d %4d %3d %.6f\n' % (v_x_voxel[m], v_y_voxel[m], v_z_voxel[m], v_aggregate[m]))
                #print('%4d %4d %3d %.6f' % (v_x_voxel[m], v_y_voxel[m], v_z_voxel[m], v_aggregate[m]))
            break
            
#    print(v_aggregate[:10])
#    print(v_z_voxel[:10])
#    
    
#    print(v_top_det_slice)
#    sys.exit(0)
    
    return v_top_det_slice

#==============================================================================            
def prepare_noncancer_data(dir_slices, dir_recon_local, n_target_slices, 
                           normal_slice_cut_method, lis_fn_det_txt):
    lis_view = [dir_recon_local+f+'/' for f in os.listdir(dir_recon_local)]
    for view in lis_view:       
        tmp = view.split('/')
#        for n in range(len(tmp)):
#            print('[%d][%s]' % (n, tmp[n]))
        case = tmp[6]; mod = tmp[7]; b_view = tmp[8]
        
        view_long_name = '%s_%s_%s' % (case, mod, b_view)
        view_long_name_2 = '%s.%s.%s' % (case, mod, b_view)
        
        # (0) method-dependent data
        if normal_slice_cut_method == 'top_det':
            v_top_det_slice = np.arange(n_target_slices)
            
            for fn_det_txt in lis_fn_det_txt:
                if fn_det_txt.find(view_long_name_2) != -1:
                    #print(fn_det_txt)
                    fn_top_det_txt = fn_det_txt.replace(dir_det_txt, dir_top_det_txt)
                    v_top_det_slice = get_top_det_slice(fn_top_det_txt, fn_det_txt, n_target_slices)
                    break
                
#            print('v_top_det_slice')
#            print(v_top_det_slice)
        
        # (1) read dcm
        lis_fn_dcm = [view+f for f in os.listdir(view) if f.endswith('.dcm')]
        if len(lis_fn_dcm) > 1:
            print('need to handle ct type data!!!')
            sys.exit(0)
        
        fn_dcm = lis_fn_dcm[0]

        ds = pydicom.read_file(fn_dcm)    

        volume = np.asarray(ds.pixel_array)
        
        # (2) cut slices
        n_slice = volume.shape[0]
        n_row = volume.shape[1]
        n_col = volume.shape[2]
        
        if normal_slice_cut_method == 'random':
            half_lesion_slices = int(n_target_slices / 2)
            
            v_idx = np.arange(half_lesion_slices+1, n_slice-half_lesion_slices)
            np.random.shuffle(v_idx)       
            idx_random_focus_slice = v_idx[0]
    
            idx_stt_slice = idx_random_focus_slice - half_lesion_slices
            idx_stp_slice = idx_random_focus_slice + half_lesion_slices
                
            str_idx_slice = str(idx_random_focus_slice)
            
            slices = volume[idx_stt_slice:idx_stp_slice+1, :, :]
        elif normal_slice_cut_method == 'top_det':
            str_idx_slice = str(v_top_det_slice[0])
            for i in range(1, len(v_top_det_slice)):
                str_idx_slice += '_%d' % v_top_det_slice[i]
                
            slices = volume[v_top_det_slice, :, :]
            
        # (3) save to binary file
        fn_slices = dir_slices + view_long_name + '_%s_%dx%dx%d.slices' % (str_idx_slice, n_col, n_row, slices.shape[0])
        
        slices.tofile(fn_slices)
        
#==============================================================================
def main(argv):            
    time_start = time.time()
    
    # 1. get idx_case_stt, idx_case_stp from inputs
    import sys, getopt
    
    idx_case_stt = 0
    idx_case_stp = 0
    
    try:
        opts, args = getopt.getopt(argv,"hs:t:",["i_stt=","i_stp="])
    except getopt.GetoptError:
        print('%s -s <idx_case_stt> -t <idx_case_stp>' % (os.path.basename(__file__)))
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('%s -s <idx_case_stt> -t <idx_case_stp>' % (os.path.basename(__file__)))
            sys.exit()
        elif opt in ("-s", "--stt"):
            idx_case_stt = int(arg)
        elif opt in ("-t", "--stp"):
            idx_case_stp = int(arg)
          
    print('idx_case_stt = %d, idx_case_stp = %d' % (idx_case_stt, idx_case_stp))
    
    # 2. prepare folders/lists
    mh.mkdir(dir_output)
    mh.mkdir(dir_top_det_txt)
    
    dir_slices = dir_output + 'slices/'
    dir_mask = dir_output + 'mask/'
    dir_contour = dir_output + 'contour/'
    
    mh.mkdir(dir_slices)
    if b_cancer_lis:
        mh.mkdir(dir_mask)
        mh.mkdir(dir_contour)
    
    lis_fn_det_txt = ''
    if normal_slice_cut_method == 'top_det':
        lis_fn_det_txt = [dir_det_txt+f for f in os.listdir(dir_det_txt)]
    
    # 3. loop thru cases
    lis_case = mh.ReadLisFile(fn_lis_case)
    n_case = len(lis_case)
    
    lis_ann_lesion_type_all = []
    for n in range(idx_case_stt, min(idx_case_stp, n_case)):
        time_stt_case = time.time()
        
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
            print('%s does not exist' % dir_recon_local)
            break
    
        if b_cancer_lis:
            lis_ann_lesion_type_case = prepare_cancer_data(dir_slices, dir_mask, dir_contour, dir_recon_local, 
                                                           n_target_slices, b_lesion_info_only)
            lis_ann_lesion_type_all += lis_ann_lesion_type_case
        else:
            prepare_noncancer_data(dir_slices, dir_recon_local, n_target_slices, 
                                   normal_slice_cut_method, lis_fn_det_txt) 
    
        print('run time = %.2f sec' % (time.time() - time_stt_case))
        #break
    
    if b_cancer_lis:
        if b_lesion_info_only:                 
            mh.WriteLisFile(fn_lesion_type, lis_ann_lesion_type_all)
    
    mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))
    
if __name__ == "__main__":
   main(sys.argv[1:])    
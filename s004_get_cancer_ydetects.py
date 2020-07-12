import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs  
fn_lis_ann = 'D:/projects/025_candidate_detection/lis/lis_ann_all_tr.txt'
dir_det = 'D:/projects/023_dev_test/PFAI_30_Dev_Train/hologic/'

#fn_lis_ann = 'D:/projects/025_candidate_detection/lis/lis_ann_all_ts.txt'
#dir_det = 'D:/projects/023_dev_test/PFAI_30_Dev_Test/output_v2.1/hologic/'

# outputs:

dir_det_tgt = 'D:/projects/025_candidate_detection/data/det/hologic/'


dir_det = dir_det_tgt


fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

lis_ann = mh.ReadLisFile(fn_lis_ann)
n_ann = len(lis_ann)

for n in range(n_ann):
    ann = lis_ann[n]
    #print('[%4d/%4d] %s' % (n+1, n_ann, ann))
    
    tmp = ann[:ann.find('.')].split('_')
    case = tmp[0]
    view = tmp[3]+'_'+tmp[4]
    
    dir_case = dir_det + case + '/'
    if not os.path.exists(dir_case):
        mh.print_log_msg(fn_log, 'case %s had no detections in %s' % (case, dir_det))
        continue
    
    dir_case_tgt = dir_det_tgt + case + '/'
    mh.mkdir(dir_case_tgt)
    
    fn_ydet = dir_case + '%s.%s.ydetects' % (case, view)
    if not os.path.exists(fn_ydet):
        mh.print_log_msg(fn_log, 'case %s view %s had no ydetects in %s' % (case, view, dir_det))
        continue
    
    if dir_det_tgt != dir_det:
        shutil.copy2(fn_ydet, dir_case_tgt)    
    #break

mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

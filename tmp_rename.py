import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs

dir_1 = 'D:/projects/025_candidate_detection/data/det/hologic/'

# outputs:



fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

lis_ydet = [f for f in os.listdir(dir_1) if f.endswith('ydetects')]

#tomo.reconstructed_slices.LCC_0.ewbth0000798brpb00001.dcm.ydetects
for ydet in lis_ydet:
    tmp = ydet.split('.')
    case = tmp[3][0:len('ewbth0000798b')]
    view = tmp[2]
    fn_src = dir_1 + ydet
    dir_case = dir_1 + case + '/'
    mh.mkdir(dir_case)
    fn_tgt = dir_case + '%s.%s.ydetects' % (case, view)
    shutil.move(fn_src, fn_tgt)
    
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

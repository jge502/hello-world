import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================

tr_or_ts = 'ts'
# inputs
if  tr_or_ts == 'tr':    
    dir_run = 'D:/projects/023_dev_test/PFAI_30_Dev_Train/hologic/' #aecth0000001a/aecth0000001a.LCC_0.denseg
else:
    dir_run = 'D:/projects/023_dev_test/PFAI_30_Dev_Test/output_v2.1/hologic/'

fn_lis_case = 'D:/projects/025_candidate_detection/lis/lis_case_all_%s.txt' % tr_or_ts

# outputs:    
fn_out_unknown = 'lis_case_flip_unknown_%s.txt' % tr_or_ts
fn_out_info = 'flip_info_%s.txt' % tr_or_ts

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

lis_case = mh.ReadLisFile(fn_lis_case)

lis_flip_info = []
lis_case_flip_unknown = []
for case in lis_case:
    dir_case = dir_run + case + '/'
    if not os.path.exists(dir_case):
        lis_case_flip_unknown.append(case)
        continue
        
    lis_fn_denseg = [f for f in os.listdir(dir_case) if f.endswith('.denseg')]
    #print(lis_fn_denseg)
    
    for fn_denseg in lis_fn_denseg:
        lis_line = mh.ReadLisFile(dir_case+fn_denseg)
        tmp = lis_line[0].split()
        for item in tmp:
            if item.find('flip_x') != -1:
                flip_x = item.split(':')[1]
            if item.find('flip_y') != -1:
                flip_y = item.split(':')[1]
         
        lis_flip_info.append('%s flip_x %s flip_y %s' % (fn_denseg, flip_x, flip_y))
        
#        if flip_x == '1' or flip_y == '1':
#            print('%s flip_x %s flip_y %s' % (fn_denseg, flip_x, flip_y))
#            sys.exit(0)
        #print(lis_line)
    
    #break
        
mh.WriteLisFile(fn_out_unknown, lis_case_flip_unknown) 
mh.WriteLisFile(fn_out_info, lis_flip_info)
       
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))
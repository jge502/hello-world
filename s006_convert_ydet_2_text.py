import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs


dir_src = 'D:/projects/025_candidate_detection/data/det/hologic/'
ext_det = '.ydetects'

dir_run = 'D:/projects/025_candidate_detection/script/'

fn_exe = 'D:/projects/015_ipsilateral/exe/dfilter.exe'

# outputs:

dir_tgt = 'D:/projects/025_candidate_detection/data/det_txt/hologic/'

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

   
n_fn_bat = 12
dir_bat = dir_run + '/convert_dets_to_txt_bat/'
mh.mkdir(dir_bat)
fn_bat = dir_bat + 'run_detects_to_feat.bat'
fn_run_all = dir_bat + 'run_all.bat'

#==============================================================================

mh.mkdir(dir_tgt)

lis_case = [f for f in os.listdir(dir_src)]

lis_fn_det = []
for case in lis_case:
    mh.mkdir(dir_tgt+case+'/')
    
    lis_fn_det += [case+'/'+f for f in os.listdir(dir_src+case) if f.endswith(ext_det)]

n_fn_det = len(lis_fn_det)
batch_sz = int(n_fn_det/n_fn_bat)+1

ct_all = 0
with open(fn_run_all, 'wt') as fh:    
    for n in range(n_fn_bat):
        fn_bat_n = fn_bat.replace('.bat', '_%d.bat'%n)
        fh.write('start cmd /K \"%s\"\n' % fn_bat_n)
        
        with open(fn_bat_n, 'wt') as fi:            
            for m in range(n*batch_sz, min((n+1)*batch_sz, n_fn_det)):            
                fi.write('%s -if %s -of %s\n' % \
                         (fn_exe, dir_src+lis_fn_det[m], 
                          dir_tgt+lis_fn_det[m]+'.feature_data.txt'))
            fi.write('exit\n')
        
        lis_line = mh.ReadLisFile(fn_bat_n)
        #print('%4d %s' % (len(lis_line), fn_bat_n) )
        ct_all += (len(lis_line) - 1)

print('%d cmd lines' % ct_all)
    
if ct_all != n_fn_det:
    print(' %d cmd lines != n_fn_det %d ' % (ct_all, n_fn_det))
    sys.exit(0)
    
os.system(fn_run_all.replace('/', '\\'))    

mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs
   
fn_lis_view = 'D:/projects/025_candidate_detection/script/lis_hologic_dcm.txt'

dir_local_root = 'D:/data/Mammo/dbt/'
dir_s3_root = 's3://icadmed.research/Mammo/dbt/'

fn_ccad_exe = 'D:/svn/bin/msvc-x64/dynamic/Release/ccad.exe'
dir_model = 'D:/svn/bin/intel64/models/cad_final/'

# outputs:

dir_out = 'D:/projects/025_candidate_detection/data/det/hologic/'

fn_bat_0 = '%srun_gpu_0.bat' % dir_out
fn_bat_1 = '%srun_gpu_1.bat' % dir_out

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

mh.mkdir(dir_out)

lis_view = mh.ReadLisFile(fn_lis_view)
n_view = len(lis_view)

lis_cmd_gpu_0 = []
lis_cmd_gpu_1 = []
for n in range(n_view):
    view = lis_view[n]
    view = view.split()[0]
    view = view.replace(dir_s3_root, dir_local_root)
    
    view = view[:view.rfind('/')]
    
    tmp = view.split('/')
    
    fn_y = '%stomo.%s.%s.%s.ydetects' % (dir_out, tmp[-3], tmp[-2], tmp[-1])
#    fn_l = fn_y.replace('.y', '.l')
#    fn_m = fn_y.replace('.y', '.m')
#    fn_h = fn_y.replace('.y', '.h')
#    cmd = '%s -if %s -md %s -of %s -ofl %s -ofm %s -ofh %s -gpu %d' % (fn_ccad_exe, view, dir_model, fn_y, fn_l, fn_m, fn_h, n%2)
    cmd = '%s -if %s -md %s -of %s -gpu %d' % (fn_ccad_exe, view, dir_model, fn_y, n%2)
    
    if n%2 == 0:
        lis_cmd_gpu_0.append(cmd)
    else:
        lis_cmd_gpu_1.append(cmd)
        
        
mh.WriteLisFile(fn_bat_0, lis_cmd_gpu_0)
mh.WriteLisFile(fn_bat_1, lis_cmd_gpu_1)
        
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))
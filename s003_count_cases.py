import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs
   
dir_contour = 'D:/projects/025_candidate_detection/data/hologic_cancer/contour/'

fn_lis_ann_lesion_type = 'D:/projects/025_candidate_detection/lis/ann_lesion_type.txt'

# outputs:

# train odd / test even


fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

lis_ann_contour = [f for f in os.listdir(dir_contour)]
lis_ann = []
for c in lis_ann_contour:
    lis_ann.append(c[:c.rfind('.')])    

lis_ann_lesion_type = mh.ReadLisFile(fn_lis_ann_lesion_type)
n_ann_all = len(lis_ann_lesion_type)

lis_ann_all = []
lis_lesion_type_all = []
for ann_lesion_type in lis_ann_lesion_type:
    tmp = ann_lesion_type.split()
    lis_ann_all.append(tmp[0])
    lis_lesion_type_all.append(tmp[1])

lis_ann_calc = []
lis_ann_mass = []
lis_ann_mixed = []    
lis_ann_calc_tr = []
lis_ann_mass_tr = []
lis_ann_mixed_tr = [] 
lis_ann_calc_ts = []
lis_ann_mass_ts = []
lis_ann_mixed_ts = [] 

for ann in lis_ann:
    b_tr = True
    if int(ann[5:12])%2 == 0:
        b_tr = False
        
    b_calc = False
    b_mass = False    
    for n in range(n_ann_all):
        if lis_ann_all[n] == ann:
            if lis_lesion_type_all[n] == 'calc':
                b_calc = True
            if lis_lesion_type_all[n] == 'mass':
                b_mass = True
    if b_calc: 
        lis_ann_calc.append(ann)
        if b_tr:
            lis_ann_calc_tr.append(ann)
        else:
            lis_ann_calc_ts.append(ann)
    if b_mass:
        lis_ann_mass.append(ann)
        if b_tr:
            lis_ann_mass_tr.append(ann)
        else:
            lis_ann_mass_ts.append(ann)        
    if b_calc and b_mass:
        lis_ann_mixed.append(ann)
        if b_tr:
            lis_ann_mixed_tr.append(ann)
        else:
            lis_ann_mixed_ts.append(ann)     
 
lis_ann_all = lis_ann_calc+lis_ann_mass+lis_ann_mixed
lis_ann_all = list(set(lis_ann_all))   
lis_ann_all.sort()
          
lis_ann_all_tr = lis_ann_calc_tr+lis_ann_mass_tr+lis_ann_mixed_tr
lis_ann_all_tr = list(set(lis_ann_all_tr))   
lis_ann_all_tr.sort()
            
lis_ann_all_ts = lis_ann_calc_ts+lis_ann_mass_ts+lis_ann_mixed_ts
lis_ann_all_ts = list(set(lis_ann_all_ts))   
lis_ann_all_ts.sort()
         
print('n_ann_calc = %d' % len(lis_ann_calc))
print('n_ann_mass = %d' % len(lis_ann_mass))
print('n_ann_mixed = %d' % len(lis_ann_mixed))
print('n_ann_all = %d' % len(lis_ann_all))

print('n_ann_calc_tr = %d' % len(lis_ann_calc_tr))
print('n_ann_mass_tr = %d' % len(lis_ann_mass_tr))
print('n_ann_mixed_tr = %d' % len(lis_ann_mixed_tr))
print('n_ann_all_tr = %d' % len(lis_ann_all_tr))

print('n_ann_calc_ts = %d' % len(lis_ann_calc_ts))
print('n_ann_mass_ts = %d' % len(lis_ann_mass_ts))
print('n_ann_mixed_ts = %d' % len(lis_ann_mixed_ts))
print('n_ann_all_ts = %d' % len(lis_ann_all_ts))

lis_name_lis_ann = []
lis_name_lis_ann.append('lis_ann_calc')
lis_name_lis_ann.append('lis_ann_mass')
lis_name_lis_ann.append('lis_ann_mixed')
lis_name_lis_ann.append('lis_ann_all')
lis_name_lis_ann.append('lis_ann_calc_tr')
lis_name_lis_ann.append('lis_ann_mass_tr')
lis_name_lis_ann.append('lis_ann_mixed_tr')
lis_name_lis_ann.append('lis_ann_all_tr')
lis_name_lis_ann.append('lis_ann_calc_ts')
lis_name_lis_ann.append('lis_ann_mass_ts')
lis_name_lis_ann.append('lis_ann_mixed_ts')
lis_name_lis_ann.append('lis_ann_all_ts')

def get_n_case(lis_ann, fn_case):
    lis_case = []
    lis_view = []
    for ann in lis_ann:
        #aecth0000001a_reconstructed_slices_RCC_0.2541856002329.ann
        lis_view.append(ann[:ann.find('.')])
        lis_case.append(ann[:ann.find('_')])
    
    lis_case = list(set(lis_case))
    lis_case.sort()

    lis_view = list(set(lis_view))
    lis_view.sort()
    
    mh.WriteLisFile(fn_case, lis_case)
    mh.WriteLisFile(fn_case.replace('_case_', '_view_'), lis_view)
    
    return len(lis_case)

for name_lis_ann in lis_name_lis_ann:
    #print(name_lis_ann)
    fn_case = name_lis_ann.replace('_ann_', '_case_')+'.txt'
    exec('n_case = get_n_case(%s, fn_case)' % name_lis_ann)
    print('%s n_case = %d' % (name_lis_ann, n_case))
    
    fn = '%s.txt' % name_lis_ann
    exec('mh.WriteLisFile("%s", %s)' % (fn, name_lis_ann))
    
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

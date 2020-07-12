import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh

from matplotlib import pyplot as plt

#==============================================================================

# inputs
   
dir_mask = 'D:/projects/025_candidate_detection/data/hologic_cancer/mask/'

# outputs:

fn_ann_pixel = 'hologic_3229_ann_nonzero_pixel.txt'

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

if 0:
    lis_fn_mask = [f for f in os.listdir(dir_mask)]
    n_fn_mask = len(lis_fn_mask)
    
    lis_ann_pixel = []
    for n in range(n_fn_mask):
        fn_mask = lis_fn_mask[n]
        print('[%4d/%4d] %s' % (n+1, n_fn_mask, fn_mask))
        
        img = np.fromfile(dir_mask+fn_mask, dtype=np.uint8)
        n_nonzero_pixel = np.sum(img>0)
        
        lis_ann_pixel.append('%s %d' % (fn_mask, n_nonzero_pixel))
        #break
    
    mh.WriteLisFile(fn_ann_pixel, lis_ann_pixel)

lis_ann_pixel_all = mh.ReadLisFile(fn_ann_pixel)


lis_lesion_type = ['all', 'calc', 'mass']
lis_lesion_type = ['mixed']
lis_tr_or_ts = ['tr', 'ts']

for lesion_type in lis_lesion_type:
    plt.clf()    
    
    bin_ctr = int(0)
    bin_width = 0.35
    for tr_or_ts in lis_tr_or_ts:
        fn_lis_ann = 'D:/projects/025_candidate_detection/lis/lis_ann_%s_%s.txt' % (lesion_type, tr_or_ts)
        lis_ann = mh.ReadLisFile(fn_lis_ann)
        
        lis_n_pixel = []
        for ann in lis_ann:
            for ann_pixel in lis_ann_pixel_all:
                if ann_pixel.find(ann) != -1:
                    lis_n_pixel.append(float(ann_pixel.split()[1])*0.07*0.07)
        
        v_area = np.asanyarray(lis_n_pixel)
        bin_edge = [0, 20, 40, 60, 80, 100, 200, 300, 400, 4000]
        v_hist, bin_edge = np.histogram(v_area, bins=bin_edge)
        
        n_bin = len(v_hist)
        v_bin_range = []
        for n in range(n_bin):
            v_bin_range.append('[%d,%d]' % (bin_edge[n], bin_edge[n+1]))
        
        plt.bar(np.arange(n_bin)+bin_ctr, v_hist/sum(v_hist)*100, bin_width, label=tr_or_ts)
        
        bin_ctr += bin_width
        
    plt.xticks(np.arange(n_bin)+bin_width/2, v_bin_range, rotation=30)
    plt.xlabel('Annotation Area ($mm^2$)')
    plt.ylabel('Percentage')
    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Distribution of Lesion Annotation Area (%s)' % lesion_type)    
        
    plt.savefig('distr_lesion_ann_area_%s.png' % lesion_type)
    #break
        
        
mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

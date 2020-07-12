import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs


n_lesion_slice = int(15)

fn_lis_ann_hit_score = 'D:/projects/025_candidate_detection/script/hologic_ann_hit_score_%d_slices.txt' % n_lesion_slice

dir_normal_det = 'D:/projects/025_candidate_detection/data/hologic_ZWA_2000_top_det_txt/'
fn_normal_score = 'D:/projects/025_candidate_detection/script/hologic_ZWA_8004_scores.txt'
n_normal_view = 8004

# outputs:



fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
time_start = time.time()

if 0:
    lis_fn_normal_det = [f for f in os.listdir(dir_normal_det)]
    
    lis_score_all = []
    for fn_normal_det in lis_fn_normal_det:
        m_det = np.loadtxt(dir_normal_det + fn_normal_det)
        lis_score = m_det[:, 3].tolist()
        
        lis_score_all += lis_score
        #break
        
    np.savetxt('hologic_ZWA_8004_scores.txt', lis_score_all, fmt='%f')

lesion_type = 'all'
tr_or_ts = 'all'

lis_lesion_type = ['all', 'calc', 'mass', 'mixed']
lis_tr_or_ts = ['all', 'tr', 'ts']

for lesion_type in lis_lesion_type:
            
    import matplotlib.pyplot as plt
    plt.clf()    
    
    for tr_or_ts in lis_tr_or_ts:
        fn_lis_ann = 'D:/projects/025_candidate_detection/lis/lis_ann_%s_%s.txt' % (lesion_type, tr_or_ts)
 
        v_normal_score = np.loadtxt(fn_normal_score)
        
        lis_ann_hit_score = mh.ReadLisFile(fn_lis_ann_hit_score)
        lis_ann = mh.ReadLisFile(fn_lis_ann)
        n_ann = len(lis_ann)
        
        v_ann_score = np.zeros(n_ann)
        for n in range(n_ann):
            ann = lis_ann[n]
            b_found_ann = False
            for ann_hit_score in lis_ann_hit_score:
                if ann_hit_score.find(ann) != -1:
                    v_ann_score[n] =  ann_hit_score.split()[1]
                    b_found_ann = True
                    break
                
            if not b_found_ann:
                print('%s has no score in %s' % (ann, fn_lis_ann_hit_score))
                sys.exit(0)
                
        v_th = list(set(v_ann_score.tolist()))
        v_th.sort()
        v_th[0] = min(v_th[1], min(v_normal_score))
        
        n_th = len(v_th)
        v_sen = np.zeros(n_th)
        v_fpi = np.zeros(n_th)
        for n in range(n_th):
            v_sen[n] = np.sum(v_ann_score >= v_th[n]) / n_ann 
            v_fpi[n] = np.sum(v_normal_score >= v_th[n]) / n_normal_view

        plt.plot(v_fpi, v_sen*100)
        plt.axis([0, 10, 0, 100])
        plt.xlabel('FP rate on top-rank det 5 slices')
        plt.ylabel('Lesion Sensitivity (%)')
        plt.title('Hologic %s Lesion FROC (only count hits on focus slice +/-%d slices)' \
                  % (lesion_type, int(n_lesion_slice/2)), fontsize=10)
        plt.grid(True)
        
    plt.legend(['tr+ts', 'tr', 'ts'])
    plt.savefig('hologic_%s_lesion_cg_froc.png' % (lesion_type))
    plt.axis([0, 10, 80, 100])
    plt.savefig('hologic_%s_lesion_cg_froc_zoom.png' % (lesion_type))

mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

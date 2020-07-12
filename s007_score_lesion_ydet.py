import os, time, sys, shutil
dir_common = 'D:/code/python/common/'
if not dir_common in sys.path:
    sys.path.append(dir_common)
import numpy as np
    
import MyHelper as mh
import perf_eval_helper as peh


#==============================================================================


# inputs
dir_ann_contour = 'D:/projects/025_candidate_detection/data/hologic_cancer/contour/'
#aecth0000001a_reconstructed_slices_RCC_0.2541856002329.ann.contour   
n_lesion_slice = int(15)

dir_det_txt = 'D:/projects/025_candidate_detection/data/det_txt/hologic/'

# outputs:

fn_ann_hit_score = 'hologic_ann_hit_score_%d_slices.txt' % n_lesion_slice

fn_log = (os.path.basename(__file__)).replace('.py', '.log.txt')

#==============================================================================
#   NO NEED TO CHANGE BELOW THIS LINE
#==============================================================================
def clip_dets(m_det, v_aggregate, col_idx, min_val, max_val):
    idx = np.where(m_det[:,col_idx] <= max_val)
    m_det = m_det[idx]
    v_aggregate = v_aggregate[idx]
    
    idx = np.where(m_det[:,col_idx] >= min_val)
    m_det = m_det[idx]
    v_aggregate = v_aggregate[idx]
    
    return m_det, v_aggregate
#==============================================================================
    
def get_ann_hit_score(fn_ann_contour, fn_det_txt, n_lesion_slice):
    m_contour = np.loadtxt(fn_ann_contour, dtype=np.int)
    min_contour = np.min(m_contour, 0)
    max_contour = np.max(m_contour, 0)
    
    lesion_top_slice = max_contour[2] + int(n_lesion_slice/2)
    lesion_btm_slice = min_contour[2] - int(n_lesion_slice/2)
    
    #print('%d, %d, %d, %d' % (min_contour[2], n_lesion_slice, lesion_top_slice, lesion_btm_slice))
    
    #print(min_contour)
    #print(max_contour)
    
    lis_line = mh.ReadLisFile(fn_det_txt)
    for line in lis_line:
        line = line[line.find(']')+1:]
        if line.find('aggregate') != -1:
            v_aggregate = np.asarray([float(i) for i in (line.split()[:-1])])
        if line.find('x_sample_original') != -1:
            v_x_voxel = np.asarray([int(float(i)+0.5) for i in (line.split()[:-1])])
        if line.find('y_sample_original') != -1:
            v_y_voxel = np.asarray([int(float(i)+0.5) for i in (line.split()[:-1])])            
        if line.find('z_sample_original') != -1:
            v_z_voxel = np.asarray([int(float(i)+0.5) for i in (line.split()[:-1])])
    
    n_det = len(v_x_voxel)
    m_det = np.zeros((n_det, 3), dtype=np.int)
    m_det[:, 0] = v_x_voxel
    m_det[:, 1] = v_y_voxel
    m_det[:, 2] = v_z_voxel
    
    m_det, v_aggregate = clip_dets(m_det, v_aggregate, 2, lesion_btm_slice, lesion_top_slice)    
    #print(m_det); print(v_aggregate); print('\n');

    m_det, v_aggregate = clip_dets(m_det, v_aggregate, 0, min_contour[0], max_contour[0])    
    #print(m_det); print(v_aggregate); print('\n');

    m_det, v_aggregate = clip_dets(m_det, v_aggregate, 1, min_contour[1], max_contour[1])    
    #print(m_det); print(v_aggregate); print('\n');
    
    if len(v_aggregate) == 0:
        ann_hit_score = 0
    else:
        ann_hit_score = max(v_aggregate)
    
    return ann_hit_score

#==============================================================================
time_start = time.time()

lis_fn_ann_contour = [f for f in os.listdir(dir_ann_contour)]
n_ann = len(lis_fn_ann_contour)

lis_fn_ann_hit_score = []
for n in range(n_ann):
    fn_ann_contour = lis_fn_ann_contour[n]
    fn_ann = fn_ann_contour[:fn_ann_contour.rfind('.')]
    print('[%4d/%4d] %s' % (n+1, n_ann, fn_ann))

    tmp = fn_ann[:fn_ann.find('.')].split('_')
    case = tmp[0]
    view = tmp[3]+'_'+tmp[4]
    
    fn_det_txt = '%s%s/%s.%s.ydetects.feature_data.txt' % (dir_det_txt, case, case, view)
    
    if not os.path.exists(fn_det_txt):
        mh.print_log_msg(fn_log, '%s has no det in %s' % (fn_ann, dir_det_txt))
    
    ann_hit_score = get_ann_hit_score(dir_ann_contour+fn_ann_contour, fn_det_txt, n_lesion_slice)
    
    #print('ann_hit_score = %f' % ann_hit_score)
    lis_fn_ann_hit_score.append('%s %f' % (fn_ann, ann_hit_score))
    
    #break

mh.WriteLisFile(fn_ann_hit_score, lis_fn_ann_hit_score)

mh.print_log_msg(fn_log, 'run time = %.2f sec' % (time.time() - time_start))

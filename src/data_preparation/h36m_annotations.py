'''
Code adapted from dataset provided by https://github.com/juyongchang/PoseLifter

-- Use this file to extract annotations as h5 files, view samples of the data without additional preprocessing
(only includes processing done by Pose lifter)

-- Use to create mean and variance of the 2D/3D pose per joint or across the whole dataset
'''

import os
import sys

import h5py
import numpy as np
import scipy.io as sio
from src.data_preparation.camera_parameters import get_camera_data
###############################################################
# Set Paths
img_path = f'{os.getenv("HOME")}/lab/HPE_datasets/h36m/'
save_path = f'{os.getenv("HOME")}/lab/HPE3D/src/data/'
annot_name = 'matlab_meta_new.mat'

# Set Annotations to retrieve
subject_list = [9, 11]
subject_list = [1, 5, 6, 7, 8]
subj_str = "".join(str(x) for x in subject_list)
h5name = 'h36m17_' + subj_str
inds = range(17)
action_list = np.arange(2, 17)
subaction_list = np.arange(1, 3)
camera_list = np.arange(1, 5)

# Get smaller subset of the data for fast dev?
debug = False
# Get Mean and Std of the data alone?
mean_std = False

#################################################################

if debug:
    h5name = "debug_" + h5name

if not os.path.exists(save_path):
    os.mkdir(save_path)

idx = []
pose2d = []
pose3d = []
pose3d_global = []
bbox = []
cam_f = []
cam_c = []
cam_R = []
cam_T = []
cam_p = []
cam_k = []
subject = []
action = []
subaction = []
camera = []
num_samples = 0

for subject_ in subject_list:
    for action_ in action_list:
        for subaction_ in subaction_list:
            for camera_ in camera_list:
                dir_name = 's_%02d_act_%02d_subact_%02d_ca_%02d' % (
                    subject_, action_, subaction_, camera_)
                print(dir_name)
                annot_file = img_path + dir_name + '/' + annot_name
                try:
                    data = sio.loadmat(annot_file)
                except:
                    print('pass %s' % dir_name)
                    continue
                pose2d_ = np.transpose(data['pose2d'], (2, 1, 0))
                pose3d_ = np.transpose(data['pose3d'], (2, 1, 0))
                pose3d_global_ = np.transpose(data['pose3d_global'], (2, 1, 0))
                bbox_ = data['bbox']
                cam_f_ = data['f']
                cam_c_ = data['c']
                cam_R_ = data['R']
                cam_T_ = data['T']
                cam_p_ = get_camera_data(camera_, subject_, 'p')
                cam_k_ = get_camera_data(camera_, subject_, 'k')
                num_images = pose2d_.shape[2]
                for i in range(num_images):
                    if i % 5 != 0:
                        continue
                    idx.append(i+1)
                    pose2d.append(pose2d_[inds, :, i])
                    pose3d.append(pose3d_[inds, :, i])
                    pose3d_global.append(pose3d_global_[inds, :, i])
                    bbox.append(bbox_[i].astype(int))
                    cam_f.append(cam_f_[i])
                    cam_c.append(cam_c_[i])
                    cam_R.append(cam_R_[i])
                    cam_T.append(cam_T_[i])
                    cam_p.append(cam_p_)
                    cam_k.append(cam_k_)
                    subject.append(subject_)
                    action.append(action_)
                    subaction.append(subaction_)
                    camera.append(camera_)
                    num_samples += 1

                    print(subject_, action_, pose3d_.shape)

                    #############################################################
                    # Comment or uncomment these debug conditions to change the debug dataset distribution

                    if debug:
                        break
                if debug:
                    break
            if debug:
                break
        # if debug:
        #     break
    # if debug:
    #     break

print(f'{dir_name}  number of samples = %d' % num_samples)

if mean_std:
    # Not going to use this anymore
    sys.path.append(f'{os.getenv("HOME")}/lab/HPE3D/src/')

    from processing import zero_the_root 
    
    # Zero the root 
    pose2d = zero_the_root(np.asarray(pose2d))
    pose3d = zero_the_root(np.asarray(pose3d))
    # Standardize the poses
    # max2d = pose2d.max()
    # max3d = pose3d.max()
    # pose2d = pose2d/max2d
    # pose3d = pose3d/max3d
    # mean and std to normalize at this point
    norm_stats = {}
    norm_stats['mean2d'] = np.mean(pose2d, axis=(0))
    norm_stats['mean3d'] = np.mean(pose3d, axis=(0))
    norm_stats['std2d'] = np.std(pose2d, axis=(0))
    norm_stats['std3d'] = np.std(pose3d, axis=(0))
    # norm_stats['max2d'] = max2d
    # norm_stats['max3d'] = max3d
    # norm_stats['mean_dist2d'] = np.mean(np.sqrt(np.sum(np.power(np.subtract(pose2d, np.zeros((1,2))), 2), axis=2)), axis=1)
    # norm_stats['mean_dist3d'] = np.mean(np.sqrt(np.sum(np.power(np.subtract(pose3d, np.zeros((1,3))), 2), axis=2)), axis=1)   

    f = h5py.File(f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/data/norm_stats.h5", 'w')
    for key in norm_stats.keys():
        f[key] = norm_stats[key]
    f.close()
    print("Saved to", f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/data/norm_stats.h5")
    exit()

f = h5py.File(save_path+h5name+'.h5', 'w')
f['idx'] = idx
f['pose2d'] = pose2d
f['pose3d'] = pose3d
f['pose3d_global'] = pose3d_global
f['bbox'] = bbox
f['cam_f'] = cam_f
f['cam_c'] = cam_c
f['cam_R'] = cam_R
f['cam_T'] = cam_T
f['cam_p'] = cam_p
f['cam_k'] = cam_k
f['subject'] = subject
f['action'] = action
f['subaction'] = subaction
f['camera'] = camera
f.close()

print(f"Saved to {save_path+h5name+'.h5'}")

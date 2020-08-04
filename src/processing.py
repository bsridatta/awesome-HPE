'''
Reference code - https://github.com/una-dinosauria/3d-pose-baseline
'''
import gc
import os

import h5py
import numpy as np
import torch

path = f"{os.path.dirname(os.path.abspath(__file__))}/data/norm_stats.h5"
if os.path.exists(path):
    f = h5py.File(path, 'r')

    NORM_STATS = {}
    for key in f.keys():
        NORM_STATS[key] = f[key][:]
    f.close()


ROOT_INDEX = 0  # Root at Pelvis index 0


def zero_the_root(pose, root_idx=ROOT_INDEX):
    '''
    center around root - pelvis

    Arguments:
        pose (numpy) -- array of poses
        root_idx (int) -- index of root(pelvis)

    Returns:
        pose (numpy) -- poses with root shifted to origin,
                        w/o root as always 0 
    '''
    # center at root
    for i in range(pose.shape[0]):
        pose[i, :, :] = pose[i, :, :] - pose[i, root_idx, :]

    # remove root
    pose = np.delete(pose, root_idx, 1)  # axis -> [n, j, x/y]

    return pose


def normalize(pose):
    '''
    using the mean and std of h3.6m trainig poses after zeroing the root and standarding
    refer -- src/data_preparation/h36m_annotations.py

    Arguments:
        pose (numpy) -- array of 2/3d poses with 16 joints w/o root [n, 16, 2/3]
    Returns:
        pose (numpy) -- array of normalized pose
    '''
    mean = NORM_STATS[f"mean{pose.shape[2]}d"]
    pose = (pose - NORM_STATS[f"mean{pose.shape[2]}d"]
            )/NORM_STATS[f"std{pose.shape[2]}d"]

    return pose


def denormalize(pose):
    """ De-Standardize and then 
    Denormalize poses for evaluation of actual pose.  

    Args:
        pose (numpy): 2d/3d pose [n, 16, 2/3]

    Returns:
       numpy : denormalized pose [n, 16, 2/3]
    """

    # pose *= torch.tensor(norm_stats_val[f"mean_dist{pose.shape[2]}d"],
    #                      device=pose.device).reshape((-1, 1, 1))

    pose *= torch.tensor(NORM_STATS[f"std{pose.shape[2]}d"],
                         device=pose.device)
    pose += torch.tensor(NORM_STATS[f"mean{pose.shape[2]}d"],
                         device=pose.device)

    return pose


def preprocess(annotations, root_idx=ROOT_INDEX, normalize_pose=True):
    '''
    Preprocessing steps on -
    pose3d - 3d pose in camera frame(data already coverted from world to camera)
    pose2d - 2d poses obtained by projection of above 3d pose using camera params

    Arguments:
        annotations (dic) -- dictionary of all data excluding raw images

    Returns:
        annotations (dic) -- with normalized 16 joint 2d and 3d poses
    '''
    # center the 2d and 3d pose at the root and remove the root
    pose2d = zero_the_root(annotations['pose2d'], root_idx)
    pose3d = zero_the_root(annotations['pose3d'], root_idx)

    if normalize_pose:
        # Standardize
        # mean_dist2d = np.mean(np.sqrt(
        #     np.sum(np.power(np.subtract(pose2d, np.zeros((1, 2))), 2), axis=2)), axis=1)
        # mean_dist3d = np.mean(np.sqrt(
        #     np.sum(np.power(np.subtract(pose3d, np.zeros((1, 3))), 2), axis=2)), axis=1)
        # pose2d = pose2d/mean_dist2d.reshape(-1, 1, 1)
        # pose3d = pose3d/mean_dist3d.reshape(-1, 1, 1)

        # # Normalize
        pose2d = normalize(pose2d)
        pose3d = normalize(pose3d)

    annotations['pose2d'] = pose2d
    annotations['pose3d'] = pose3d

    return annotations


def post_process(config, recon, target):
    '''
    DeNormalize Validation Data
    Add root at 0,0,0
    '''

    # de-normalize data to original coordinates
    recon = denormalize(recon)
    target = denormalize(target)

    # # # de-standardize
    # recon = recon*torch.tensor(NORM_STATS[f"max3d"],
    #                      device=recon.device)
    # target = target*torch.tensor(NORM_STATS[f"max3d"],
    #                      device=target.device)

    # since the MPJPE is computed for 17 joints with roots aligned i.e zeroed
    # Not very fair, but the average is with 17 in the denom after adding root joiny at zero!
    recon = torch.cat(
        (torch.zeros(recon.shape[0], 1, recon.shape[2], device=config.device), recon), dim=1)
    target = torch.cat(
        (torch.zeros(target.shape[0], 1, recon.shape[2], device=config.device), target), dim=1)

    return recon, target


def normalize_image(img, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), max_pixel_value=255.0):
    """Code from Albumentations

    Arguments:
        img {Tensor} -- Image sample

    Keyword Arguments:
        mean {tuple} -- Mean of ImageNet used in albumentations (default: {(0.485, 0.456, 0.406)})
        std {tuple} -- Std of ImageNet (default: {(0.229, 0.224, 0.225)})
        max_pixel_value {float} -- Max value before normalization (default: {255.0})

    Returns:
        Tensor -- Normalized image
    """
    mean = np.array(mean, dtype=np.float32)
    mean *= max_pixel_value

    std = np.array(std, dtype=np.float32)
    std *= max_pixel_value

    denominator = np.reciprocal(std, dtype=np.float32)

    img = img.astype(np.float32)
    img -= mean
    img *= denominator

    return img

def project_3d_to_2d(pose3d, cam_params, coordinates="camera"):
    """
    Project 3d pose from camera coordiantes to image frame
    using camera parameters including radial and tangential distortion

    Args:
        P: Nx3 points in camera coordinates
        cam_params (dic):
            R: 3x3 Camera rotation matrix
            T: 3x1 Camera translation parameters
            f: 2x1 Camera focal length accounting imprection in x, y
            c: 2x1 Camera center
            k: 3x1 Camera radial distortion coefficients
            p: 2x1 Camera tangential distortion coefficients

    Returns:
        Proj: Nx2 points in pixel space
        D: 1xN depth of each point in camera space
        radial: 1xN radial distortion per point
        tan: 1xN tangential distortion per point
        r2: 1xN squared radius of the projected points before distortion
    """
    f = cam_params['cam_f'].view(-1, 1, 2)
    c = cam_params['cam_c'].view(-1, 1, 2)
    p = cam_params['cam_p'].view(-1, 1, 2)
    k = cam_params['cam_k'].view(-1, 1, 3)

    if coordinates == 'world':  # rotate and translate
        R = cam_params('cam_R')
        T = cam_params('cam_T')
        X = R.dot(torch.transpose(pose3d, 1, 2) - T)
    
    pose2d_proj = (pose3d/pose3d[:,:,2][:,:,None].repeat(1,1,3))[:,:,:2]
    
    f = 1
    # c = 0
    pose2d_proj = f * pose2d_proj + c
    return pose2d_proj

def project_3d_to_2d_martinez(pose3d, cam_params, coordinates="camera"):
    """
    from https://github.com/una-dinosauria/3d-pose-baseline

    Project 3d pose from camera coordiantes to image frame
    using camera parameters including radial and tangential distortion

    Args:
        P: Nx3 points in camera coordinates
        cam_params (dic):
            R: 3x3 Camera rotation matrix
            T: 3x1 Camera translation parameters
            f: 2x1 Camera focal length accounting imprection in x, y
            c: 2x1 Camera center
            k: 3x1 Camera radial distortion coefficients
            p: 2x1 Camera tangential distortion coefficients

    Returns:
        Proj: Nx2 points in pixel space
        D: 1xN depth of each point in camera space
        radial: 1xN radial distortion per point
        tan: 1xN tangential distortion per point
        r2: 1xN squared radius of the projected points before distortion
    """
    f = cam_params['cam_f'].view(-1, 2, 1)
    c = cam_params['cam_c'].view(-1, 2, 1)
    p = cam_params['cam_p'].view(-1, 2, 1)
    k = cam_params['cam_k'].view(-1, 3, 1)

    if coordinates == 'world':  # rotate and translate
        R = cam_params('cam_R')
        T = cam_params('cam_T')
        X = R.dot(torch.transpose(pose3d, 1, 2) - T)

    N = pose3d.shape[1]     
    X = torch.transpose(pose3d, 1, 2)
    
    XX = X[:, :2, :] / X[:, 2, :][:,None,:].repeat(1,2,1)
    r2 = XX[:, 0, :]**2 + XX[:, 1, :]**2

    radial = 1 + torch.einsum('bij,bij->bj', k.repeat(1, 1, N),
                              torch.cat([r2, r2**2, r2**3], dim=0).view(-1, 3, N))

    tan = p[:, 0]*XX[:, 1, :] + p[:, 1]*XX[:, 0, :]

    XXX = XX * (radial+tan)[:,None,:].repeat(1, 2, 1) + \
        torch.cat([p[:, 1], p[:, 0]], dim=1)[:, :, None] @ r2[:, None, :]

    # pose2d_proj = (1 * XXX) + 0
    pose2d_proj = (f * XXX) + c
    pose2d_proj = torch.transpose(pose2d_proj, 1, 2)

    D = X[:, 2, ]

    # return pose2d_proj, D, radial, tan, r2
    return pose2d_proj

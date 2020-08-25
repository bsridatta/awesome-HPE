import os

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from torchvision import transforms
from src.processing import project_3d_to_2d
import torch

SKELETON_COLORS = ['b', 'b', 'b', 'b', 'orange', 'orange', 'orange',
                   'b', 'b', 'b', 'b', 'b', 'b', 'orange', 'orange', 'orange', 'orange']
SKELETON = ((0, 7), (7, 8), (8, 9), (9, 10), (8, 11), (11, 12), (12, 13),
            (8, 14), (14, 15), (15, 16), (0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6))
LABELS = ('Pelvis', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee', 'L_Ankle', 'Torso', 'Neck',
          'Nose', 'Head', 'L_Shoulder', 'L_Elbow', 'L_Wrist', 'R_Shoulder', 'R_Elbow', 'R_Wrist')


def plot_2d(pose, mode="show", color=None, labels=False, show_ticks=False, mean_root=False):
    """Base function for 2D pose plotting

    Args:
        pose (array): for 16 joints its numpy array (for adding root joint)
                      else tensor also works
        mode (str, optional): choose from
            Image: plot -> png -> image tensor, useful for latent space viz 
            Axis: return only the matplotlib axis to plot via caller method.
            Show: Just show the plot 

        color (str, optional): color of pose useful for comparision when overlayed
        labels (bool, optional): Show joint labels
        show_ticks (bool, optional): Show coordinates

    Returns:
        Tensor/MatplotlibAxis: Depends on the mode
    """

    fig = plt.figure(1, figsize=(19.20, 10.80))
    ax = fig.gca()
    plt.tight_layout()
    ax.set_aspect('equal')
    # plt.cla()

    if color:
        colors = [color]*len(SKELETON_COLORS)
    else:
        colors = SKELETON_COLORS

    if pose.shape[0] == 16:
        if mean_root:
            root = (pose[0] + pose[3])/2
            pose = np.concatenate((root.reshape((1, 2)), pose), axis=0)
            (colors[0], colors[10], colors[13]) = 'pink', 'pink', 'pink'
        else:
            pose = np.concatenate((np.zeros((1, 2)), pose), axis=0)

    x = pose[:, 0]
    y = pose[:, 1]
    # Image coordinates origin on the top left corner
    # Hence keypoints value increases as we move down to the bottom of the images
    # Hence after 0ing legs would be positive and head would be negative
    ax.scatter(x, y, alpha=0.6, s=2)
    plt.gca().invert_yaxis()

    for link, color in zip(SKELETON, colors):
        ax.plot(x[([link[0], link[1]])],
                y[([link[0], link[1]])],
                c=color, alpha=0.6, lw=3)

    if labels:
        for i, j, l in zip(x, y, LABELS):
            ax.text(i, j, s=f"{l[:4], i, j}", size=8, zorder=1, color='k')

    if show_ticks:
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')

    if not show_ticks:
        ax.set_xticks([])
        ax.set_yticks([])

    if mode == 'axis':
        return ax

    elif mode == 'show':
        plt.show()

    elif mode == "image":
        DPI = fig.get_dpi()
        fig.set_size_inches(305.0/float(DPI), 305.0/float(DPI))
        fig.savefig(f"{os.getenv('HOME')}/lab/HPE3D/src/results/x.png")
        fig.clf()
        image = Image.open(f"{os.getenv('HOME')}/lab/HPE3D/src/results/x.png")
        image = image.convert('RGB')
        image = transforms.ToTensor()(image).unsqueeze_(0)
        return image

    elif mode == "plt":
        return plt

    else:
        raise ValueError("Please choose from 'image', 'show', 'axis' only")


def plot_3d(pose, root_z=10, mode="show", color=None, floor=False, axis3don=True, labels=False, show_ticks=False, mean_root=False):
    """Base function for 3D pose plotting

    Args:
        pose (array): for 16 joints its numpy array (for adding root joint)
                      else tensor also works
        mode (str, optional): choose from
            image: plot -> png -> image tensor, useful for latent space viz 
            sxis: return only the matplotlib axis to plot via caller method.
            show: Just show the plot 
            plt: return plt instance for logging to wandb

        color (str, optional): color of pose useful for comparision when overlayed
        labels (bool, optional): Show joint labels
        show_ticks (bool, optional): Show coordinates

    Returns:
        Tensor/MatplotlibAxis: Depends on the mode
    """
    fig = plt.figure(1, figsize=(19.20, 10.80))
    ax = fig.gca(projection='3d')
    ax._axis3don = axis3don
    plt.tight_layout()

    if color:
        colors = [color]*len(SKELETON_COLORS)
    else:
        colors = SKELETON_COLORS

    if pose.shape[0] == 16:
        if mean_root:
            root = (pose[0] + pose[3])/2
            pose = np.concatenate((root.reshape((1, 3)), pose), axis=0)
            (colors[0], colors[10], colors[13]) = 'pink', 'pink', 'pink'
        else:
            if root_z is None:
                root_z = 0
            root_ = np.array([0, 0, float(root_z)]).reshape(1, 3)
            pose = np.concatenate((root_, pose), axis=0)

    x = pose[:, 0]
    y = pose[:, 1]
    z = pose[:, 2]

    ax.scatter(x, y, z, alpha=0.6, s=0.1)

    for link, color_ in zip(SKELETON, colors):
        ax.plot(x[([link[0], link[1]])],
                y[([link[0], link[1]])],
                z[([link[0], link[1]])],
                c=color_, alpha=0.6, lw=3)

    fix_3D_aspect(ax, x, y, z)

    if labels:
        # Show coordinate values
        for i, j, k, l in zip(x, y, z, LABELS):
            ax.text(i, j, k, s=f'{l[:4], round(i, 2), round(j, 2), round(k, 2)}',
                    size=7, zorder=1, color='k')

    # Plot floor
    if floor:
        # xx, yy = np.meshgrid([-max(x), max(x)], [-max(y), max(y)])
        xx, yy = np.meshgrid([x[3], x[6]], [y[3], y[5]])
        zz = np.ones((len(xx), len(yy))) * min(z)*1.01  # padding
        ax.plot_surface(xx, yy, zz, cmap='gray',
                        linewidth=0, alpha=0.2)

    if show_ticks:
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')

    if not show_ticks:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

    ax.view_init(elev=-45, azim=-90)

    if mode == "axis":
        return ax

    elif mode == "show":
        plt.show()
        fig.clf()

    elif mode == "image":
        DPI = fig.get_dpi()
        fig.set_size_inches(305.0/float(DPI), 305.0/float(DPI))
        fig.savefig(f"{os.getenv('HOME')}/lab/HPE3D/src/results/x.png")
        fig.clf()
        image = Image.open(f"{os.getenv('HOME')}/lab/HPE3D/src/results/x.png")
        image = image.convert('RGB')
        image = transforms.ToTensor()(image).unsqueeze_(0)
        return image

    elif mode == "plt":
        return plt

    else:
        raise ValueError("Please choose from 'image', 'show', 'axis', 'plt' only")


def fix_3D_aspect(ax, x, y, z):
    """From https://stackoverflow.com/a/13701747/6710388"""
    # Create cubic bounding box to simulate equal aspect ratio
    max_range = np.array(
        [x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max()
    Xb = 0.5*max_range*np.mgrid[-1:2:2, -1:2:2, -
                                1:2:2][0].flatten() + 0.5*(x.max()+x.min())
    Yb = 0.5*max_range*np.mgrid[-1:2:2, -1:2:2, -
                                1:2:2][1].flatten() + 0.5*(y.max()+y.min())
    Zb = 0.5*max_range*np.mgrid[-1:2:2, -1:2:2, -
                                1:2:2][2].flatten() + 0.5*(z.max()+z.min())

    # Comment or uncomment the below lines to test the fake bounding box
    for xb, yb, zb in zip(Xb, Yb, Zb):
        ax.plot([xb], [yb], [zb], 'w')


def plot_area(pose1, pose2):
    """Plot area between 2 poses, used for showing error in prediction

    Args:
        pose1 (array): predicted 
        pose2 (array): ground truth
    """
    if pose1.shape[0] == 16:
        root_z = 0
        root_ = np.array([0, 0, float(root_z)]).reshape(1, 3)
        pose1 = np.concatenate((root_, pose1), axis=0)

    if pose2.shape[0] == 16:
        root_z = 0
        root_ = np.array([0, 0, float(root_z)]).reshape(1, 3)
        pose2 = np.concatenate((root_, pose2), axis=0)

    x1 = pose1[:, 0]
    y1 = pose1[:, 1]
    z1 = pose1[:, 2]

    x2 = pose2[:, 0]
    y2 = pose2[:, 1]
    z2 = pose2[:, 2]

    vertices = []
    for link in SKELETON:
        area = [(x1[link[0]], y1[link[0]], z1[link[0]]),
                (x1[link[1]], y1[link[1]], z1[link[1]]),
                (x2[link[1]], y2[link[1]], z2[link[1]]),
                (x2[link[0]], y2[link[0]], z2[link[0]])
                ]
        vertices.append(area)

    fig = plt.figure(1)
    ax = fig.gca()

    ax.add_collection3d(Poly3DCollection(vertices, facecolors=[
                        'r', 'r'], alpha=0.2, zorder='max'))


def plot_data(pose2d=None, pose3d=None, image=None):
    """creates a combined figure with image 2d and 3d plots

    Args:
        pose2d (numpy array): 2d pose
        pose3d (numpy array): 3d pose
        image (str, optional): image
    """
    fig = plt.figure()
    i = 1
    col = 0

    for x in [pose2d, pose3d, image]:
        if x is not None:
            col += 1

    if image is not None:
        ax = fig.add_subplot(100+col*10+i)
        i += 1
        if type(image) == str:
            image = Image.open(image)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.imshow(image.convert("RGB"))

    if pose2d is not None:
        ax = fig.add_subplot(100+col*10+i)
        i += 1
        plot_2d(pose2d, mode='axis', show_ticks=True)

    if pose3d is not None:
        ax = fig.add_subplot(100+col*10+i, projection='3d')
        i += 1
        plot_3d(pose3d, mode="axis", labels=True, show_ticks=True)

    plt.show()


def plot_errors(poses, targets, errors=None, grid=2, labels=False, area=True):
    """Show difference between predictions and targets

    Arguments:
        poses {list} -- list of prediction
        targets {list} -- list of ground truths
        errors {list} -- list of avg pjpe for each prediction

    Keyword Arguments:
        grid {int} -- number of plots to show (default: {5})
    """
    fig = plt.figure(figsize=(15., 12.))
    plt.rcParams['savefig.dpi'] = 300

    rows = cols = grid

    i = 1
    for pose, target in zip(poses[:grid], targets[:grid]):
        ax = fig.add_subplot(rows, cols, i, projection='3d')
        plot_3d(pose, mode="axis", color='b', floor=False, axis3don=True, labels=labels)
        plot_3d(target, mode="axis", color='grey', floor=False, axis3don=True, labels=labels)
        if area:
            plot_area(pose, target)
        i += 1

    plt.show()


def print_pose(pose):
    """print pose with its joint name. for debugging

    Args:
        pose (numpy): 2D or 3D pose
    """
    joint_names = ('Pelvis', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee', 'L_Ankle', 'Torso',
                   'Neck', 'Nose', 'Head', 'L_Shoulder', 'L_Elbow', 'L_Wrist', 'R_Shoulder', 'R_Elbow', 'R_Wrist')

    if torch.is_tensor(pose):
        pose = pose.numpy()
    if len(pose) == 17:
        for x in range(len(pose)):
            print(f'{joint_names[x]:10} {pose[x]}')
    else:
        for x in range(len(pose)):
            print(f'{joint_names[x+1]:10} {pose[x]}')


def plot_proj(pose2d, pose3d, pose2d_proj, log=False):
    fig = plt.figure()
    i = 1
    col = 3

    # pose2d
    ax = fig.add_subplot(100+col*10+i)
    i += 1
    plot_2d(pose2d, color='g', mode='axis', show_ticks=True, labels=True)

    # pose3d
    ax = fig.add_subplot(100+col*10+i, projection='3d')
    i += 1
    plot_3d(pose3d, mode="axis", show_ticks=True, labels=True, root_z=10)

    # psoe2d_proj[0]
    ax = fig.add_subplot(100+col*10+i)
    i += 1
    plot_2d(pose2d_proj, color="orange", mode='axis',
            show_ticks=True, labels=True)

    if log:
        plt.savefig("$HOME/temp.png")
        img = Image("$HOME/temp.png")
        return img

    else:
        plt.show()


def plot_projection_raw(sample):
    fig = plt.figure()
    i = 1
    col = 4

    pose2d = sample['pose2d'].copy()
    pose3d = sample['pose3d'].copy()

    pose2d -= pose2d[0]
    pose3d -= pose3d[0]

    dist = np.linalg.norm(pose2d[0]-pose2d[10])
    dist1 = np.linalg.norm(pose3d[0]-pose3d[10])

    pose2d /= 2*dist

    pose3d = pose3d/dist1

    pose3d += (0, 0, 2)

    # dist2 = pose2d[0][1]-pose2d[10][1]
    # dist3 = pose3d[0][1]-pose3d[10][1]
    print("[plot_proj] ", pose3d[0], pose3d[10])
    # pose2d
    ax = fig.add_subplot(100+col*10+i)
    i += 1
    plot_2d(pose2d, color='g', mode='axis', show_ticks=True, labels=True)

    # pose3d
    ax = fig.add_subplot(100+col*10+i, projection='3d')
    i += 1
    plot_3d(sample["pose3d"]-sample["pose3d"][0],
            mode="axis", show_ticks=True, labels=True)

    # pose3d
    ax = fig.add_subplot(100+col*10+i, projection='3d')
    i += 1
    plot_3d(pose3d, mode="axis", show_ticks=True, labels=True)

    # pose2d_proj
    pose3d = torch.Tensor([pose3d])
    for x in sample.keys():
        if not isinstance(sample[x], str):
            sample[x] = torch.Tensor(sample[x])

    pose2d_proj = project_3d_to_2d(pose3d, cam_params=sample)

    # print("dist", dist, "dist1", dist1, "dist2", dist2, "dist3", dist3, "scale", pose2d/pose2d_proj)
    print(pose2d, "\n", pose2d_proj)
    # psoe2d_proj[0]
    ax = fig.add_subplot(100+col*10+i)
    i += 1
    plot_2d(pose2d_proj[0], color="orange",
            mode='axis', show_ticks=True, labels=True)

    print(torch.equal(torch.Tensor(pose2d), pose2d_proj))
    print(torch.allclose(torch.Tensor(pose2d), pose2d_proj))
    print(torch.mean(torch.tensor(pose2d)-pose2d_proj))
    print(torch.tensor(pose2d))
    print(pose3d)

    plt.show()


def plot_all_proj(config, recon_2d, novel_2d, target_2d, recon_3d, target_3d, name=""):

    recon_2d = recon_2d.detach().cpu().numpy()
    novel_2d = novel_2d.detach().cpu().numpy()
    target_2d = target_2d.detach().cpu().numpy()
    recon_3d = recon_3d.detach().cpu().numpy()
    target_3d = target_3d.detach().cpu().numpy()

    img = plot_2d(target_2d, color='pink', mode='image', show_ticks=True, labels=False)
    config.logger.log({name+"target_2d": config.logger.Image(img)}, commit=False)

    img = plot_2d(recon_2d, color='blue', mode='image',
                  show_ticks=True, labels=False, mean_root=True)
    config.logger.log({name+"recon_2d": config.logger.Image(img)}, commit=False)
  
    img = plot_2d(novel_2d, color='blue', mode='image',
                  show_ticks=True, labels=False, mean_root=True)
    config.logger.log({name+"novel_2d": config.logger.Image(img)}, commit=False)

    img = plot_3d(target_3d, color='pink', mode="image", show_ticks=True, labels=False)
    config.logger.log({name+"target_3d": config.logger.Image(img)}, commit=False)

    img = plot_3d(recon_3d, color='blue', mode="image", show_ticks=True, labels=False, mean_root=True)
    config.logger.log({name+"recon_3d": config.logger.Image(img)}, commit=True)


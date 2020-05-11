import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mayavi import mlab
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def plot_diff(pose, target, error):
    # info to connect joints
    skeleton = ((0, 7), (7, 8), (8, 9), (9, 10), (8, 11), (11, 12), (12, 13),
                (8, 14), (14, 15), (15, 16), (0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6))
    labels = ('Pelvis', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee', 'L_Ankle', 'Torso', 'Neck',
              'Nose', 'Head', 'L_Shoulder', 'L_Elbow', 'L_Wrist', 'R_Shoulder', 'R_Elbow', 'R_Wrist')

    fig = plt.figure(1)
    ax = fig.gca(projection='3d')
    ax._axis3don = False

    x = pose[:, 0]
    y = -1*pose[:, 2]
    z = -1*pose[:, 1]

    x1 = target[:, 0]
    y1 = -1*target[:, 2]
    z1 = -1*target[:, 1]

    ax.scatter(x, y, z, alpha=0.6, s=2)
    ax.scatter(x1, y1, z1, c='grey', s=1, alpha=0.5)

    verts = []

    for link in skeleton:
        ax.plot(x[([link[0], link[1]])],
                y[([link[0], link[1]])], z[([link[0], link[1]])],
                c='b', alpha=0.6, lw=3)

        ax.plot(x1[([link[0], link[1]])],
                y1[([link[0], link[1]])], z1[([link[0], link[1]])],
                c='grey', alpha=0.5, lw=1)

        area = [(x[link[0]], y[link[0]], z[link[0]]),
                (x[link[1]], y[link[1]], z[link[1]]),
                (x1[link[1]], y1[link[1]], z1[link[1]]),
                (x1[link[0]], y1[link[0]], z1[link[0]])
                ]

        verts.append(area)

    ax.add_collection3d(Poly3DCollection(verts, facecolors=[
                        'r', 'r'], alpha=0.5, zorder='max'))

    # for i, j, k, l in zip(x, y, z, labels):
    #     ax.text(i, j, k, s=l, size=8, zorder=1, color='k')

    # Plot the surface.
    xx, yy = np.meshgrid([-500, 500], [-500, 500])
    zz = np.ones((len(xx), len(yy))) * min(min(z), min(z1))*1.01  # padding
    ax.plot_surface(xx, yy, zz, cmap='gray',
                    linewidth=0, alpha=0.2)

    ax.text(200, 200, zz[0][0], s=str(round(error, 2)) +
            " mm", size=8, zorder=1, color='k')

    # ax.set_xlabel('X Label')
    # ax.set_ylabel('Y Label')
    # ax.set_zlabel('Z Label')
    # ax.axis = 'off'
    
    plt.show()

    # for angle in range(0, 360):
    #     ax.view_init(30, angle)
    #     plt.draw()
    #     plt.pause(.001)


def plot_diff_3D(pose, target, error):
    # info to connect joints
    skeleton = ((0, 7), (7, 8), (8, 9), (9, 10), (8, 11), (11, 12), (12, 13),
                (8, 14), (14, 15), (15, 16), (0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6))

    black = (0, 0, 0)
    white = (1, 1, 1)
    mlab.figure(bgcolor=white)

    x = pose[:, 0]
    y = -1*pose[:, 2]
    z = -1*pose[:, 1]

    x1 = target[:, 0]
    y1 = -1*target[:, 2]
    z1 = -1*target[:, 1]

    for link in skeleton:
        x_ = [x[link[0]], x[link[1]]]
        y_ = [y[link[0]], y[link[1]]]
        z_ = [z[link[0]], z[link[1]]]
        mlab.plot3d(x_, y_, z_, color=(0, 0, 1), tube_radius=10.)

        x1_ = [x1[link[0]], x1[link[1]]]
        y1_ = [y1[link[0]], y1[link[1]]]
        z1_ = [z1[link[0]], z1[link[1]]]
        mlab.plot3d(x1_, y1_, z1_, color=(0, 0, 1), tube_radius=10., opacity=0.5)


    # Finally, display the set of lines
    # mlab.pipeline.surface(lines, colormap='Accent', line_width=1, opacity=.4)

    # And choose a nice view
    # mlab.view(33.6, 106, 5.5, [0, 0, .05])
    # mlab.roll(125)
    # mlab.savefig("stick_2.obj")
    mlab.show()

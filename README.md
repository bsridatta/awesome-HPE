# HPE3D

Code for human pose estimation with VAE-GAN hybrid model.

[Presentation](https://docs.google.com/presentation/d/167crr5xf_YZ8U8hUgSEpa6ah-odgo1ag0sWCCX0omBo)
[Thesis](https://www.diva-portal.org/smash/get/diva2:1536685/FULLTEXT01.pdf)

# Human Pose Estimation - Literature Study

* [Concetps](#Concepts)  
* [3D HPE](#3D-HPE)
  * [2D-3D Lifting](#2D-3D-Lifting) 
* [2D HPE](#2D-HPE)
* [Datasets](#Datasets)  
* [More Stuff](#More-Stuff)    

Concepts
========
* Reprojection Error Optimization - 3D human body model is deformed such that it satisfies a reprojection error  
* Direct NN inference -  estimate 3D poses directly from images or detected keypoints
* Kinematic Chain Space (KCS) - Projecting 3D human pose into KCS, a contraint is derived that is based on the assumption that the bone lengths are constant. This can be benificial as giving an additional feature matrix to the network, it doesnt have to learn joint length computation and angular constraints on its own [KCS for monocular MoCap](https://arxiv.org/pdf/1702.00186.pdf)
* Non rigid structure from motion (NRSfM) - aims to obtain the varying 3D structure and camera motion from uncalibrated 2D point tracks [NR-SFM video explanation](https://www.youtube.com/watch?v=zBalNj2F8Ik)
* Kinematic Feature updates (in 2D) -  encode the kinematic structure via feature updates at coarse resolution [RePose](https://arxiv.org/pdf/2002.03933v1.pdf)
* Real-time: Casading, Long short skip connections [XNect](https://arxiv.org/pdf/1907.00837v1.pdf)
* Ordinal Ranking [Ordinal+CVAE](#Monocular-3D-Human-Pose-Estimation-by-Generation-and-Ordinal-Ranking) [DRPose3D - Depth Ranking](https://arxiv.org/pdf/1805.08973.pdf)  
* C-VAE [Ordinal+CVAE](#Monocular-3D-Human-Pose-Estimation-by-Generation-and-Ordinal-Ranking)


3D HPE
======


#### Camera Distance-aware Top-down Approach for 3D Multi-person Pose Estimation from a Single RGB Image   
[[Paper](https://arxiv.org/pdf/1907.11346v2.pdf)]
[[Code](https://github.com/mks0601/3DMPPE_POSENET_RELEASE)] 
[[Code](https://github.com/mks0601/3DMPPE_ROOTNET_RELEASE)] 
[**ICCV 2019**]
[image-2Dheatmap-3D, absolute pose, multi person, pose depth, cascade]

#### Unsupervised 3D Pose Estimation with Geometric Self-Supervision 
[[Paper](https://arxiv.org/pdf/1904.04812.pdf)]
[**CVPR 2019**]
[2D-3D, self supervised, discriminator, domain adaptation, temporal consistency]


#### PoseLifter: Absolute 3D human pose lifting network from a single noisy 2D human pose
[[Paper](https://arxiv.org/pdf/1910.12029.pdf)]
[2019,2020]
[image-2D-3D, project w/ focal length, learn human size, absolute pose, noise, errors, cascade]

#### RepNet: Weakly Supervised Training of an Adversarial Reprojection Network for 3D Human Pose Estimation
[[Paper](https://arxiv.org/pdf/1902.09868.pdf)]
[[Code](https://github.com/bastianwandt/RepNet)]
[**CVPR 2019**]
[2D-3D, KCS, weakly supervised, adversial training, GAN]

#### Distill Knowledge from NRSfM for Weakly Supervised 3D Pose Learning
[[Paper](http://openaccess.thecvf.com/content_ICCV_2019/papers/Wang_Distill_Knowledge_From_NRSfM_for_Weakly_Supervised_3D_Pose_Learning_ICCV_2019_paper.pdf)]
[**ICCV 2019**]
[Image features+2D-3D, NRSfM, teacher student, weakly supervised]

#### C3DPO: Canonical 3D Pose Networks for Non-Rigid Structure From Motion 
[[Paper](https://arxiv.org/pdf/1909.02533.pdf)]
[[Code](https://github.com/facebookresearch/c3dpo_nrsfm)]
[**ICCV 2019**]
[2D-3D, NRSFM, canonicalization network, self-supervised]

#### Unsupervised Adversarial Learning of 3D Human Pose from 2D Joint Locations
[[Paper](https://arxiv.org/pdf/1803.08244.pdf)]
[[Code](https://github.com/DwangoMediaVillage/3dpose_gan)]
[2018]
[2D-3D, GAN, unsupervised]

#### Monocular 3D Human Pose Estimation by Generation and Ordinal Ranking 
[[Paper](http://openaccess.thecvf.com/content_ICCV_2019/papers/Sharma_Monocular_3D_Human_Pose_Estimation_by_Generation_and_Ordinal_Ranking_ICCV_2019_paper.pdf)]
[**ICCV 2019**]
[2Dheatmap-3D, ambigious use of 3D GT, C-VAE, ordinal ranking and score, condition on 2d pose]

#### Occlusion-Aware Networks for 3D Human Pose Estimation in Video
[[Paper](http://openaccess.thecvf.com/content_ICCV_2019/papers/Cheng_Occlusion-Aware_Networks_for_3D_Human_Pose_Estimation_in_Video_ICCV_2019_paper.pdf)]
[**ICCV 2019**]
[2Dheatmap-3D, reprojection+GT, adversarial, occlusion, video]


Using GT
---------

2D HPE
======

#### RePose: Learning Deep Kinematic Priors for Fast Human Pose Estimation 
[[Paper](https://arxiv.org/pdf/2002.03933v1.pdf)]
[**2020**]
[kinematic priors]

<!-- Template for a paper
#### Title 
[[Paper](https://arxiv.org/pdf/)]
[**Venue**]
</br>
<details>
<summary>
Keyword1, keyword2, keyword3    
</summary>
<*Remove this*/br>  
> * Keypoint 1 
> * Keypoint 2
</details>
End of Template -->  

Datasets
========
* [Human3.6](http://vision.imar.ro/human3.6m/description.php)[2014] - 2D and 3D relative joint pose, multi view
* [MPI-INF-3DHP](http://gvv.mpi-inf.mpg.de/3dhp-dataset/)[2017] - 2D and 3D relative joint pose, mutli view
* [JTA Joint Track Auto](https://aimagelab.ing.unimore.it/imagelab/page.asp?IdPage=25)[2018] - 2D, 3D, occulusion annotation, synthetic

More Stuff
===========
* [Learning to Reconstruct people](https://sric.me/Learning-to-Reconstruct-People/)
* [Gyeongsik Moon - Seoul National University](https://scholar.google.com.hk/citations?user=2f2D258AAAAJ&hl=zh-CN)
* [awesome-human-pose-estimation](https://github.com/wangzheallen/awesome-human-pose-estimation)
* [3d-human-pose-estimation](https://github.com/trumDog/3d-human-pose-estimation)

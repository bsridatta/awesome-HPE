python3.7 ../src/train.py \
    --cuda True\
    --wandb True\
    --seed 400\
    --annotation_file /home/datta/lab/HPE3D/src/data/debug_h36m17.h5\
    --image_path /home/datta/lab/HPE_datasets/h36m/\
    --ignore_images True\
    --epochs 200\
    --batch_size 5\
    --fast_dev_run True\
    --resume_pt 0\
    --variant 2\
    --latent_dim 30\
    --pretrained False\
    --train_last_block False\
    --n_joints 16\
    --learning_rate 0.001\
    --save_dir ../checkpoints\
    --exp_name run_1\
    --log_interval 1\
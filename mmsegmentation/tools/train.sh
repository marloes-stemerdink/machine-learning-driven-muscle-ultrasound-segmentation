############## TRAINING/FINETUNING MODEL ###########################
CUDA_LAUNCH_BLOCKING=1
python mmsegmentation/tools/train.py /path/to/config.py --work-dir /path/to/save/results

############## EXAMPLE ###########################
CUDA_LAUNCH_BLOCKING=1
python mmsegmentation/tools/train.py /mnt/model_to_train/subset_4/finetuning_config_subset_4.py --work-dir /mnt/model_to_train/subset_4/results/

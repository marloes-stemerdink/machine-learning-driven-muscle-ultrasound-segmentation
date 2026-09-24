############## TRAINING/FINETUNING MODEL ###########################
CUDA_LAUNCH_BLOCKING=1
python mmsegmentation/tools/train.py /path/to/config.py --work-dir /path/to/save/results

############## EXAMPLE ###########################
CUDA_LAUNCH_BLOCKING=1
python mmsegmentation/tools/train.py input/finetuning_base_config.py --work-dir /mnt/model_to_train/subset_4/results/

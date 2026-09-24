############## TESTING MODEL ###########################
python tools/local_inference.py /path/to/config.py --checkpoint /path/to/checkpoint.pth --img_folder /path/to/image/folder --out_results /path/output/folder--ground_truth path/mask/folder --plot_rgb --plot_label_compare

############## EXAMPLE ###########################
python tools/local_inference.py /mnt/data/subset_4/finetuning_confic_subset_4.py --checkpoint /mnt/data/subset_4/iter_3000.pth --img_folder /mnt/data/subset_1/images --out_results /mnt/data/subset_4/testing--ground_truth /mnt/data/subset_1/masks --plot_rgb --plot_label_compare



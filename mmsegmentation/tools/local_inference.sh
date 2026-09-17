############## TESTING FINETUNING ITER ###########################
python tools/local_inference.py mnt/data/subset_4/finetuning_confic_subset_4.py --checkpoint mnt/data/subset_4/iter_3000.pth --img_folder /mnt/data/subset_1/images --out_results /mnt/data/subset_4/testing--ground_truth /mnt/data/subset_1/masks --plot_rgb --plot_label_compare

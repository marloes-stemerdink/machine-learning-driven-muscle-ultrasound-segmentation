# Machine learning-driven muscle ultrasound segmentation
This repository implements an automatic and reproducible pipeline for muscle ultrasound analysis introducing a machine learning approach that integrates deep learning-based segmentation. The goal is to enhance the objectivity and efficiency of muscle ultrasound evaluation, reducing reliance on time-consuming manual assessments and overcoming interobserver variability. 

This repository is based on https://github.com/frmrz/Machine-learning-driven-Heckmatt-grading-in-facioscapulohumeral-muscular-dystrophy. This author developed a pipeline for deep learning-based segmentation. An initial analysis revealed that the model is not yet generalisable to ultrasound devices and populations beyond those on which it was originally trained. This repository contains everything that is necessary to finetune the existing model to a different device or population. Contact the corresponding author (https://www.sciencedirect.com/science/article/pii/S1388245725000367) for accessing the trained models.

REF NAAR METHODS

The repository is structured as follows:
- **`file_preparation/`**: Scripts to prepare the dataset for training or application of the model
- **`mmsegmentation/`**: Contains deep learning code for muscle segmentation & classification with K-Net. CHECKEN, DENK ALLEEN TOOLS NODIG
- **`feature_extraction/`**: Scripts to extract texture/radiomics features and evaluate segmentation metrics.
- **`analysis/`**: Scripts for further analysis of the results
- **`input`**: Input files required for scripts

### 1. **`file_preparation/`**
Contains the code for preparing images and masks 

- **`createQUMIAMasks.m`**
  Matlab script to generate filenames according to the format, and convert masks to correct format (0=background, 1=muscle, 255=ignore). Advisable to convert this to a .py file for consistency.
- **`crop_images_masks_convert_dcm.py`**  
  Crop information from .dcm files while converting them to .png files for the analysis. Crop masks (.png files) accordingly to retain the same image size.

### 2. **`mmsegmentation/`**
Contains the code for muscle segmentation & classification with **K-Net** (based on [MMSegmentation](https://github.com/open-mmlab/mmsegmentation)):

- **`tools/train.py`**  
  Train your segmentation model.
- **`tools/local_inference.py`**  
  Quick local inference for debugging and a more flexible image source than test.py.

### 3. **`feature_extraction/`**
Scripts to **extract texture/radiomics features** and evaluate segmentation metrics:

- **`extractNormalizedTextureFeaturesFast.py`**  
  Extracts radiomics features with PyRadiomics, writing to JSON/Excel.
- **`computeMetricsAndValuesFast.py`**  
  Generates IoU, precision and recall metrics. Visualising in boxplots
  
### 4. **`analysis/`**
Contains the code for analysis of the results.
- **`visualize_mask_and_gt.py`**
  Script to visualise predicted masks and ground truth masks. Ouputs a PNG image showing, from top to bottom: the ultrasound image, the ultrasound image with ground truth, the ultrasound image with the predicted mask, and the ultrasound image with ground truth and predicted mask combined.
- **`visualize_mask_and_gt_specific.py`**
  To make a figure of a few specific images
- **`analysis_iou.py`**
  Script to summarise intersection over union, precision and recall. Outputs a .csv file with these values per image and a .csv file with these values grouped per muscle (mean+sd, be careful with small datasets!).
-  **`echogenicity_compare.py`**
  Script to compare echogenicity values of predicted masks and ground truth masks. Outputs paired t-test and Wilcoxon signed rank test comparison per muscle and a Bland Altman plot per group

### 5. **`input/`**
Contains files that are required for scripts
- **`Muscles.xlsx`**
  Excel file containing the muscle codes. Please note that orbicularis oris is coded with 029, while it was coded as 013 in the base model

---

## How to Reproduce the Results

1. **Install Dependencies & Environment**  
   - Install the [Python environment](environment.yml) with key packages in the correct version.

2. **Prepare dataset**
   - Compile a dataset with muscle ultrasound images representative of the group you eventually want to apply the pipeline to.
   - The dataset should consist of muscle ultrasound images and corresponding masks, both in .png format. Masks should contain class indices as follows: background = 0, muscle = 1, ignore label = 255 (only for pixels you want the training to ignore). Filenames should be structured as follows: PatientID_musclecode_side_index(_visit). See [`file_preparation`](/file_preparation) for scripts and further information.
   - Use `createQUMIAMasks.m` for filename structure and correct class indices
   - Use `crop_images_masks_convert_dcm.py` for changing the file format
   - Split images into train/validation/testing folds

3. **Test the segmentation model**
   - Generate predicted masks using `mmsegmentation/tools/local_inference.py`
   - Example:
     ```bash
     python local_inference.py /path/to/your_config.py --checkpoint /path/to/your_checkpoint.pth --img_folder /path/to/ultrasound/images/ --out_results path/to/save/results/ --ground_truth /path/to/ground/truth/masks/ --plot_rgb --plot_label_compare
     ```
   - Extract radiomics features using `extractNormalizedTextureFeaturesFast.py`
   - Extract and visualise IoU, precision and recall in boxplots using `computeMetricsAndValuesFast.py`
   - Get IoU, precision and recall per muscle using `analysis_iou.py`
   - Compare echogenicity values of predicted and ground truth masks using `echogenicity_compare.py`

4. **Train the segmentation model**
   - Under `mmsegmentation/tools/`, adapt or create a config
   - Example:
     ```bash
     python train.py /path/to/your_config.py --work-dir /path/to/save/checkpoints
     ```
   - This trains the segmentation network. Edit the config file to train the model in the different modalities (multi-label / binary / muscle-specific).

5. **Step 5**
   - Use `test.py`:
     ```bash
     python test.py /path/to/your_config.py /path/to/checkpoint.pth
     ```
   - Saves predictions (PNG). Then run `computeMetricsAndValuesFast.py` or for confusion matric

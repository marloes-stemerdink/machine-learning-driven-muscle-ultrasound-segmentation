# Machine learning-driven muscle ultrasound segmentation
This repository implements an automatic and reproducible pipeline for muscle ultrasound analysis introducing a machine learning approach that integrates deep learning-based segmentation. The goal is to enhance the objectivity and efficiency of muscle ultrasound evaluation, reducing reliance on time-consuming manual assessments and overcoming interobserver variability. 

This repository is based on https://github.com/frmrz/Machine-learning-driven-Heckmatt-grading-in-facioscapulohumeral-muscular-dystrophy. This author developed a pipeline for deep learning-based segmentation. An initial analysis revealed that the model is not yet generalisable to ultrasound devices and populations beyond those on which it was originally trained. This repository contains everything that is necessary to finetune the existing model to a different device or population.

TOEVOEGEN
environment!
matlab voor het juiste filename format (uitleggen waarom matlab)
waar vind je het open source model

The repository is structured as follows:
- **`file_preparation/`**: Scripts to prepare the dataset for training or application of the model
- **`mmsegmentation/`**: Contains deep learning code for muscle segmentation & classification with K-Net. CHECKEN, DENK ALLEEN TOOLS NODIG
- **`feature_extraction/`**: Scripts to extract texture/radiomics features and evaluate segmentation metrics.

### 1. **`file_preparation/`**
Contains the code for preparing images and masks 

- **`crop_images_masks_convert_dcm.py`**  
  Crop information from .dcm files while converting them to .png files for the analysis. Crop masks (.png files) accordingly to retain the same image size.
- **`visualize_mask_and_gt.py`**
  Script to visualise predicted masks and ground truth masks. Ouputs a PNG image showing, from top to bottom: the ultrasound image, the ultrasound image with ground truth, the ultrasound image with the predicted mask, and the ultrasound image with ground truth and predicted mask combined.
- **`visualize_mask_and_gt_specific.py`**
  To make a figure of a few specific images
- **`analysis_iou.py`**
  Script to summarise intersection over union, precision and recall. Outputs a .csv file with these values per image and a .csv file with these values grouped per muscle (mean+sd, be careful with small datasets!).
-  **`echogenicity_compare.py`**
  Script to compare echogenicity values of predicted masks and ground truth masks. Outputs paired t-test and Wilcoxon signed rank test comparison per muscle and a Bland Altman plot. CHECKEN, OOK PER GROEP DOEN ?!

### 2. **`mmsegmentation/`**
Contains the code for muscle segmentation & classification with **K-Net** (based on [MMSegmentation](https://github.com/open-mmlab/mmsegmentation)):

- **`tools/train.py`**  
  Train your segmentation model.
- **`tools/local_inference.py`**  
  Quick local inference for debugging and a more flexible image source than test.py.
- **`utils/compareRevisionResults.py`**  
  Compare segmentation metrics (IoU, precision, recall) for different model versions (multi-label / binary / muscle-specific) with statistical tests.  CHECKEN, WEGHALEN?!

### 3. **`feature_extraction/`**
Scripts to **extract texture/radiomics features** and evaluate segmentation metrics:

- **`extractNormalizedTextureFeaturesFast.py`**  
  Extracts radiomics features with PyRadiomics, writing to JSON/Excel.  
---

## How to Reproduce the Results

1. **Install Dependencies & Environment**  AANPASSEN
   - Python ≥ 3.8 recommended.
   - Key packages: PyTorch, MMCV, MMEngine, MMSegmentation, PyRadiomics, XGBoost, SHAP, pandas, seaborn, etc.
   - The `mmsegmentation` folder is a partial copy of [MMSegmentation](https://github.com/open-mmlab/mmsegmentation). Ensure versions match `mmseg/__init__.py`.

2. **Step 2**
   - Data used in the paper: [Mendeley dataset](https://doi.org/10.17632/yzg86vb895.1).

3. **Step 3**
   - Under `mmsegmentation/tools/`, adapt or create a config for K-Net (similar to `knet_swin_mod`).
   - Example:
     ```bash
     python train.py /path/to/your_config.py --work-dir /path/to/save/checkpoints
     ```
   - This trains the segmentation network. Edit the config file to train the model in the different modalities (multi-label / binary / muscle-specific).

4. **Step 4**
   - Use `test.py`:
     ```bash
     python test.py /path/to/your_config.py /path/to/checkpoint.pth
     ```
   - Saves predictions (PNG). Then run `computeMetricsAndValuesFast.py` or for confusion matric

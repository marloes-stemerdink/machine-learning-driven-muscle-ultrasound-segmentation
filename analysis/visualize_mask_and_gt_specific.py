''' Script for visualising masks on images to check segmentation by mmsegmentation trained models'''
'Look up img_path, gt_path, mask_path and output_path and change to own directories.'
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

# Check overlay for every muscle
# List of muscles with their codes
muscles = {
    'biceps brachii': '001',
    'deltoideus': '002',
    'depressor anguli oris': '003',
    'digastricus': '004',
    'extensor digitorum brevis': '005',
    'flexor carpi radialis': '006',      
    'flexor digitorum profundus': '007', 
    'gastrocnemius medial head': '008',
    'geniohyoideus': '009',
    'levator labii superior': '010', 
    'masseter': '011',
    'mentalis': '012',
    'orbicularis oris': '013',
    'peroneus tertius': '014',    
    'rectus abdominis': '015',
    'rectus femoris': '016',
    'temporalis': '017',
    'tibialis anterior': '018',
    'trapezius': '019',
    'vastus lateralis': '020',
    'zygomaticus': '021',
    'sternocleidomastoideus': '022', 
    'interosseus dorsalis': '023',   
    'soleus': '024', 
    'biceps femoris': '025',
    'flexor carpi ulnaris': '026',
    'zygomaticus major': '027',
    'zygomaticus minor': '028',
    'orbicularis oris': '029',
    'obliquus ext abdominus': '030',
    'intercostals': '031', 
    'diafragma inademen': '032',
    'diafragma uitademen': '033',
    'serratus anterior': '034',
    'obliquus int abdominus': '035',
    'paraspinal thoracal': '036',
    'paraspinal lumbal': '037',
    'triceps': '038',
    'diaphragm': '039',
    'extensors underarm': '040',
    'transversus abdominus': '041',
    'splenius capitis': '042'
    }

# overlay a single mask
def overlay(image, mask, color):
    out = image.astype(np.float32)
    out[mask] = (1 - alpha) * out[mask] + alpha * color

    return out.astype(np.uint8)

# overlay GT + prediction
def overlay_both(image, gt, pred):
    out = image.astype(np.float32)

    only_gt = gt & ~pred
    only_pred = pred & ~gt
    both = gt & pred

    out[only_gt] = (1 - alpha) * out[only_gt] + alpha * gt_color
    out[only_pred] = (1 - alpha) * out[only_pred] + alpha * pred_color
    out[both] = (1 - alpha) * out[both] + alpha * overlap_color

    return out.astype(np.uint8)

# List of selected images
# TODO change to images you'd like to see visualised
selected = {
        "healthy": ["00003_007_03.png", "00004_002_02.png"],
        "klinisch": ['00005_006_06_6.png'],
        "last_strong": ["00007_015_02_5.png"]
}
group_names = {
    "healthy": "Healthy",
    "klinisch": "Outpatient clinic",
    "last_strong": "LAST STRONG"
}

alpha = 0.4 # transparency masks

# Colors masks
gt_color = np.array([0, 255, 0]) # green
pred_color = np.array([255, 0, 0]) # red
overlap_color = np.array([255, 255, 0]) # yellow

fig, axes = plt.subplots(4, 4, figsize=(12,12))
row_labels=["Original image", 'Ground truth mask', 'Predicted mask','Combined']
letters = ["A", "B", "C", "D"]
col = 0

output_path="/mnt/data/oud/test_visualise/"

for group, files in selected.items():
    for fname in files:
    # for file in files_path.iterdir():
        img_path = f'/mnt/data/dataset_training/subset_4/converted/training/images/{fname}'
        gt_path = f'/mnt/data/dataset_training/subset_4/converted/training/masks/{fname}'
        mask_path = f'/mnt/data/dataset_training/subset_4/converted/training/masks/{fname}'

         # Load image, gt and predicted mask
        img = np.array(Image.open(img_path).convert("RGB")) #.convert("RGB"))
        mask = np.array(Image.open(mask_path)) == 1  # 0 = background, 1 = foreground
        gt = np.array(Image.open(gt_path)) == 1

        # Create overlays
        img_gt = overlay(img, gt, gt_color)
        img_pred = overlay(img, mask, pred_color)
        img_both = overlay_both(img, gt, mask)

        # Get muscle name
        muscle_code = fname.split("_")[1]
        muscle_name = [name for name, code in muscles.items() if code == muscle_code][0]

        # Plot
        axes[0, col].imshow(img)
        axes[1, col].imshow(img_gt)
        axes[2, col].imshow(img_pred)
        axes[3, col].imshow(img_both)

        # Turn axes off
        images = [img,img_gt,img_pred,img_both]
        for r in range(4):
            axes[r,col].imshow(images[r])
            axes[r,col].set_title(row_labels[r],fontsize=12)
            axes[r, col].axis('off')
        
        # Titles on top row
        axes[0,col].set_title(f"{letters[col]}: {group_names[group]} - {muscle_name}")
        
        col+=1

        plt.tight_layout()
        # plt.show()

fig.savefig(f'{output_path}results_figure_subset4_3.png')
plt.close()
 

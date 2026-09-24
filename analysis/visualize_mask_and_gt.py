" Script for visualising masks on images to check segmentation by mmsegmentation trained models"
'Look up all paths in the script and change to own directories'
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

alpha = 0.4 # transparency masks

# Colors masks
gt_color = np.array([0, 255, 0]) # green
pred_color = np.array([255, 0, 0]) # red
overlap_color = np.array([255, 255, 0]) # yellow

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

files_path = Path('/mnt/data/model_to_train/subset_4/zippen/testing/pred/')
files = list(files_path.iterdir())
for file in tqdm(files, leave=False):
# for file in files_path.iterdir():
    img_path = f'/mnt/data/dataset_training/subset_1/together/images/{file.name}'
    gt_path = f'/mnt/data/dataset_training/subset_1/together/masks/{file.name}'
    mask_path = f'/mnt/data/model_to_train/subset_4/zippen/testing/pred/{file.name}'

        # Load image, gt and predicted mask
    img = np.array(Image.open(img_path).convert("RGB")) #.convert("RGB"))
    mask = np.array(Image.open(mask_path)) == 1  # 0 = background, 1 = foreground
    gt = np.array(Image.open(gt_path)) == 1

    # Create overlays
    img_gt = overlay(img, gt, gt_color)
    img_pred = overlay(img, mask, pred_color)
    img_both = overlay_both(img, gt, mask)

    # Get muscle name
    muscle_code = file.name.split("_")[1]
    muscle_name = [name for name, code in muscles.items() if code == muscle_code][0]

    # Plot
    fig, axes = plt.subplots(4, 1, figsize=(6,16))

    axes[0].imshow(img)
    axes[0].set_title(f"Original image ({muscle_name})")
    axes[0].axis("off")

    axes[1].imshow(img_gt)
    axes[1].set_title("Ground truth mask")
    axes[1].axis("off")

    axes[2].imshow(img_pred)
    axes[2].set_title("Predicted mask")
    axes[2].axis("off")

    axes[3].imshow(img_both)
    axes[3].set_title("Ground truth and prediction")
    axes[3].axis("off")

    plt.tight_layout()
    # plt.show()
    plt.savefig(f"/mnt/data/model_to_train/subset_4/visualised/{file.name}")
    plt.close()

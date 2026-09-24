''' Script to crop masks and images, and convert DICOM files to png files'''
'Look up input_dir and output_dir and change to own directories'
'Change crop values if necessary'

import pydicom
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from PIL import Image
from pydicom.errors import InvalidDicomError


def load_dicom(file_path):
    """Load DICOM file and return dataset."""
    return pydicom.dcmread(file_path)

def visualize_image(dicom_dataset):
    """Visualize the DICOM image."""
    plt.imshow(dicom_dataset.pixel_array, cmap=plt.cm.gray)
    plt.title("DICOM Image")
    plt.show()

def crop_image(image, top_crop_px=0, bottom_crop_px=0, left_crop_px=0, right_crop_px=0):
    """
    Crop irrelevant information from all sides of the image.

    Works for:
      - 2D arrays: (H, W)
      - 3D arrays: (H, W, C)  e.g. color images
    """
    if image.ndim == 2:
        h, w = image.shape
    elif image.ndim == 3:
        h, w, _ = image.shape
    else:
        raise ValueError(f"Unsupported image shape {image.shape}; expected 2D or 3D array.")

    top = max(0, top_crop_px)
    bottom = max(0, bottom_crop_px)
    left = max(0, left_crop_px)
    right = max(0, right_crop_px)

    if top + bottom >= h:
        raise ValueError("Cropping too much vertically; adjust top/bottom_crop_px.")
    if left + right >= w:
        raise ValueError("Cropping too much horizontally; adjust left/right_crop_px.")

    if image.ndim == 2:
        return image[top:h - bottom, left:w - right]
    else:  # 3D (H, W, C)
        return image[top:h - bottom, left:w - right, :]

def save_image_as_png(
    dicom_dataset,
    output_file_path,
    top_crop_px=0,
    bottom_crop_px=0,
    left_crop_px=0,
    right_crop_px=0,
):
    """Save the DICOM image data as a PNG file, with optional cropping from all sides."""
    img = dicom_dataset.pixel_array

    if any(v > 0 for v in (top_crop_px, bottom_crop_px, left_crop_px, right_crop_px)):
        img = crop_image(
            img,
            top_crop_px=top_crop_px,
            bottom_crop_px=bottom_crop_px,
            left_crop_px=left_crop_px,
            right_crop_px=right_crop_px,
        )

    plt.imsave(output_file_path, img, cmap=plt.cm.gray)

def convert_dicom_to_png(
    input_dir,
    output_dir,
    top_crop_px=0,
    bottom_crop_px=0,
    left_crop_px=0,
    right_crop_px=0,
):
    """
    Recursively read all DICOM images in a directory and its subdirectories,
    crop from all sides, and save them as PNG images in an output directory.
    """
    for root, dirs, files in os.walk(input_dir):
        for file in tqdm(files, desc = "processing files"):
        # for file in files:
            if file.endswith(".dcm"):
                file_path = os.path.join(root, file)
                try:
                    dicom_dataset = pydicom.dcmread(file_path)
                except InvalidDicomError as e:
                    raise InvalidDicomError(f"{e} (file: {file_path})") from e
                output_file_path = os.path.join(output_dir, file.replace(".dcm", ".png"))
                if os.path.exists(output_file_path):    # skip existing files
                    continue
                save_image_as_png(
                    dicom_dataset,
                    output_file_path,
                    top_crop_px=top_crop_px,
                    bottom_crop_px=bottom_crop_px,
                    left_crop_px=left_crop_px,
                    right_crop_px=right_crop_px,
                )

def crop_png_image(input_path, output_path, top_crop_px, bottom_crop_px, left_crop_px, right_crop_px):
    """Crop a single PNG image."""
    img = Image.open(input_path)
    width, height = img.size

    # Crop box: (left, top, right, bottom)
    cropped = img.crop((
        left_crop_px,
        top_crop_px,
        width - right_crop_px,
        height - bottom_crop_px
    ))

    cropped.save(output_path)


def crop_all_pngs(input_dir, output_dir):
    """Crop all PNG images in a folder."""
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".png"):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file)

            try:
                crop_png_image(input_path, 
                               output_path,
                               top_crop_px,
                               bottom_crop_px,
                               left_crop_px,
                               right_crop_px,)
                print(f"✅ Cropped: {file}")
            except Exception as e:
                print(f"❌ Error with {file}: {e}")

# Example Usage
# Only convert all your DICOMs in a folder to PNG (no single-image inspection)
if __name__ == "__main__":
    # # ---- STEP 1: inspect a single DICOM to decide crop values ----
    # # Pick one representative DICOM file:
    # sample_file = "/mnt/data/dataset_training/last_strong_new/png_test/dcm/01004_023_06_6.dcm"

    # ds = load_dicom(sample_file)
    # print("Image shape (height, width):", ds.pixel_array.shape)
    # visualize_image(ds)  # hover mouse to read x, y in the status bar

    # # After you run this once and write down:
    # #   - y_start, y_end (top/bottom useful rows)
    # #   - x_start, x_end (left/right useful columns)
    # # compute:
    # #
    # #   H, W = ds.pixel_array.shape
    # #   top_crop_px    = y_start
    # #   bottom_crop_px = H - 1 - y_end
    # #   left_crop_px   = x_start
    # #   right_crop_px  = W - 1 - x_end
    # #
    # # Then comment out the block above and uncomment the batch conversion below.

    # ---- STEP 2 (after you know the four crop values): batch convert ----
    # TODO change to own directories
    input_dir = "/home/Documents/testing_github/data/"
    output_dir = "/home/Documents/testing_github/data/converted/"

    # TODO change crop values if necessary
    top_crop_px = 148
    bottom_crop_px = 216
    left_crop_px = 235
    right_crop_px = 244
    
    # Convert and crop dicom images
    input_dir_images = os.path.join(input_dir,'images/')
    output_dir_images = os.path.join(output_dir,'images/')
    os.makedirs(output_dir_images, exist_ok=True)
    convert_dicom_to_png(
        input_dir_images,
        output_dir_images,
        top_crop_px=top_crop_px,
        bottom_crop_px=bottom_crop_px,
        left_crop_px=left_crop_px,
        right_crop_px=right_crop_px
    )

    # Crop png masks
    input_dir_masks = os.path.join(input_dir,'masks/')
    output_dir_masks = os.path.join(output_dir,'masks/')
    os.makedirs(output_dir_masks, exist_ok=True)

    crop_all_pngs(input_dir_masks, 
                  output_dir_masks)

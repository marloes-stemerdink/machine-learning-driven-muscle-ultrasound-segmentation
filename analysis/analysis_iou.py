''' Script for analysis of segmentation results'''
'Look up input_dir and change to own directory. Change training_set, net and experiment if necessary'

import json
import os
import pandas as pd

def parse_filename(filename):
    parts = filename.replace(".png","").split("_")
    if len(parts) == 3: # healthy
        return pd.Series({
            "group": "healthy",
            "measurement": parts[2],
            "side": None,
            "visit": None
        })
    elif len(parts) == 4:
        if len(parts[-1]) == 1: # last_strong
            return pd.Series({
                "group": "last_strong",
                "measurement": parts[2],
                "side": None,
                "visit": parts[3]
            })
        elif len(parts[-1]) == 2: # klinisch
            return pd.Series({
                "group": "klinisch",
                "measurement": parts[3],
                "side": parts[2],
                "visit": None
            })
    raise ValueError(f"Unknown filename format: {filename}")

input_dir = '/home/Documents/testing_github/results/'  # change to directory pointing to ious.json file (group folder is specified later)
training_set = 'testing_github'    # change to training_set
net = 'knet_swin_mod'
experiment = 'subset_3'
file = f"segmentation_summary_{net}_{experiment}.json"
ious_dir = os.path.join(input_dir, file)

# Load muscle code mapping
muscle_map = pd.read_excel("input/Muscles.xlsx", sheet_name="codes")
muscle_map["Code"] = muscle_map["Code"].astype(int)

# Open file with ious
with open(ious_dir, 'r') as file:
    info = json.load(file)

df = pd.DataFrame(info)
df = df.rename(columns={"side": "json_side", "muscle_code": "code", "Muscle": "muscle_name"})   # rename side column in json file

# Add relevant file features based on filename (and group)
parsed = df["File"].apply(parse_filename)
df = pd.concat([df,parsed],axis=1)

keep_cols = ['File', 'iou','prec', 'rec','subject','code','side','measurement','visit','muscle_name','group']
df = df[keep_cols]

# Average iou per muscle
summary = df.groupby(["code","muscle_name", "group"]).agg(
    iou_mean = ( "iou","mean"),
    iou_sd = ( "iou","std"),
    prec_mean = ( "prec","mean"),
    prec_sd = ( "prec","std"),
    rec_mean = ( "rec","mean"),
    rec_sd = ( "rec","std"),
    count = ("iou","count")
)

print(summary.head())

if 'group' in locals() and 'training_set' in locals():
    # Save results
    df.to_csv(os.path.join(input_dir, f"ious_image_{training_set}_{group}.csv"), index=False)
    print(f"\nInidividual image IOUS CSV file saved to: {input_dir}")
    summary.to_csv(os.path.join(input_dir, f"ious_summary_{training_set}_{group}.csv"))
else:
    df.to_csv(os.path.join(input_dir, f"ious_image_{training_set}.csv"), index=False)
    print(f"\nIndividual image IOUS CSV file saved to: {input_dir}")
    summary.to_csv(os.path.join(input_dir, f"ious_summary_{training_set}.csv"))
print(f"\nSummary IOUS CSV file saved to: {input_dir}")


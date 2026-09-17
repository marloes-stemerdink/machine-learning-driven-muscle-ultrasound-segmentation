" Script for analysis segmentation results"
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

input_dir = '/mnt/data/model_to_train/subset_3/first_3000/testing_results/'  # change to directory pointing to ious.json file (group folder is specified later)
set = 'subset_3_training_3000_iters'    # change to set
# group = 'klinisch'   # change to group
# file = 'ious.json'
file = 'segmentation_summary_knet_swin_mod_muscle_specific.json'
# ious_dir = os.path.join(input_dir, group, file)
ious_dir = os.path.join(input_dir, file)

# Load muscle code mapping
muscle_map = pd.read_excel("/mnt/data/dataset_training/Muscles.xlsx", sheet_name="codes")
muscle_map["Code"] = muscle_map["Code"].astype(int)

# Open file with ious
with open(ious_dir, 'r') as file:
    info = json.load(file)
    # ious = info['iou']

df = pd.DataFrame(info)
df = df.rename(columns={"side": "json_side", "muscle_code": "code", "Muscle": "muscle_name"})   # rename side column in json file

# Add relevant file features based on filename (and group)
parsed = df["File"].apply(parse_filename)
df = pd.concat([df,parsed],axis=1)

keep_cols = ['File', 'iou','prec', 'rec','subject','code','side','measurement','visit','muscle_name','group']
df = df[keep_cols]


# Convert IOU column to float
# df["iou"] = df["iou"].astype(float)


# Define group based on filename
# if len(parts) == 3: # healthy
#     df[["subject","code","measurement"]] = (
#         df["File"]
#         .str.replace(".png","",regex=False)
#         .str.split("_", expand=True)
#         )
#     keep_cols = ['File', 'iou','prec', 'rec','subject','code','measurement','muscle_name']

# elif len(parts) ==4: # klinisch or last_strong
#     if len(parts[-1]) == 1: # last_strong
#         df[["subject","code","measurement", "visit"]] = (
#             df["File"]
#             .str.replace(".png","",regex=False)
#             .str.split("_", expand=True)
#             )
#         keep_cols = ['File', 'iou','prec', 'rec','subject','code','measurement','visit','muscle_name']
#     elif len(parts[-1]) ==2: # klinisch
#         df[["subject","code","side","measurement"]] = (
#         df["File"]
#         .str.replace(".png","",regex=False)
#         .str.split("_", expand=True)
#         )
#         keep_cols = ['File', 'iou','prec', 'rec','subject','code','side','measurement','muscle_name']


# if  group == 'last_strong':
#     df[["subject","code","measurement", "visit"]] = (
#         df["File"]
#         .str.replace(".png","",regex=False)
#         .str.split("_", expand=True)
#         )
#     keep_cols = ['File', 'iou','prec', 'rec','subject','code','measurement','visit','muscle_name']
# elif group == 'klinisch':
#     df[["subject","code","side","measurement"]] = (
#     df["File"]
#     .str.replace(".png","",regex=False)
#     .str.split("_", expand=True)
#     )
#     keep_cols = ['File', 'iou','prec', 'rec','subject','code','side','measurement','muscle_name']
# else:
#     df[["subject","code","measurement"]] = (
#         df["File"]
#         .str.replace(".png","",regex=False)
#         .str.split("_", expand=True)
#         )
#     keep_cols = ['File', 'iou','prec', 'rec','subject','code','measurement','muscle_name']


# Add muscle name via lookup
# df["muscle_int"] = df["code"].astype(int)
# df = df.merge(
#     muscle_map.rename(columns={"Code": "muscle_int", "Muscle": "muscle_name"}),
#     on="muscle_int",
#     how="left"
# ).drop(columns="muscle_int")

# df=df[keep_cols]
# print(df.head())

# Average iou per musclel
# summary = df.groupby(["code","muscle_name"])[["iou","prec","rec"]].agg(["mean","std","count"])
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

if 'group' in locals() and 'set' in locals():
    # Save results
    df.to_csv(os.path.join(input_dir, f"ious_grouped_{set}_{group}.csv"), index=False)
    print(f"\nGrouped IOUS CSV file saved to: {input_dir}")
    summary.to_csv(os.path.join(input_dir, f"ious_summary_{set}_{group}.csv"))
    print(f"\nSummary IOUS CSV file saved to: {input_dir}")
else:
    df.to_csv(os.path.join(input_dir, f"ious_grouped_{set}.csv"), index=False)
    print(f"\nGrouped IOUS CSV file saved to: {input_dir}")
    summary.to_csv(os.path.join(input_dir, f"ious_summary_{set}.csv"))
    print(f"\nSummary IOUS CSV file saved to: {input_dir}")


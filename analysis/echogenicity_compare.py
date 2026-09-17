import json
import os
from scipy.stats import ttest_rel
from scipy.stats import wilcoxon   
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def parse_filename(filename):
    parts = filename.replace(".png","").split("_")
    if len(parts) == 3: # healthy
        return pd.Series({
            "group": "healthy",
        })
    elif len(parts) == 4:
        if len(parts[-1]) == 1: # last_strong
            return pd.Series({
                "group": "last_strong",
            })
        elif len(parts[-1]) == 2: # klinisch
            return pd.Series({
                "group": "klinisch",
            })
    raise ValueError(f"Unknown filename format: {filename}")

# Define json file location
input_path = "/mnt/data/dataset_training/subset_1/results_inference_2/"
output_path = "/mnt/data/model_to_train/comparison/"
testing_round="base_model"
input_json_path = os.path.join(input_path,"segmentation_summary_knet_swin_mod_muscle_specific.json")

with open(input_json_path,"r") as f:
    data = json.load(f)

muscles = data["Muscle"]
gt_data = data["features_img_gt"]
pred_data = data["features_img_pred"]
filenames = data["File"]

# get mean echogenicity scores
mean_gt = {file_id:values["original_firstorder_Mean"]
           for file_id, values in gt_data.items()}

mean_pred = {file_id:values["original_firstorder_Mean"]
           for file_id, values in pred_data.items()
           if values != 'mask not found'
           }
n_skipped = len(pred_data)-len(mean_pred)
print(f"Skipped {n_skipped} files because of 'mask not found")

# Only include files that are in both predicted and ground truth
# common_ids=mean_gt.keys() & mean_pred.keys()
common_ids = [k for k in mean_gt if k in mean_pred]

# Paired t-test between predicted and ground truth echogenicity scores
# TODO per muscle 
result = ttest_rel(
    [float(mean_gt[k]) for k in common_ids],
    [float(mean_pred[k]) for k in common_ids]
)

print(result)

# Dataframe with ground truths, predicted scores and the corresponding muscle
# TODO add group (healthy, last strong, klinisch)
df = pd.DataFrame({
    # "file_id": list(common_ids),
    "file_id": [filenames[f] for f in common_ids],
    "muscle": [muscles[f] for f in common_ids],
    "gt": [float(mean_gt[f]) for f in common_ids],
    "pred": [float(mean_pred[f]) for f in common_ids]
    })

group = df["file_id"].apply(parse_filename)
df = pd.concat([df,group],axis=1)

print(df)
df.to_csv(os.path.join(input_path, "pred_gt.csv"),index=False)


# Paired t-test per muscle
results=[]
for (muscle, group), subset in df.groupby(["muscle","group"]):
    if len(subset) < 2:
        continue

    result = ttest_rel(
        subset["gt"],
        subset["pred"]
    )

    result2 = wilcoxon(
        subset["gt"],
        subset["pred"]
    )
    print(
        f"{group:11s} "
        f"{muscle:26s} "
        f"n ={len(subset):4d} "
        "paired t-test "
        f"t={result.statistic:8.3f} "
        f"p={result.pvalue:.4g}")
    print(
        f"{'Wilcoxon       ':>49}"
        f"t={result2.statistic:8.3f} "
        f"p={result2.pvalue:.4g}"      
    )

    results.append({
        "muscle": muscle,
        "group": group,
        "n": len(subset),
        "t_test": result.statistic,
        "p_t_test": result.pvalue,
        "Wilcoxon": result2.statistic,
        "p_wilcox": result2.pvalue
    })

df_results = pd.DataFrame(results)
df_results.to_csv(os.path.join(input_path, "paired_ttest_results.csv"),index=False)

# Bland Altman plot of all muscles together
df["mean"] = (df["gt"] + df["pred"])/2
df["difference"] = df["gt"] - df["pred"]

groups = sorted(df["group"].unique())

fig, axes = plt.subplots(
    1,3,
    figsize=(18,6),
    sharey=True
)

# plt.figure(figsize=(10,7))

for ax, group_name in zip(axes,groups):
    subset = df[df["group"] == group_name]
    muscle_order=sorted(df["muscle"].unique())
    sns.scatterplot(
        data=subset,
        x="mean",
        y="difference",
        hue="muscle",
        hue_order=muscle_order,
        alpha=0.7,
        ax=ax
    )

    bias=subset["difference"].mean()
    sd = subset["difference"].std()

    ax.axhline(bias, color="black", label=f"Bias = {bias:.2f}")
    ax.axhline(bias + 1.96 * sd, color="gray", linestyle="--")
    ax.axhline(bias - 1.96 * sd, color="gray", linestyle="--")

    ax.set_title(group_name)
    ax.set_xlabel("Mean of GT and prediction")
    ax.set_ylabel("Prediction - GT")

handles, labels = axes[0].get_legend_handles_labels()
for ax in axes:
    if ax.get_legend() is not None:
        ax.get_legend().remove()

fig.legend(
    handles,
    labels,
    title="Muscle",
    loc="lower center",
    # bbox_to_anchor=(0.5,-0.05),
    ncol=6
)

fig.subplots_adjust(bottom=0.4)


if 'testing_round' in locals():
    plt.savefig(f'{output_path}bland_altman_echogenicity_{testing_round}.png')
else:
    plt.savefig(f'{output_path}bland_altman_echogenicity.png')


# plt.tight_layout(rect=[0,0.1,1,1])

plt.show()



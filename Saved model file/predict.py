# =============================================================================
# THESE 4 LINES MUST STAY AT THE VERY TOP
# =============================================================================
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# =============================================================================

r"""
=============================================================================
FISH DISEASE DETECTION - OFFLINE PREDICTOR (SAVEDMODEL FORMAT)
=============================================================================

WHY THIS VERSION:
  Previous versions used save_weights() which can skip layers when the Keras
  setup differs between environments. This version loads the full SavedModel,
  so it matches the exported model from Colab.

SETUP:
  1. Create a clean virtual environment.
  2. Install:
       pip install tensorflow==2.16.1 pillow matplotlib numpy
  3. Extract the SavedModel folder to:
       C:\Users\tatha\OneDrive\Desktop\offline\saved_model
  4. Run:
       python predict.py

COMMANDS:
  Whole folder (default):
    python predict.py

  Single image:
    python predict.py --image "C:\path\to\fish.jpg"

  Custom folder:
    python predict.py --folder "C:\path\to\folder"

  Change threshold:
    python predict.py --threshold 0.31=
    ============================================================================
"""

import argparse
import sys
import warnings

import numpy as np
from PIL import Image

warnings.filterwarnings("ignore")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# -----------------------------------------------------------------------------
# CONFIGURATION - update these paths
# -----------------------------------------------------------------------------
SAVED_MODEL_PATH = r"C:\Users\tatha\OneDrive\Desktop\offline\saved_model"
FOLDER_PATH = r"C:\Users\tatha\OneDrive\Desktop\offline\my_fish_images"

THRESHOLD = 0.40
# prob >= THRESHOLD -> HEALTHY (class 1)
# prob < THRESHOLD -> DISEASED (class 0)

IMG_SIZE = (224, 224)
VALID_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
try:
    import tensorflow as tf
except Exception as exc:
    print(f"\n  ERROR: TensorFlow import failed -> {exc}")
    print("\n  Fix:")
    print("    Create a clean virtual environment and install:")
    print("    pip install tensorflow==2.16.1 pillow matplotlib numpy")
    sys.exit(1)

if not hasattr(tf, "saved_model"):
    print("\n  ERROR: TensorFlow is installed, but the import is incomplete.")
    print("  This Python environment has a broken TensorFlow package.")
    print("  Fix:")
    print("    Create a clean virtual environment and install:")
    print("    pip install tensorflow==2.16.1 pillow matplotlib numpy")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    PLOTS = True
except Exception:
    PLOTS = False


# -----------------------------------------------------------------------------
# LOAD MODEL - TF SavedModel format
# -----------------------------------------------------------------------------
def load_saved_model():
    if not os.path.exists(SAVED_MODEL_PATH):
        print("\n  X SavedModel folder not found:")
        print(f"    {SAVED_MODEL_PATH}")
        print("\n  Fix:")
        print("    1. In Colab run:")
        print("         model.export('/content/drive/.../saved_model')")
        print("    2. Zip and download the saved_model folder from Drive")
        print(f"    3. Extract it to: {SAVED_MODEL_PATH}")
        sys.exit(1)

    print("  Loading SavedModel ...", end=" ", flush=True)
    try:
        model = tf.saved_model.load(SAVED_MODEL_PATH)
        infer = model.signatures.get(
            "serving_default",
            list(model.signatures.values())[0],
        )
        print("done\n")
        return infer
    except Exception as exc:
        print(f"FAILED\n  {exc}")
        print("\n  Make sure you exported with model.export() in Colab")
        sys.exit(1)


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def load_image(image_path):
    """Return raw pixels [0,255]; preprocessing is inside the SavedModel."""
    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = np.asarray(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    return tf.constant(arr), img


def run_inference(infer, arr):
    """Run inference using the SavedModel signature."""
    input_key = list(infer.structured_input_signature[1].keys())[0]
    output_key = list(infer.structured_outputs.keys())[0]
    result = infer(**{input_key: arr})
    prob = float(result[output_key].numpy().flatten()[0])
    return prob


def get_result(prob, threshold=THRESHOLD):
    label = "HEALTHY" if prob >= threshold else "DISEASED"
    conf = prob if prob >= threshold else 1.0 - prob
    return label, conf


# -----------------------------------------------------------------------------
# PREDICT SINGLE IMAGE
# -----------------------------------------------------------------------------
def predict_single(infer, image_path, threshold=THRESHOLD):
    if not os.path.exists(image_path):
        print(f"\n  X Image not found: {image_path}")
        return None, None

    arr, img = load_image(image_path)
    prob = run_inference(infer, arr)
    label, conf = get_result(prob, threshold)
    icon = "[OK]" if label == "HEALTHY" else "[X]"
    color = "green" if label == "HEALTHY" else "red"

    print("\n  +----------------------------------------------+")
    print(f"  |  File       : {os.path.basename(image_path)[:30]:<30}|")
    print(f"  |  Result     : {icon} {label:<25}|")
    print(f"  |  Confidence : {conf:.2%:<30}|")
    print(f"  |  Raw prob   : {prob:.6f:<30}|")
    print("  +----------------------------------------------+")

    if PLOTS:
        try:
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.imshow(img)
            ax.set_title(
                f"{label}\nConfidence: {conf:.2%}",
                fontsize=15,
                fontweight="bold",
                color=color,
                pad=12,
            )
            ax.axis("off")
            for spine in ax.spines.values():
                spine.set_edgecolor(color)
                spine.set_linewidth(5)
            plt.tight_layout()
            plt.close(fig)
        except Exception as exc:
            print(f"  [!] Plot error: {exc}")

    return label, conf


# -----------------------------------------------------------------------------
# PREDICT WHOLE FOLDER
# -----------------------------------------------------------------------------
def predict_folder(infer, folder_path, threshold=THRESHOLD):
    if not os.path.isdir(folder_path):
        print(f"\n  X Folder not found: {folder_path}")
        return

    images = sorted(
        f for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in VALID_EXT
    )

    if not images:
        print(f"\n  X No images found in: {folder_path}")
        print(f"  Supported: {', '.join(sorted(VALID_EXT))}")
        return

    print(f"\n  Found {len(images)} image(s) - predicting...\n")
    print(f"  {'#':<5}{'Filename':<36}{'Result':<12}{'Confidence':>11}{'Prob':>8}")
    print("  " + "-" * 74)

    results = {"HEALTHY": [], "DISEASED": []}
    all_probs = []

    for idx, fname in enumerate(images, 1):
        img_path = os.path.join(folder_path, fname)
        try:
            arr, _ = load_image(img_path)
            prob = run_inference(infer, arr)
            label, conf = get_result(prob, threshold)
            icon = "[OK]" if label == "HEALTHY" else "[X]"
            results[label].append(fname)
            all_probs.append(prob)
            short = fname if len(fname) <= 35 else fname[:32] + "..."
            print(f"  {idx:<5}{short:<36}{icon} {label:<7}{conf:>12.2%}{prob:>8.4f}")
        except Exception as exc:
            print(f"  {idx:<5}{fname:<36}  ERROR: {exc}")

    print("  " + "-" * 74)

    total = len(images)
    healthy_count = len(results["HEALTHY"])
    diseased_count = len(results["DISEASED"])

    print(
        f"""
  +---------------------------------------------+
  |                 SUMMARY                     |
  +---------------------------------------------+
  |  Total fish    : {total:<26}|
  |  Healthy       : {healthy_count} ({healthy_count / total * 100:.1f}%){'':<18}|
  |  Diseased      : {diseased_count} ({diseased_count / total * 100:.1f}%){'':<18}|
  |  Threshold     : {threshold:<26}|
  +---------------------------------------------+"""
    )

    if results["DISEASED"]:
        print("\n  Diseased fish:")
        for fname in results["DISEASED"]:
            print(f"      {fname}")

    if results["HEALTHY"]:
        print("\n  Healthy fish:")
        for fname in results["HEALTHY"]:
            print(f"      {fname}")

    if PLOTS and total > 0:
        try:
            fig, axes = plt.subplots(1, 2, figsize=(13, 5))

            bar_colors = [
                "#4CAF50" if prob >= threshold else "#F44336"
                for prob in all_probs
            ]
            axes[0].bar(
                range(1, total + 1),
                all_probs,
                color=bar_colors,
                edgecolor="white",
                linewidth=0.5,
            )
            axes[0].axhline(
                y=threshold,
                color="navy",
                linestyle="--",
                linewidth=1.5,
            )
            axes[0].set_xlabel("Fish #", fontsize=11)
            axes[0].set_ylabel("Probability (>= threshold = HEALTHY)", fontsize=10)
            axes[0].set_title("Prediction per Fish", fontsize=12, fontweight="bold")
            axes[0].set_xticks(range(1, total + 1))
            axes[0].set_xticklabels(
                [str(idx) for idx in range(1, total + 1)],
                rotation=45,
                ha="right",
            )
            axes[0].set_ylim(0, 1.1)
            axes[0].grid(axis="y", alpha=0.3)

            healthy_patch = mpatches.Patch(
                color="#4CAF50", label=f"Healthy ({healthy_count})"
            )
            diseased_patch = mpatches.Patch(
                color="#F44336", label=f"Diseased ({diseased_count})"
            )
            threshold_patch = mpatches.Patch(
                color="navy", label=f"Threshold = {threshold}"
            )
            axes[0].legend(
                handles=[healthy_patch, diseased_patch, threshold_patch],
                fontsize=9,
            )

            pie_vals = [value for value in [healthy_count, diseased_count] if value > 0]
            pie_labels = [
                label
                for label, value in zip(
                    [f"Healthy\n{healthy_count}", f"Diseased\n{diseased_count}"],
                    [healthy_count, diseased_count],
                )
                if value > 0
            ]
            pie_colors = [
                color
                for color, value in zip(
                    ["#4CAF50", "#F44336"],
                    [healthy_count, diseased_count],
                )
                if value > 0
            ]

            axes[1].pie(
                pie_vals,
                labels=pie_labels,
                colors=pie_colors,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 12},
                wedgeprops={"edgecolor": "white", "linewidth": 2},
            )
            axes[1].set_title("Overall Split", fontsize=12, fontweight="bold")

            plt.suptitle("Fish Disease Detection - Results", fontsize=14, fontweight="bold")
            plt.tight_layout()
            plt.close(fig)
        except Exception as exc:
            print(f"\n  [!] Plot error: {exc}")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    tf_version = getattr(tf, "__version__", "unknown")

    print("\n" + "=" * 57)
    print("  FISH DISEASE DETECTION - OFFLINE PREDICTOR")
    print("=" * 57)
    print(f"\n  TensorFlow    : {tf_version}")
    gpus = tf.config.list_physical_devices("GPU")
    print(f"  GPU           : {gpus if gpus else 'None (CPU mode)'}")
    print(f"  SavedModel    : {SAVED_MODEL_PATH}")
    print(f"  Folder        : {FOLDER_PATH}\n")

    parser = argparse.ArgumentParser(
        description="Fish Disease Detection - Offline Predictor"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to a single fish image",
    )
    parser.add_argument(
        "--folder",
        type=str,
        default=FOLDER_PATH,
        help="Path to folder of fish images",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=THRESHOLD,
        help=f"Decision threshold (default {THRESHOLD})",
    )
    args = parser.parse_args()

    infer = load_saved_model()

    if args.image:
        predict_single(infer, args.image, threshold=args.threshold)
    else:
        predict_folder(infer, args.folder, threshold=args.threshold)

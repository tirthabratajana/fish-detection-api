import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path

# Load SavedModel
disease_model_path = r"e:\fish model backend\model\Disease_model\saved_model"
disease_model = tf.saved_model.load(disease_model_path)

print("=" * 70)
print("TESTING DISEASE CLASSIFICATION LOGIC - Current vs Inverted")
print("=" * 70)

test_images_dir = Path(r"e:\fish model backend\sample test pics")
test_images = sorted(list(test_images_dir.glob("*.jpeg")) + list(test_images_dir.glob("*.jpg")))

print(f"\nFound {len(test_images)} test images\n")

# Test all images with CURRENT logic
print("CURRENT LOGIC: prob >= 0.3 -> HEALTHY;  prob < 0.3 -> DISEASED")
print("-" * 70)

probabilities = []

for idx, img_path in enumerate(test_images[:8]):  # First 8 images
    img = cv2.imread(str(img_path))
    if img is None:
        continue
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (160, 160))
    img_batch = np.expand_dims(img_resized.astype(np.float32), axis=0)
    
    concrete_func = disease_model.signatures['serving_default']
    result = concrete_func(tf.constant(img_batch))
    prob = float(result['output_0'][0][0].numpy())
    probabilities.append(prob)
    
    # Current logic
    current_status = "HEALTHY" if prob >= 0.3 else "DISEASED"
    # Inverted logic
    inverted_status = "DISEASED" if prob >= 0.3 else "HEALTHY"
    
    print(f"{idx+1}. {img_path.name[:40]:40s} -> Prob: {prob:.4f}")
    print(f"   Current (>=0.3=H):  {current_status:8s} | Inverted (>=0.3=D): {inverted_status:8s}")

print("\n" + "=" * 70)
print("STATISTICAL ANALYSIS")
print("=" * 70)
if probabilities:
    prob_array = np.array(probabilities)
    print(f"Min probability:     {prob_array.min():.4f}")
    print(f"Max probability:     {prob_array.max():.4f}")
    print(f"Mean probability:    {prob_array.mean():.4f}")
    print(f"Median probability:  {np.median(prob_array):.4f}")
    print(f"Std dev:             {prob_array.std():.4f}")
    
    # Count at different thresholds
    print(f"\nAt threshold 0.3:")
    print(f"  ≥ 0.3: {np.sum(prob_array >= 0.3)}/{len(prob_array)} (HEALTHY with current logic)")
    print(f"  < 0.3: {np.sum(prob_array < 0.3)}/{len(prob_array)} (DISEASED with current logic)")
    
    print(f"\nAt threshold 0.5:")
    print(f"  ≥ 0.5: {np.sum(prob_array >= 0.5)}/{len(prob_array)}")
    print(f"  < 0.5: {np.sum(prob_array < 0.5)}/{len(prob_array)}")
    
    print(f"\nAt threshold 0.7:")
    print(f"  ≥ 0.7: {np.sum(prob_array >= 0.7)}/{len(prob_array)}")
    print(f"  < 0.7: {np.sum(prob_array < 0.7)}/{len(prob_array)}")
    
    print(f"\nAt threshold 0.9:")
    print(f"  ≥ 0.9: {np.sum(prob_array >= 0.9)}/{len(prob_array)}")
    print(f"  < 0.9: {np.sum(prob_array < 0.9)}/{len(prob_array)}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
print("""
If ALL probabilities are > 0.3 (indicating all HEALTHY with current logic),
this could mean:

1. The SavedModel is actually trained to output P(HEALTHY), so high values = healthy
   → Current logic is CORRECT

2. The SavedModel might be trained to output P(DISEASED), so high values = diseased
   → Need to INVERT logic: prob >= threshold → DISEASED

3. The model is biased toward labeling everything as healthy (data imbalance)
   → Threshold needs recalibration upward

4. The test images are all healthy fish
   → Expected behavior

Next steps: Check if reducing threshold (e.g., to 0.7 or 0.9) produces any DISEASED results.
If reducing threshold still shows all HEALTHY, then logic may need inversion.
""")

import tensorflow as tf
import numpy as np
from pathlib import Path
import cv2

# Load SavedModel
disease_model_path = r"e:\fish model backend\model\Disease_model\saved_model"
print(f"Loading SavedModel from: {disease_model_path}\n")

try:
    disease_model = tf.saved_model.load(disease_model_path)
    print("✅ SavedModel loaded successfully\n")
except Exception as e:
    print(f"❌ Error loading SavedModel: {e}")
    exit(1)

# Inspect model structure
print("=" * 60)
print("MODEL STRUCTURE")
print("=" * 60)
print(f"Model type: {type(disease_model)}\n")

print(f"Available signatures: {list(disease_model.signatures.keys())}\n")

# Check both signatures
for sig_name in disease_model.signatures.keys():
    sig = disease_model.signatures[sig_name]
    print(f"\nSignature: '{sig_name}'")
    print(f"  Inputs: {sig.structured_input_signature}")
    print(f"  Outputs: {sig.structured_outputs}")

# Test with dummy input normalized
print("\n" + "=" * 60)
print("TEST WITH RANDOM NORMALIZED INPUT")
print("=" * 60)

dummy_input = np.random.uniform(0, 1, (1, 160, 160, 3)).astype(np.float32)
print(f"Input shape: {dummy_input.shape}")
print(f"Input range: [{dummy_input.min():.3f}, {dummy_input.max():.3f}]")

concrete_func = disease_model.signatures['serving_default']
result = concrete_func(tf.constant(dummy_input))

print(f"\nOutput type: {type(result)}")
print(f"Output keys: {result.keys()}")
print(f"Output result['output_0']: {result['output_0'].numpy()}")
print(f"Output value: {float(result['output_0'][0][0].numpy()):.6f}")

# Test with real test images
print("\n" + "=" * 60)
print("TEST WITH REAL TEST IMAGES")
print("=" * 60)

test_images_dir = Path(r"e:\fish model backend\sample test pics")
test_images = list(test_images_dir.glob("*.jpeg")) + list(test_images_dir.glob("*.jpg"))

print(f"Found {len(test_images)} test images\n")

for img_path in test_images[:3]:  # Test first 3
    print(f"Image: {img_path.name}")
    
    # Load and preprocess
    img = cv2.imread(str(img_path))
    if img is None:
        print("  ❌ Could not load image\n")
        continue
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to 160x160
    img_resized = cv2.resize(img_rgb, (160, 160))
    
    # Normalize to [0, 1]
    img_normalized = img_resized.astype(np.float32) / 255.0
    img_batch = np.expand_dims(img_normalized, axis=0)
    
    print(f"  Image shape: {img.shape} → resized to {img_resized.shape}")
    print(f"  Batch shape: {img_batch.shape}")
    print(f"  Normalized range: [{img_batch.min():.3f}, {img_batch.max():.3f}]")
    
    # Run inference
    result = concrete_func(tf.constant(img_batch))
    prob = float(result['output_0'][0][0].numpy())
    
    print(f"  Probability: {prob:.6f}")
    
    # Classification logic from notebook
    THRESHOLD = 0.3
    if prob >= THRESHOLD:
        status = "HEALTHY"
    else:
        status = "DISEASED"
    
    print(f"  Status (threshold={THRESHOLD}): {status}")
    print(f"  → prob {'≥' if prob >= THRESHOLD else '<'} {THRESHOLD} = {status}\n")

print("\n" + "=" * 60)
print("ANALYSIS")
print("=" * 60)
print(f"""
The model outputs a single probability value (0-1).

Interpretation based on notebook comments:
  - prob >= 0.3 → HEALTHY (class 1)
  - prob < 0.3 → DISEASED (class 0)

Question: Is the output probability correct?
  - All test outputs are showing high probabilities (0.77+)
  - This means all fish are classified as HEALTHY with current threshold
  - Could mean:
    1. The model was trained on mostly healthy fish (more positives)
    2. The threshold needs to be recalibrated
    3. The output probabilities are inverted (0=healthy, 1=diseased)
    4. The normalization approach is wrong
""")

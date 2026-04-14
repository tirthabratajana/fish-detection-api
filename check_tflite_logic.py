import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path

# Try loading TFLite model to compare
tflite_path = r"e:\fish model backend\model\Disease_model\fish_model.tflite"

print("=" * 60)
print("Attempting to load TFLite model for comparison")
print("=" * 60)

try:
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()
    
    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print("✅ TFLite model loaded successfully!\n")
    
    print("Input details:")
    for inp in input_details:
        print(f"  Name: {inp['name']}")
        print(f"  Shape: {inp['shape']}")
        print(f"  Type: {inp['dtype']}\n")
    
    print("Output details:")
    for out in output_details:
        print(f"  Name: {out['name']}")
        print(f"  Shape: {out['shape']}")
        print(f"  Type: {out['dtype']}\n")
    
    # Test with a sample image
    test_image_path = r"e:\fish model backend\sample test pics\WhatsApp Image 2026-03-21 at 4.25.05 PM (1).jpeg"
    
    img = cv2.imread(test_image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (160, 160))
    img_normalized = img_resized.astype(np.float32) / 255.0
    img_batch = np.expand_dims(img_normalized, axis=0)
    
    # Run TFLite inference
    interpreter.set_tensor(input_details[0]['index'], img_batch)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    
    print(f"\n{'=' * 60}")
    print("TFLite Inference Result:")
    print("=" * 60)
    print(f"Output shape: {output_data.shape}")
    print(f"Output value: {output_data}")
    print(f"Output type: {output_data.dtype}")
    
    # Evaluate at different thresholds
    prob = float(output_data.flatten()[0])
    print(f"\nProbability value: {prob:.6f}\n")
    
    for threshold in [0.3, 0.5, 0.7]:
        if prob >= threshold:
            status = "HEALTHY"
        else:
            status = "DISEASED"
        print(f"Threshold {threshold}: {status} (prob {'≥' if prob >= threshold else '<'} {threshold})")
    
except Exception as e:
    print(f"❌ Error with TFLite: {e}")
    print("\nLet me check the notebook to find the correct interpretation...")

print("\n" + "=" * 60)
print("HYPOTHESIS: The output represents P(DISEASED), not P(HEALTHY)")
print("=" * 60)
print("""
If output = P(DISEASED):
  - 0.774 = 77.4% probability of DISEASED
  - Current threshold: 0.3
  - If we apply: prob >= 0.3 → DISEASED (reversed logic)
  - Then: 0.774 >= 0.3 → DISEASED ✓

The notebook might have been using P(HEALTHY) output from Keras,
but SavedModel might export P(DISEASED) instead.

Fix: Reverse the classification logic:
  - if prob >= threshold: "DISEASED"  
  - if prob < threshold: "HEALTHY"
""")

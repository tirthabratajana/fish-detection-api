"""
Debug script to inspect SavedModel disease detection output
"""
import tensorflow as tf
import numpy as np
from PIL import Image

# Load the SavedModel
model_path = '../model/Disease_model/saved_model'
try:
    model = tf.saved_model.load(model_path)
    print("✅ Model loaded successfully")
    print(f"Model type: {type(model)}")
    print(f"Model dir: {dir(model)}")
    
    # Check for signatures
    if hasattr(model, 'signatures'):
        print(f"\nAvailable signatures: {list(model.signatures.keys())}")
        for sig_name in model.signatures.keys():
            sig = model.signatures[sig_name]
            print(f"\nSignature '{sig_name}':")
            print(f"  Inputs: {sig.structured_input_signature}")
            print(f"  Outputs: {sig.structured_outputs}")
    
    # Try making a prediction with dummy input
    print("\n" + "="*60)
    print("Testing inference with dummy input (160x160x3)")
    print("="*60)
    
    dummy_input = np.random.randn(1, 160, 160, 3).astype(np.float32)
    print(f"Dummy input shape: {dummy_input.shape}")
    
    # Try different calling methods
    print("\n1. Direct model call:")
    try:
        result = model(tf.constant(dummy_input))
        print(f"   Result type: {type(result)}")
        print(f"   Result: {result}")
        if isinstance(result, dict):
            for key, val in result.items():
                print(f"     {key}: {val.shape if hasattr(val, 'shape') else type(val)}")
        elif isinstance(result, (list, tuple)):
            for i, item in enumerate(result):
                print(f"     [{i}]: {item.shape if hasattr(item, 'shape') else type(item)}")
                print(f"          Value: {item}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Using concrete function:")
    try:
        concrete_func = model.signatures['serving_default']
        result = concrete_func(tf.constant(dummy_input))
        print(f"   Result type: {type(result)}")
        print(f"   Result: {result}")
        if isinstance(result, dict):
            for key, val in result.items():
                print(f"     {key}: shape={val.shape}, dtype={val.dtype}")
                print(f"            value={val.numpy()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Checking model call method:")
    try:
        # List all callable methods
        callables = [attr for attr in dir(model) if callable(getattr(model, attr))]
        print(f"   Available methods: {callables}")
    except Exception as e:
        print(f"   Error: {e}")

except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()

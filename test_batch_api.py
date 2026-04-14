import requests
import json
from pathlib import Path

# Test the batch API with multiple images
test_images_dir = r"e:\fish model backend\sample test pics"
image_files = list(Path(test_images_dir).glob("*.jpeg")) + list(Path(test_images_dir).glob("*.jpg"))

print(f"Found {len(image_files)} test images")

if image_files:
    # Test with first 2 images
    test_images = image_files[:2]
    
    url = "http://127.0.0.1:8000/predict-batch"
    
    files = [("files", (img.name, open(img, "rb"), "image/jpeg")) for img in test_images]
    
    print(f"\n📤 Sending batch request with {len(test_images)} images...")
    
    response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Batch API Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ API Error:")
        print(response.text)
else:
    print("No test images found")

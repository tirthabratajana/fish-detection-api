import requests
import json
from pathlib import Path

# Test the API with the test image
test_image = r"e:\fish model backend\sample test pics\WhatsApp Image 2026-03-21 at 4.25.05 PM (1).jpeg"

# Check if file exists
if not Path(test_image).exists():
    print(f"❌ Test image not found: {test_image}")
    exit(1)

print(f"✅ Found test image: {test_image}")

# Send request to API
url = "http://127.0.0.1:8000/predict"

with open(test_image, "rb") as f:
    files = {"file": (test_image, f, "image/jpeg")}
    print(f"\n📤 Sending POST request to {url}...")
    
    response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ API Response:")
        print(json.dumps(result, indent=2))
        
        # Verify disease detection is working
        print(f"\n📊 Disease Detection Status:")
        print(f"   Status: {result.get('disease_status', 'N/A')}")
        print(f"   Confidence: {result.get('disease_confidence', 0):.4f}")
        print(f"   Confidence %: {result.get('disease_confidence_percent', 'N/A')}")
    else:
        print(f"❌ API Error:")
        print(response.text)

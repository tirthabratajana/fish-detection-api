#!/bin/bash
# Diagnostic script to test if FastAPI app can start

cd /app/fastapi_app

echo "🔍 Starting diagnostic checks..."
echo ""

# Check Python version
echo "1️⃣ Python Version:"
python --version
echo ""

# Check if requirements installed
echo "2️⃣ Checking installed packages:"
python -c "
import sys
packages = ['fastapi', 'uvicorn', 'tensorflow', 'torch', 'ultralytics', 'PIL']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg}')
    except ImportError as e:
        print(f'  ❌ {pkg}: {e}')
"
echo ""

# Try importing the main app
echo "3️⃣ Importing FastAPI app:"
python -c "
try:
    from app.main import app
    print('  ✅ FastAPI app imported successfully')
except Exception as e:
    print(f'  ❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
echo ""

# Try loading models
echo "4️⃣ Loading models (this may take a moment):"
timeout 120 python -c "
try:
    from app.utils.model_loader import ModelLoader
    import os
    
    MODEL_BASE_PATH = '/app'
    YOLO_PATH = os.path.join(MODEL_BASE_PATH, 'best.pt')
    EFFICIENTNET_PATH = os.path.join(MODEL_BASE_PATH, 'efficientnet_fish.h5')
    CLASS_MAP_PATH = os.path.join(MODEL_BASE_PATH, 'clf_class_names.json')
    DISEASE_PATH = os.path.join(MODEL_BASE_PATH, 'model', 'Disease_model', 'fish.tflite')
    
    print(f'  YOLO model exists: {os.path.exists(YOLO_PATH)}')
    print(f'  EfficientNet model exists: {os.path.exists(EFFICIENTNET_PATH)}')
    print(f'  Disease model exists: {os.path.exists(DISEASE_PATH)}')
    print(f'  Class map exists: {os.path.exists(CLASS_MAP_PATH)}')
    print('')
    
    print('  ⏳ Loading models...')
    yolo_m, effnet_m, disease_m, classes = ModelLoader.setup_models(
        yolo_model_path=YOLO_PATH,
        efficientnet_model_path=EFFICIENTNET_PATH,
        disease_model_path=DISEASE_PATH,
        class_map_path=CLASS_MAP_PATH
    )
    print('  ✅ All models loaded successfully')
except Exception as e:
    print(f'  ❌ Error loading models: {e}')
    import traceback
    traceback.print_exc()
" || echo "  ⚠️ Model loading timed out (>120 seconds) - may be memory issue"
echo ""

# Check memory usage
echo "5️⃣ System Resources:"
python -c "
import psutil
import os
mem = psutil.virtual_memory()
print(f'  Available RAM: {mem.available / 1024 / 1024:.0f} MB')
print(f'  Total RAM: {mem.total / 1024 / 1024:.0f} MB')
print(f'  CPU Count: {os.cpu_count()}')
"
echo ""

echo "✅ Diagnostic complete!"
echo ""
echo "If all checks pass, the app should start successfully with:"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 10000"

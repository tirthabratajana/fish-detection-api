#!/bin/bash

# Render Deployment Setup Script
# Run this before pushing to GitHub

echo "🚀 Preparing for Render Deployment..."

# Check if Git LFS is installed
if ! command -v git-lfs &> /dev/null; then
    echo "⚠️  Git LFS not installed. Installing..."
    # Ubuntu/Debian
    sudo apt-get install git-lfs
    # macOS
    # brew install git-lfs
fi

# Initialize Git LFS
echo "📦 Setting up Git LFS..."
git lfs install

# Track large files
echo "📝 Tracking large model files..."
git lfs track "*.pt"
git lfs track "*.h5"
git lfs track "*.tflite"
git lfs track "*.pb"

# Add .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking for model files" || true

# Verify large files are tracked
echo "✅ Git LFS Configuration:"
git lfs ls-files

echo ""
echo "📚 Next Steps:"
echo "1. Create GitHub repository"
echo "2. Add your GitHub as remote: git remote add origin <your-repo-url>"
echo "3. Push to GitHub: git push -u origin main"
echo "4. Go to https://dashboard.render.com"
echo "5. Connect your GitHub repository"
echo "6. Create persistent disk for models"
echo "7. Deploy!"
echo ""
echo "For detailed instructions, see RENDER_DEPLOYMENT.md"

@echo off
REM Render Deployment Setup Script for Windows
REM Run this before pushing to GitHub

echo 🚀 Preparing for Render Deployment...

REM Check if Git LFS is installed
where git-lfs >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Git LFS not found. Please install from: https://git-lfs.github.com
    pause
    exit /b 1
)

REM Initialize Git LFS
echo 📦 Setting up Git LFS...
call git lfs install

REM Track large files
echo 📝 Tracking large model files...
call git lfs track "*.pt"
call git lfs track "*.h5"
call git lfs track "*.tflite"
call git lfs track "*.pb"

REM Add .gitattributes
call git add .gitattributes
call git commit -m "Add Git LFS tracking for model files" 2>nul

REM Verify large files are tracked
echo ✅ Git LFS Configuration:
call git lfs ls-files

echo.
echo 📚 Next Steps:
echo 1. Create GitHub repository
echo 2. Add your GitHub as remote: git remote add origin [your-repo-url]
echo 3. Push to GitHub: git push -u origin main
echo 4. Go to https://dashboard.render.com
echo 5. Connect your GitHub repository
echo 6. Create persistent disk for models
echo 7. Deploy!
echo.
echo For detailed instructions, see RENDER_DEPLOYMENT.md
pause

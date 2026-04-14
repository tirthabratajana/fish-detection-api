"""
Startup script to run the FastAPI server
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Change to the fastapi_app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Run uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

import os

from pathlib import Path

# Get project root directory
# Or use absolute path pointing to backend directory, e.g. on Windows: BasePath = D:\git_project\fastapi_mysql\backend
BasePath = Path(__file__).resolve().parent.parent.parent


LOG_DIR = os.path.join(BasePath, "log")

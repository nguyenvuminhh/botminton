import uvicorn

from backend.app import create_app
from config import API_PORT

app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend_main:app", host="0.0.0.0", port=API_PORT, reload=False)

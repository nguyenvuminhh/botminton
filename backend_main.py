import os
import uvicorn

from backend.app import create_app
from config import API_PORT

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", API_PORT))  # platforms like Railway inject PORT
    uvicorn.run("backend_main:app", host="0.0.0.0", port=port, reload=False)

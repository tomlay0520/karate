import uvicorn
from api.match_api import app
from config.settings import Settings

settings = Settings()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
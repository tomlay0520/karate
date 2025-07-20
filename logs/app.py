import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.match_api import app

# 挂载前端静态文件
app.mount("../frontend", StaticFiles(directory="frontend"), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
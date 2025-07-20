import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.match_api import app

# 获取当前文件所在目录（logs）
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建 frontend 的绝对路径
frontend_path = os.path.join(current_dir, "..", "frontend")

# 挂载前端静态文件
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

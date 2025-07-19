# 引入 FastAPI 主类和 HTTP 异常处理模块
from fastapi import FastAPI, HTTPException
# 使用 Pydantic 创建请求数据模型
from pydantic import BaseModel
# 引入可选类型支持
from typing import Optional
# 从项目内部导入比赛逻辑模块（假设放在上级目录的 Model 文件夹中）
from Model.match_logic import KarateMatchSystem

# 创建 FastAPI 应用实例
app = FastAPI()

# 定义前端请求数据的数据结构（比赛分组请求）
class MatchRequest(BaseModel):
    category_type: str  # 比赛类别，例如 'kumite'（组手）或 'kata'（型）
    competition_type: Optional[str] = None  # 比赛类型，如 'weighted'（分量制）或 'open'（无差别）
    age: Optional[int] = None  # 选手年龄
    gender: Optional[str] = None  # 性别，'male' 或 'female'
    weight_input: Optional[str] = None  # 用户输入的体重数据（字符串形式）
    weight_flag: Optional[bool] = None  # 是否启用体重规则
    group_type: Optional[str] = None  # 分组类型（可选扩展，如根据段位等）
    open_category: Optional[str] = None  # 无差别比赛的类别（可选）

# API 路由：接收选手匹配请求（POST 方法），路径为 /api/match
@app.post("/api/match")
async def match_athletes(request: MatchRequest):
    try:
        # 创建比赛系统对象，连接数据库文件
        match_system = KarateMatchSystem("karate.db")
        
        # 根据用户请求参数获取匹配的选手信息
        athletes = match_system.get_athletes_by_category(
            request.category_type,
            competition_type=request.competition_type,
            age=request.age,
            gender=request.gender,
            weight_input=request.weight_input,
            weight_flag=request.weight_flag,
            group_type=request.group_type,
            open_category=request.open_category
        )
        
        # 返回匹配成功结果
        return {"status": "success", "athletes": athletes}
    
    except Exception as e:
        # 如果发生异常，返回 500 错误并附上错误信息
        raise HTTPException(status_code=500, detail=str(e))

# API 路由：更新 A/B/C 分组名称，路径为 /api/group_names，使用 POST 方法
@app.post("/api/group_names")
async def update_group_names(group_a: str, group_b: str, group_c: str):
    try:
        # 创建比赛系统对象，连接数据库
        match_system = KarateMatchSystem("karate.db")
        
        # 调用系统逻辑，更新三组的名称
        match_system.update_group_names(group_a, group_b, group_c)
        
        # 返回更新成功状态
        return {"status": "success"}
    
    except Exception as e:
        # 异常处理，返回 500 错误及具体原因
        raise HTTPException(status_code=500, detail=str(e))

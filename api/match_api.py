from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
from Model.match_logic import KarateMatchSystem
from Model.excel_to_db import excel_to_db
from config.settings import Settings
import os
import logging
import sqlite3

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
settings = Settings()

# 初始化全局组别名称
GROUP_A = "甲组"
GROUP_B = "乙组"
GROUP_C = "丙组"


class MatchRequest(BaseModel):
    category_type: str
    competition_type: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_input: Optional[str] = None
    weight_flag: Optional[bool] = None
    group_type: Optional[str] = None
    open_category: Optional[str] = None


class MatchTreeRequest(BaseModel):
    athletes: List[Dict]
    category: str


class GroupNames(BaseModel):
    group_a: str
    group_b: str
    group_c: str


@app.post("/api/match")
async def match_athletes(request: MatchRequest):
    try:
        match_system = KarateMatchSystem(settings.DATABASE_PATH)
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
        logger.info(f"查询到 {len(athletes)} 名运动员")
        return {"status": "success", "athletes": athletes}
    except Exception as e:
        logger.error(f"查询运动员失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/group_names")
async def get_group_names():
    """
    获取当前组别名称
    """
    return {
        "group_a": GROUP_A,
        "group_b": GROUP_B,
        "group_c": GROUP_C
    }


@app.post("/api/group_names")
async def update_group_names(group_names: GroupNames):
    """
    更新组别名称
    """
    global GROUP_A, GROUP_B, GROUP_C
    GROUP_A = group_names.group_a
    GROUP_B = group_names.group_b
    GROUP_C = group_names.group_c

    return {
        "group_a": GROUP_A,
        "group_b": GROUP_B,
        "group_c": GROUP_C
    }


@app.post("/api/upload")
async def upload_excel(file: UploadFile = File(...)):
    test_database_path = '../data/ath.db'
    try:
        if not file.filename.endswith('.xlsx'):
            logger.error("上传文件必须为 .xlsx 格式")
            raise HTTPException(status_code=400, detail="仅支持 .xlsx 文件")

        file_path = f"./temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        # excel_to_db(file_path, settings.DATABASE_PATH)
        excel_to_db(file_path, test_database_path)
        os.remove(file_path)
        logger.info("Excel 文件上传并导入成功")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match_tree")
async def generate_match_tree(request: MatchTreeRequest):
    try:
        match_system = KarateMatchSystem(settings.DATABASE_PATH)
        match_tree = match_system.generate_match_tree(request.athletes, request.category)

        # 将比赛树存储到 matches 数据库
        conn = sqlite3.connect(settings.MATCH_DATABASE_PATH)
        cursor = conn.cursor()
        try:
            for match in match_tree:
                cursor.execute(
                    """
                    INSERT INTO matches (category, athlete1_id, athlete2_id, round, result)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (match['category'], match['athletes'][0], match['athletes'][1], match['round'], match['result'])
                )
            conn.commit()
            logger.info(f"比赛树已存储到数据库，包含 {len(match_tree)} 场比赛")
        finally:
            conn.close()

        return {"status": "success", "match_tree": match_tree}
    except Exception as e:
        logger.error(f"生成比赛树失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

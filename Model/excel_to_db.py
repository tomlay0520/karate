import pandas as pd
import sqlite3
import os
import re
import logging
from config.settings import Settings
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def excel_to_db(excel_file_path: str, db_file_path: str) -> None:
    """
    将 Excel 文件中的运动员信息导入数据库
    编写人：汤磊
    更新：2025.7.21 - 删除“身高”列，仅提取体重；修复数据库连接错误
    """
    conn = None  # 避免 finally 中变量未定义

    if not os.path.exists(excel_file_path):
        logger.error(f"❌ Excel 文件 {excel_file_path} 不存在")
        raise FileNotFoundError(f"Excel 文件 {excel_file_path} 不存在")

    try:
        with pd.ExcelFile(excel_file_path) as excel_file:
            if '运动员汇总表' not in excel_file.sheet_names:
                logger.error("❌ 未找到 '运动员汇总表' 工作表")
                raise ValueError("未找到 '运动员汇总表' 工作表")

            df = excel_file.parse('运动员汇总表')

        df.columns = ['单位名称', '姓名', '性别', '身份证', '身高/体重',
                      '组_别_分量制', '组_别_型', '组_别_无差', '备注']
        df = df[3:].reset_index(drop=True)

        # 仅提取体重部分（保留数字部分）
        df['weight'] = df['身高/体重'].astype(str).str.extract(r'/?(\d+\.?\d*)')[0]

        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ath (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_name TEXT,
                ath_name TEXT,
                gender TEXT,
                id_card TEXT UNIQUE,
                weight TEXT,
                weight_category TEXT,
                kata TEXT,
                open TEXT,
                remarks TEXT
            );
        """)

        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ath';")

        for _, row in df.iterrows():
            if pd.isnull(row['姓名']) or row['姓名'] == '':
                logger.warning(f"跳过空姓名记录：{row.to_dict()}")
                continue

            cursor.execute("""
                INSERT OR IGNORE INTO ath (
                    unit_name, ath_name, gender, id_card, weight,
                    weight_category, kata, open, remarks
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                row['单位名称'], row['姓名'], row['性别'], row['身份证'],
                row['weight'], row['组_别_分量制'],
                row['组_别_型'], row['组_别_无差'], row['备注']
            ))

        conn.commit()
        logger.info("✅ 数据成功导入数据库")

    except Exception as e:
        logger.error(f"导入过程中出错: {e}")
        raise
    finally:
        if conn:
            conn.close()


# 测试用例
if __name__ == '__main__':
    settings = Settings()
    test_excel_file_path = '../data/7.27选手名单.xlsx'
    test_db_file_path = settings.DATABASE_PATH

    logger.info(f"准备测试数据库写入: {test_db_file_path}")

    try:
        excel_to_db(test_excel_file_path, test_db_file_path)
        conn = sqlite3.connect(test_db_file_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM ath')
        result = cursor.fetchone()[0]
        conn.close()
        logger.info(f"✅ 数据库中运动员数量：{result}")
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")

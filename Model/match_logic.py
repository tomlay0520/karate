import sqlite3
import re
import random
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KarateMatchSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.group_names = {'甲组': '甲组', '乙组': '乙组', '丙组': '丙组'}

    def update_group_names(self, group_a: str, group_b: str, group_c: str) -> None:
        """更新甲乙丙组的自定义名称"""
        if not all([group_a, group_b, group_c]):
            logger.error("组别名称不能为空")
            raise ValueError("组别名称不能为空")
        self.group_names = {'甲组': group_a, '乙组': group_b, '丙组': group_c}
        logger.info(f"组别名称更新为: 甲组={group_a}, 乙组={group_b}, 丙组={group_c}")

    def _generate_weight_category(self, age: int, gender: Optional[str], weight_input: Optional[str],
                                  weight_flag: Optional[bool], group_type: Optional[str]) -> str:
        """生成分量制比赛分组名称"""
        if not isinstance(age, int) or age < 0:
            logger.error("年龄必须为非负整数")
            raise ValueError("年龄必须为非负整数")

        gender_map = {'male': '男', 'female': '女', '男': '男', '女': '女'}
        if gender and gender not in gender_map:
            logger.error(f"无效性别: {gender}")
            raise ValueError("性别必须为 'male', 'female', '男' 或 '女'")

        if age <= 5:
            category = f"U{age}男女混合"
            if not weight_flag and weight_input:
                category += f"{weight_input}KG"
            else:
                category += "KG"
        else:
            if not group_type or group_type not in self.group_names:
                logger.error(f"无效组别类型: {group_type}")
                raise ValueError("无效的组别类型")
            if not gender:
                logger.error("年龄大于5时必须提供性别")
                raise ValueError("年龄大于5时必须提供性别")
            gender_text = gender_map[gender]
            group_text = self.group_names[group_type]
            category = f"U{age}{gender_text}子{group_text}"
            if not weight_flag and weight_input:
                category += f"{weight_input}KG"
        logger.info(f"生成分量制分组: {category}")
        return category

    def _generate_kata_category(self, age: int, gender: str, group_type: str) -> str:
        """生成型赛分组名称"""
        if not isinstance(age, int) or age < 0:
            logger.error("年龄必须为非负整数")
            raise ValueError("年龄必须为非负整数")
        gender_map = {'male': '男', 'female': '女', '男': '男', '女': '女'}
        if gender not in gender_map:
            logger.error(f"无效性别: {gender}")
            raise ValueError("性别必须为 'male', 'female', '男' 或 '女'")
        if group_type not in self.group_names:
            logger.error(f"无效组别类型: {group_type}")
            raise ValueError("无效的组别类型")

        gender_text = gender_map[gender]
        group_text = self.group_names[group_type]
        category = f"U{age}{group_text}{gender_text}子个人型"
        logger.info(f"生成型赛分组: {category}")
        return category
#以下是核心的查找方法，用于根据前端输入进行模糊查找数据库中满足条件的运动员行
    def get_athletes_by_category(self, category_type: str, competition_type: Optional[str], age: Optional[int],
                                 gender: Optional[str], weight_input: Optional[float],
                                 weight_flag: Optional[bool] = None,
                                 group_type: Optional[str] = None, open_category: Optional[str] = None) -> List[Dict]:
        categories = []

        if category_type == "kumite":
            if competition_type == "open":
                if age is not None and gender is not None:
                    category = self._generate_category(age, gender, open_category=open_category)
                    athletes = self._fuzzy_match_athletes(category,category_type = "open")
                    categories.append({"category": category, "athletes": athletes})
            elif competition_type == "weighted":
                if age is not None and gender is not None and weight_input is not None:
                    category = self._generate_weight_category(age, gender, weight_input, weight_flag=weight_flag,
                                                              group_type=group_type)
                    athletes = self._fuzzy_match_athletes(category,category_type = "weighted")
                    categories.append({"category": category, "athletes": athletes})
            else:
                if age is not None and gender is not None and weight_input is not None:
                    category = self._generate_weight_category(age, gender, weight_input, weight_flag=weight_flag,
                                                              group_type=group_type)
                    athletes = self._fuzzy_match_athletes(category , category_type = "kata")
                    categories.append({"category": category, "athletes": athletes})

        elif category_type == "kata":
            if age is not None and gender is not None:
                category = self._generate_kata_category(age, gender, group_type=group_type)
                athletes = self._fuzzy_match_athletes(category ,category_type = "kata")
                categories.append({"category": category, "athletes": athletes})

        return categories

    #新增的辅助方法，用于智能查找
    def _fuzzy_match_athletes(self, category: str, category_type: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        type_field_map = {
            "weighted": "weight_category",
            "open": "open",
            "kata": "kata"
        }
        field = type_field_map.get(category_type, "weight_category")  # 默认使用 weight_category

        query = f"SELECT * FROM ath WHERE {field} = ?"
        logger.info(f"查找字段: {field}, 分类名: {category}")
        cursor.execute(query, (category,))
        athletes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return athletes

    def create_match_database(self, db_path: str) -> None:
        """创建比赛过程信息数据库"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    athlete1_id INTEGER NOT NULL,
                    athlete2_id INTEGER NOT NULL,
                    round INTEGER NOT NULL,
                    result TEXT,
                    FOREIGN KEY (athlete1_id) REFERENCES ath(id),
                    FOREIGN KEY (athlete2_id) REFERENCES ath(id)
                )
            """)
            conn.commit()
            logger.info(f"比赛数据库创建成功: {db_path}")
        except Exception as e:
            logger.error(f"创建比赛数据库失败: {e}")
            raise
        finally:
            conn.close()

    def generate_match_tree(self, athletes: List[Dict], category: str) -> List[Dict]:
        """生成比赛树状图结构"""
        if not athletes:
            logger.warning("无运动员数据，无法生成比赛树")
            return []

        # 随机打乱选手顺序，模拟种子分配
        random.shuffle(athletes)
        match_tree = []
        current_round = 1
        current_matches = athletes.copy()

        while len(current_matches) > 1:
            next_round = []
            for i in range(0, len(current_matches), 2):
                if i + 1 < len(current_matches):
                    match = {
                        'round': current_round,
                        'match_id': len(match_tree) + 1,
                        'category': category,
                        'athletes': [current_matches[i]['id'], current_matches[i + 1]['id']],
                        'result': None
                    }
                    match_tree.append(match)
                    next_round.append(None)  # 占位，等待比赛结果
                else:
                    # 轮空选手直接晋级
                    next_round.append(current_matches[i])
            current_matches = next_round
            current_round += 1

        logger.info(f"生成比赛树，包含 {len(match_tree)} 场比赛")
        return match_tree
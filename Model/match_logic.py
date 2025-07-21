import sqlite3
import random
import math
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
        if not all([group_a, group_b, group_c]):
            logger.error("组别名称不能为空")
            raise ValueError("组别名称不能为空")
        self.group_names = {'甲组': group_a, '乙组': group_b, '丙组': group_c}
        logger.info(f"组别名称更新为: 甲组={group_a}, 乙组={group_b}, 丙组={group_c}")

    def _generate_weight_category(self, age: int, gender: Optional[str], weight_input: Optional[str],
                                  weight_flag: Optional[bool], group_type: Optional[str]) -> str:
        if not isinstance(age, int) or age < 0 or age > 100:
            logger.error("年龄必须为0-100的整数")
            raise ValueError("年龄必须为0-100的整数")

        gender_map = {'male': '男', 'female': '女', '男': '男', '女': '女'}
        if gender and gender not in gender_map:
            logger.error(f"无效性别: {gender}")
            raise ValueError("性别必须为 'male', 'female', '男' 或 '女'")

        if age <= 5:
            category = f"U{age}男女混合"
            if not weight_flag and weight_input:
                category += f"{weight_input}KG"
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
        if not isinstance(age, int) or age < 0 or age > 100:
            logger.error("年龄必须为0-100的整数")
            raise ValueError("年龄必须为0-100的整数")
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

    def get_athletes_by_category(self, category_type: str, competition_type: Optional[str] = None,
                                 age: Optional[int] = None, gender: Optional[str] = None,
                                 weight_input: Optional[str] = None, weight_flag: Optional[bool] = None,
                                 group_type: Optional[str] = None, open_category: Optional[str] = None) -> List[Dict]:
        if category_type == "kumite":
            if competition_type == "open":
                if not open_category:
                    raise ValueError("无差别比赛需要提供类别")
                athletes = self._fuzzy_match_athletes(open_category, "open")
                return [{"category": open_category, "athletes": athletes}]
            elif competition_type == "weighted":
                if age is None:
                    raise ValueError("分量制比赛需要提供年龄")
                category = self._generate_weight_category(age, gender if age > 5 else None,
                                                         weight_input, weight_flag,
                                                         group_type if age > 5 else None)
                athletes = self._fuzzy_match_athletes(category, "weighted")
                return [{"category": category, "athletes": athletes}]
            else:
                raise ValueError("组手比赛类型必须为 'weighted' 或 'open'")
        elif category_type == "kata":
            if age is None or gender is None or group_type is None:
                raise ValueError("型赛需要提供年龄、性别和组别")
            category = self._generate_kata_category(age, gender, group_type)
            athletes = self._fuzzy_match_athletes(category, "kata")
            return [{"category": category, "athletes": athletes}]
        else:
            raise ValueError("比赛类别必须为 'kumite' 或 'kata'")

    def _fuzzy_match_athletes(self, category: str, category_type: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        type_field_map = {
            "weighted": "weight_category",
            "open": "open",
            "kata": "kata"
        }
        field = type_field_map.get(category_type, "weight_category")

        query = f"SELECT * FROM ath WHERE {field} = ?"
        logger.info(f"查找字段: {field}, 分类名: {category}")
        cursor.execute(query, (category,))
        athletes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return athletes

    def create_match_database(self, db_path: str) -> None:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    athlete1_id INTEGER,
                    athlete2_id INTEGER,
                    round INTEGER NOT NULL,
                    result TEXT,
                    is_bye INTEGER DEFAULT 0,
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
        if not athletes:
            logger.warning("无运动员数据，无法生成比赛树")
            return []

        # 随机打乱选手
        random.shuffle(athletes)
        num_athletes = len(athletes)
        # 计算需要的轮次
        num_rounds = math.ceil(math.log2(num_athletes))
        match_tree = []
        current_round_athletes = athletes.copy()
        round_num = 1

        while len(current_round_athletes) > 1:
            matches_in_round = []
            next_round_athletes = []
            for i in range(0, len(current_round_athletes), 2):
                match = {
                    'round': round_num,
                    'match_id': len(match_tree) + 1,
                    'category': category,
                    'athletes': [None, None],
                    'result': None,
                    'is_bye': 0
                }
                if i + 1 < len(current_round_athletes):
                    # 正常对局
                    match['athletes'] = [current_round_athletes[i]['id'], current_round_athletes[i + 1]['id']]
                else:
                    # 轮空
                    match['athletes'] = [current_round_athletes[i]['id'], None]
                    match['is_bye'] = 1
                    match['result'] = f"Athlete {current_round_athletes[i]['id']} advances (Bye)"
                matches_in_round.append(match)
                next_round_athletes.append(None)  # 占位符，等待比赛结果
            match_tree.extend(matches_in_round)
            current_round_athletes = next_round_athletes
            round_num += 1

        # 如果只有一名选手，直接生成决赛
        if len(athletes) == 1:
            match = {
                'round': 1,
                'match_id': 1,
                'category': category,
                'athletes': [athletes[0]['id'], None],
                'result': f"Athlete {athletes[0]['id']} advances (Bye)",
                'is_bye': 1
            }
            match_tree.append(match)

        logger.info(f"生成单淘汰制比赛树，包含 {len(match_tree)} 场比赛")
        return match_tree
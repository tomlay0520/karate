import sqlite3
import re

class KarateMatchSystem:
    def __init__(self, db_path):
        self.db_path = db_path
        self.group_names = {
            '甲组': '甲组',
            '乙组': '乙组',
            '丙组': '丙组'
        }

    def update_group_names(self, group_a, group_b, group_c):
        """更新甲乙丙组的自定义名称"
        self.group_names = {
            '甲组': group_a,
            '乙组': group_b,
            '丙组': group_c
        }

    def _generate_weight_category(self, age, gender, weight_input, weight_flag, group_type):
        """生成分量制比赛的分组名称"
        if age <= 5:
            category = f"U{age}男女混合"
            if not weight_flag:
                category += f"{weight_input}组"
            else:
                category += "组"
        else:
            gender_text = "男" if gender == "男" else "女"
            group_text = self.group_names[group_type]
            category = f"U{age}{gender_text}子{group_text}"
            if not weight_flag:
                category += f"{weight_input}KG"
        return category

    def _generate_kata_category(self, age, gender, group_type):
        """生成型赛的分组名称"
        gender_text = "男" if gender == "男" else "女"
        group_text = self.group_names[group_type]
        return f"U{age}{group_text}{gender_text}子个人型"

    def get_athletes_by_category(self, category_type, **kwargs):
        """根据比赛类别查询选手
        category_type: 'kumite' 或 'kata'
        kwargs: 包含相应的参数
        ""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if category_type == 'kumite':
                # 组手比赛
                competition_type = kwargs.get('competition_type')
                age = kwargs.get('age')
                gender = kwargs.get('gender') if age >=6 else None
                weight_input = kwargs.get('weight_input')
                weight_flag = kwargs.get('weight_flag')
                group_type = kwargs.get('group_type') if age >=6 else None

                if competition_type == 'weighted':
                    # 分量制比赛
                    category = self._generate_weight_category(age, gender, weight_input, weight_flag, group_type)
                    query = "SELECT * FROM ath WHERE weight_catogory = ?"
                    cursor.execute(query, (category,))
                else:
                    # 无差别比赛
                    open_category = kwargs.get('open_category')
                    query = "SELECT * FROM ath WHERE open = ?"
                    cursor.execute(query, (open_category,))

            elif category_type == 'kata':
                # 型赛
                age = kwargs.get('age')
                gender = kwargs.get('gender')
                group_type = kwargs.get('group_type')
                category = self._generate_kata_category(age, gender, group_type)
                query = "SELECT * FROM ath WHERE kata = ?"
                cursor.execute(query, (category,))

            athletes = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in athletes]

        finally:
            conn.close()

    def create_match_database(self, db_path):
        """创建比赛过程信息数据库"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建比赛表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                athlete1_id INTEGER,
                athlete2_id INTEGER,
                round INTEGER,
                result TEXT,
                FOREIGN KEY (athlete1_id) REFERENCES ath(id),
                FOREIGN KEY (athlete2_id) REFERENCES ath(id)
            )
        """)

        conn.commit()
        conn.close()

    def generate_match_tree(self, athletes, category):
        """生成比赛树状图结构"
        if not athletes:
            return []

        # 简单实现单淘汰赛树
        match_tree = []
        current_round = 1
        current_matches = athletes.copy()

        while len(current_matches) > 1:
            next_round = []
            for i in range(0, len(current_matches), 2):
                if i+1 < len(current_matches):
                    match = {
                        'round': current_round,
                        'match_id': len(match_tree) + 1,
                        'athletes': [current_matches[i]['id'], current_matches[i+1]['id']],
                        'result': None
                    }
                    match_tree.append(match)
                    next_round.append(None)  # 占位，实际比赛后更新胜者
                else:
                    # 轮空选手直接进入下一轮
                    next_round.append(current_matches[i])

            current_matches = next_round
            current_round += 1

        return match_tree
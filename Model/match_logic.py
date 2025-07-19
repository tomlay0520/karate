import sqlite3
import re  # 可选：用于后续字符串处理或正则匹配（当前未使用，但预留）

class KarateMatchSystem:
    def __init__(self, db_path):
        """
        初始化：指定数据库路径，初始化默认的甲乙丙组组名。
        :param db_path: 存储选手信息的 SQLite 数据库路径
        """
        self.db_path = db_path
        self.group_names = {
            '甲组': '甲组',
            '乙组': '乙组',
            '丙组': '丙组'
        }

    def update_group_names(self, group_a, group_b, group_c):
        """
        更新比赛中使用的“甲乙丙组”的自定义名称
        :param group_a: 新的“甲组”名称
        :param group_b: 新的“乙组”名称
        :param group_c: 新的“丙组”名称
        """
        self.group_names = {
            '甲组': group_a,
            '乙组': group_b,
            '丙组': group_c
        }

    def _generate_weight_category(self, age, gender, weight_input, weight_flag, group_type):
        """
        根据年龄、性别、体重输入等参数生成“组手·分量制”项目的分组名称
        """
        if age is None:
            return None
        
        if age <= 5:
            # 5岁以下混合赛
            category = f"U{age}男女混合"
            if not weight_flag and weight_input:
                category += f"{weight_input}组"
            else:
                category += "组"
        else:
            # 6岁及以上分男女、甲乙丙组、体重
            gender_text = "男" if gender == "男" else "女"
            group_text = self.group_names.get(group_type, group_type if group_type else "")
            category = f"U{age}{gender_text}子{group_text}"
            if not weight_flag and weight_input:
                category += f"{weight_input}KG"

        return category

    def _generate_kata_category(self, age, gender, group_type):
        """
        生成型项目的分组名称（U[年龄][甲组名][男/女]子个人型）
        """
        if age is None or not gender or not group_type:
            return None
        gender_text = "男" if gender == "男" else "女"
        group_text = self.group_names.get(group_type, group_type)
        return f"U{age}{group_text}{gender_text}子个人型"

    def get_athletes_by_category(self, category_type, **kwargs):
        """
        查询某个组别下的所有运动员信息。
        :param category_type: 比赛类别（'kumite'组手 或 'kata'型）
        :param kwargs: 额外参数，比如年龄、体重、组别名、性别等
        :return: 运动员信息（字典列表）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if category_type == 'kumite':
                # 处理组手项目
                competition_type = kwargs.get('competition_type')  # 分量制 or 无差别
                age = kwargs.get('age')
                gender = kwargs.get('gender') if age and age >= 6 else None
                weight_input = kwargs.get('weight_input')  # 体重值，字符串（例如 "+25"）
                weight_flag = kwargs.get('weight_flag')  # 是否为无体重限制
                group_type = kwargs.get('group_type') if age and age >= 6 else None

                if competition_type == 'weighted':
                    # 分量制比赛，根据参数拼接分组名
                    category = self._generate_weight_category(age, gender, weight_input, weight_flag, group_type)
                    query = "SELECT * FROM ath WHERE weight_catogory = ?"
                    cursor.execute(query, (category,))
                else:
                    # 无差别赛（用户输入组名）
                    open_category = kwargs.get('open_category')  # 用户在前端输入的组名
                    query = "SELECT * FROM ath WHERE open = ?"
                    cursor.execute(query, (open_category,))

            elif category_type == 'kata':
                # 型赛，使用 age/gender/group_type 拼接分组名
                age = kwargs.get('age')
                gender = kwargs.get('gender')
                group_type = kwargs.get('group_type')
                category = self._generate_kata_category(age, gender, group_type)
                query = "SELECT * FROM ath WHERE kata = ?"
                cursor.execute(query, (category,))

            # 返回结果封装成字典列表
            athletes = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in athletes]

        finally:
            conn.close()

    def create_match_database(self, db_path):
        """
        创建一个新的比赛数据库，用于记录比赛对局过程
        :param db_path: 新的数据库文件路径
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 比赛记录表，每一场对局都存 athlete1, athlete2, round, result 等
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,               -- 比赛组别名称
                athlete1_id INTEGER,         -- 选手1 ID（来自 ath 表）
                athlete2_id INTEGER,         -- 选手2 ID
                round INTEGER,               -- 比赛轮次
                result TEXT,                 -- 胜者ID或比赛结果
                FOREIGN KEY (athlete1_id) REFERENCES ath(id),
                FOREIGN KEY (athlete2_id) REFERENCES ath(id)
            )
        """)

        conn.commit()
        conn.close()

    def generate_match_tree(self, athletes, category):
        """
        为某组比赛生成一个“单淘汰制”的比赛对阵树结构（不含胜负，只是结构）。
        :param athletes: 该组的选手信息（字典列表）
        :param category: 比赛组名
        :return: 比赛对阵树（列表）
        """
        if not athletes:
            return []

        match_tree = []              # 最终比赛树
        current_round = 1            # 当前轮次
        current_matches = athletes.copy()  # 当前轮次选手

        while len(current_matches) > 1:
            next_round = []
            for i in range(0, len(current_matches), 2):
                if i + 1 < len(current_matches):
                    # 正常配对（2个一组）
                    match = {
                        'round': current_round,
                        'match_id': len(match_tree) + 1,
                        'athletes': [current_matches[i]['id'], current_matches[i + 1]['id']],
                        'result': None
                    }
                    match_tree.append(match)
                    next_round.append(None)  # 等待比赛结果来替换
                else:
                    # 奇数个选手时，最后一人轮空晋级
                    next_round.append(current_matches[i])

            current_matches = next_round
            current_round += 1

        return match_tree

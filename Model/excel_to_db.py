import pandas as pd
import sqlite3
import os


def excel_to_db(excel_file_path, db_file_path):
    """
    把 excel 文件里的运动员信息导入到数据库，参数如下
    :param excel_file_path: excel 的路径
    :param db_file_path: 数据库文件的路径
    :return: 无
    编写人：汤磊
    2025.7.18 17:20
    """
    excel_file = pd.ExcelFile(excel_file_path)
    df = excel_file.parse('运动员汇总表')
    df.columns = ['单位名称', '姓名', '性别', '身份证', '身高/体重', '组  别_分量制', '组  别_型', '组  别_无差', '备注']
    df = df[3:]

    df = df.reset_index(drop=True)
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    create_table_query = """
        CREATE TABLE IF NOT EXISTS ath (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_name TEXT,
            ath_name TEXT,
            gender TEXT,
            id_card TEXT UNIQUE,
            weight TEXT,
            weight_catogory TEXT,
            kata TEXT,
            open TEXT,
            remarks TEXT
        );
        """
    cursor.execute(create_table_query)

    # 解决了数据库里序号不从1开始的bug
    reset_sequence_query = "DELETE FROM sqlite_sequence WHERE name='ath';"
    cursor.execute(reset_sequence_query)

    for _, row in df.iterrows():
        if pd.isnull(row['姓名']) or row['姓名'] == '':
            continue

        insert_query = """
                       INSERT 
                       OR IGNORE INTO ath (unit_name, ath_name, gender, id_card, weight, 
                                           weight_category, kata, open, remarks)
            VALUES (?,?,?,?,?,?,?,?,?); 
                       """
        cursor.execute(insert_query, (
            row['单位名称'],
            row['姓名'],
            row['性别'],
            row['身份证'],
            row['身高/体重'],
            row['组  别_分量制'],
            row['组  别_型'],
            row['组  别_无差'],
            row['备注']
        ))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    test_excel_file_path = './7.27选手名单.xlsx'
    test_db_file_path = './ath.db'

    # 测试excel_to_db函数的可用性
    excel_to_db(test_excel_file_path, test_db_file_path)

    try:
        conn = sqlite3.connect(test_db_file_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM ath')
        result = cursor.fetchone()[0]

        conn.close()

        if result > 0:
            print("数据成功导入到数据库。")
        else:
            print("数据未成功导入到数据库。")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
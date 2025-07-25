import pandas as pd
import os
import tempfile
import random


def generate_kata_markdown(input_folder, output_path=None):
    """
    生成型对阵表的 Markdown 文件。

    :param input_folder: 型子表所在文件夹路径
    :param output_path: Markdown 文件保存路径，如果为 None，则使用系统临时目录下的默认路径
    """
    if output_path is None:
        output_path = './subtable/match_kata/match_kata.md'

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"无法创建文件夹 {output_dir}: {e}")
            return

    markdown_content = "# 型对阵表\n\n"
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_excel(file_path, header=0)

                    # 获取选手列表（跳过表头）
                    players = []
                    for _, row in df.iterrows():
                        player_info = f"{row.iloc[0]} {row.iloc[1]}"
                        players.append(player_info)

                    # 随机打乱选手顺序
                    random.shuffle(players)

                    # 处理奇数情况，随机插入轮空
                    if len(players) % 2 != 0:
                        insert_pos = random.randint(0, len(players))
                        players.insert(insert_pos, "轮空")

                    markdown_content += f"## {file.replace('.xlsx', '')} 对阵表\n\n"

                    # 生成对阵表
                    for i in range(0, len(players), 2):
                        if i + 1 < len(players):
                            markdown_content += f"- {players[i]} vs {players[i + 1]}\n"
                        else:
                            markdown_content += f"- {players[i]} vs 轮空\n"
                    markdown_content += "\n"

                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")
                    continue

    try:
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print(f"型对阵表 Markdown 文件已成功保存到 {output_path}")
    except PermissionError:
        print(f"权限不足，无法写入文件 {output_path}")


if __name__ == '__main__':
    kata_input_folder = './subtable/按分量制拆分的子表/型'
    generate_kata_markdown(kata_input_folder)
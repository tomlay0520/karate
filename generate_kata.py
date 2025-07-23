import pandas as pd
import os
import tempfile


def generate_kumite_markdown(input_folder, output_path=None):
    """
    生成组手对阵表的 Markdown 文件。

    :param input_folder: 组手子表所在文件夹路径
    :param output_path: Markdown 文件保存路径，如果为 None，则使用系统临时目录下的默认路径
    """
    if output_path is None:
        # 使用系统临时目录生成一个默认文件名
        # output_path = os.path.join(tempfile.gettempdir(), "match_kata.md")
        output_path = './subtable/match_kata/match_kata.md'

    # 确保输出路径的目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"无法创建文件夹 {output_dir}: {e}")
            return

    markdown_content = ""
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.xlsx'):
                excel_file = pd.ExcelFile(os.path.join(root, file))
                df = excel_file.parse()
                # 拼接第一列和第二列字段信息
                combined_column = df.iloc[:, 0].astype(str) + ' ' + df.iloc[:, 1].astype(str)
                markdown_content += f"### {file.replace('.xlsx', '')} 对阵表\n\n"
                for i in range(1, len(combined_column), 2):
                    if i + 1 < len(combined_column):
                        markdown_content += f"{combined_column[i]} vs {combined_column[i + 1]}\n\n"
                    else:
                        markdown_content += f"{combined_column[i]} vs 轮空\n\n"

    # 保存 Markdown 文件
    try:
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print(f"组手 Markdown 文件已成功保存到 {output_path}")
    except PermissionError:
        print(f"权限不足，无法写入组手文件 {output_path}")


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

    markdown_content = ""
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.xlsx'):
                excel_file = pd.ExcelFile(os.path.join(root, file))
                df = excel_file.parse()
                # 拼接第一列和第二列字段信息
                combined_column = df.iloc[:, 0].astype(str) + ' ' + df.iloc[:, 1].astype(str)
                markdown_content += f"### {file.replace('.xlsx', '')} 型对阵表\n\n"
                for i in range(1, len(combined_column), 2):
                    if i + 1 < len(combined_column):
                        markdown_content += f"{combined_column[i]} vs {combined_column[i + 1]}\n\n"
                    else:
                        markdown_content += f"{combined_column[i]} vs 轮空\n\n"

    try:
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        print(f"型 Markdown 文件已成功保存到 {output_path}")
    except PermissionError:
        print(f"权限不足，无法写入型文件 {output_path}")


if __name__ == '__main__':
    kata_input_folder = './subtable/按分量制拆分的子表/型'
    generate_kata_markdown(kata_input_folder)
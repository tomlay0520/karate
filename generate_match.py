import pandas as pd
import os


def generate_kumite_markdown(input_folder, output_path):
    """
    生成组手对阵表的 Markdown 文件。

    :param input_folder: 组手子表所在文件夹路径
    :param output_path: Markdown 文件保存路径
    """
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
    with open(output_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_content)


if __name__ == '__main__':
    # 组手子表所在文件夹路径，需要根据实际情况修改
    input_folder = './subtable/按分量制拆分的子表/组手'
    # Markdown 文件保存路径，需要根据实际情况修改
    output_path = './subtable/match_kumite'
    generate_kumite_markdown(input_folder, output_path)
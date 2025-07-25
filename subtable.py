# import pandas as pd
# import os
#
# # 选手的名单
# file_path = './data/选手名单7.27(最终版）.xlsx'
#
# # 重读数据，设置表头行为1
# data = pd.ExcelFile(file_path).parse('Sheet1', header=1)
#
# # 按分量制列进行分组
# grouped_weight = data.groupby('分量制')
# # 按型列进行分组
# grouped_type = data.groupby('型')
#
# # 指定保存路径
# output_path = './subtable/按分量制拆分的子表'
# if not os.path.exists(output_path):
#     os.makedirs(output_path)
#
# # 确保组手和型文件夹存在
# kumite_folder = os.path.join(output_path, '组手')
# kata_folder = os.path.join(output_path, '型')
# os.makedirs(kumite_folder, exist_ok=True)
# os.makedirs(kata_folder, exist_ok=True)
#
# # 遍历每个按分量制的组并保存到组手文件夹
# for group_name, group_data in grouped_weight:
#     file_name = f'{group_name}.xlsx'
#     file_path = os.path.join(kumite_folder, file_name)
#     group_data.to_excel(file_path, index=False)
#
# # 遍历每个按型的组并保存到型文件夹
# for group_name, group_data in grouped_type:
#     file_name = f'{group_name}.xlsx'
#     file_path = os.path.join(kata_folder, file_name)
#     group_data.to_excel(file_path, index=False)

import pandas as pd
import os


def split_excel_data():
    # 选手的名单 Excel 文件路径，这里需要根据实际文件路径修改
    file_path = './data/选手名单7.27(最终版）.xlsx'

    # 重读数据，设置表头行为 1
    data = pd.ExcelFile(file_path).parse('Sheet1', header=1)

    # 按分量制列进行分组
    grouped_weight = data.groupby('分量制')
    # 按型列进行分组
    grouped_type = data.groupby('型')

    # 指定保存路径，这里也需要根据实际想要保存的路径修改
    output_path = './subtable/按分量制拆分的子表'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # 确保组手和型文件夹存在
    kumite_folder = os.path.join(output_path, '组手')
    kata_folder = os.path.join(output_path, '型')
    os.makedirs(kumite_folder, exist_ok=True)
    os.makedirs(kata_folder, exist_ok=True)

    # 遍历每个按分量制的组并保存到组手文件夹
    for group_name, group_data in grouped_weight:
        file_name = f'{group_name}.xlsx'
        file_path = os.path.join(kumite_folder, file_name)
        group_data.to_excel(file_path, index=False)

    # 遍历每个按型的组并保存到型文件夹，确保遵循命名规则
    for group_name, group_data in grouped_type:
        if pd.notna(group_name):
            file_name = f'{group_name}.xlsx'
        else:
            file_name = '未分类型.xlsx'
        file_path = os.path.join(kata_folder, file_name)
        group_data.to_excel(file_path, index=False)


if __name__ == '__main__':
    split_excel_data()
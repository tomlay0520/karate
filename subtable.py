import pandas as pd
import os

# 选手的名单
file_path = './data/7.27选手名单.xlsx'

data = pd.ExcelFile(file_path).parse('运动员汇总表')

# 按分量制列进行分组
grouped = data.groupby('分量制')

# 指定保存路径
output_path = './subtable/按分量制拆分的子表'
if not os.path.exists(output_path):
    os.makedirs(output_path)

# 遍历每个组并保存为独立的 Excel 文件
for group_name, group_data in grouped:
    file_name = f'{group_name}.xlsx'
    file_path = os.path.join(output_path, file_name)
    group_data.to_excel(file_path, index=False)
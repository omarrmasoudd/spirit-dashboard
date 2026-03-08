import pandas as pd

file_path = "Spirit_Project_Template_CORRECT.xlsx"

xls = pd.ExcelFile(file_path)

print(xls.sheet_names)
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Cases"

ws.append([
    "ID",
    "Category",
    "Title",
])

rows = [
    ["QAQC_001","QAQC","Quá nhiệt gây cong vênh cấu kiện"],
    ["QAQC_002","QAQC","Sai kích thước sau hàn"],
    ["QAQC_003","QAQC","Sai kích thước lắp ráp"],
    ["MT_001","Maintenance","Động cơ quá nhiệt"],
    ["MT_002","Maintenance","Ổ bi hỏng"],
    ["WELD_001","Welding","Rỗ khí mối hàn"],
]

for r in rows:
    ws.append(r)

wb.save("planner/STEEL_CASE_REGISTER.xlsx")

print("PASS")

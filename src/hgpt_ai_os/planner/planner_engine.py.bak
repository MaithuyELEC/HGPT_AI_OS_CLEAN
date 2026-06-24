from openpyxl import load_workbook
from pathlib import Path


class PlannerEngine:

    def __init__(self, planner="planner/HGPT_MASTER_PLANNER.xlsx"):
        self.planner = Path(planner)

    def workbook(self):
        return load_workbook(self.planner)

    def marketing(self):
        wb = self.workbook()
        return wb["MarketingPlan"]

    def next_task(self):
        ws = self.marketing()

        for row in ws.iter_rows(min_row=2):
            if str(row[4].value).upper() == "TODO":
                return {
                    "row": row[0].row,
                    "id": row[0].value,
                    "day": row[1].value,
                    "topic": row[2].value,
                    "platform": row[3].value,
                    "status": row[4].value,
                    "folder": row[5].value,
                    "priority": row[6].value,
                }

        return None

    def update_status(self, row, status):
        wb = self.workbook()
        ws = wb["MarketingPlan"]
        ws.cell(row=row, column=5).value = status
        wb.save(self.planner)

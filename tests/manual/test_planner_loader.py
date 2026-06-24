from hgpt_ai_os.planner import PlannerLoader

loader = PlannerLoader(
    "planner/HGPT_MASTER_PLANNER.xlsx"
)

rows = loader.load()

print(f"Rows: {len(rows)}")

if rows:
    print(rows[0])

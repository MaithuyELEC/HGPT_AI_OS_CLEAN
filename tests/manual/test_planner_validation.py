from hgpt_ai_os.planner import PlannerLoader
from hgpt_ai_os.planner import PlannerValidator

loader = PlannerLoader(
    "planner/HGPT_MASTER_PLANNER.xlsx"
)

rows = loader.load()

validator = PlannerValidator()

result = validator.validate_rows(rows)

print("VALID:", result.ok)

if result.errors:
    print("\nERRORS")
    for e in result.errors:
        print("-", e)

if result.warnings:
    print("\nWARNINGS")
    for w in result.warnings:
        print("-", w)

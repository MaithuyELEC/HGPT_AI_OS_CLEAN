from dataclasses import dataclass
from typing import List, Dict, Any


REQUIRED_COLUMNS = [
    "ID",
    "Day",
    "Platform",
    "Status",
    "Output Folder",
]

VALID_STATUS = {
    "TODO",
    "RUNNING",
    "GENERATED",
    "DONE",
    "APPROVED",
    "REJECTED",
}

VALID_PLATFORMS = {
    "Facebook",
    "TikTok",
    "Image",
    "Video",
    "SEO",
    "Hashtags",
    "Approval",
    "LinkedIn",
    "YouTube",
    "Blog",
}


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str]
    warnings: List[str]


class PlannerValidator:

    def validate_headers(self, headers: List[str]) -> List[str]:
        errors = []

        missing = [
            c for c in REQUIRED_COLUMNS
            if c not in headers
        ]

        if missing:
            errors.append(
                f"Missing required columns: {missing}"
            )

        return errors

    def validate_rows(
        self,
        rows: List[Dict[str, Any]]
    ) -> ValidationResult:

        errors = []
        warnings = []

        seen_ids = set()

        for idx, row in enumerate(rows, start=2):

            task_id = row.get("ID")
            day = row.get("Day")
            platform = row.get("Platform")
            status = row.get("Status")

            if task_id in seen_ids:
                errors.append(
                    f"Row {idx}: duplicated ID '{task_id}'"
                )

            seen_ids.add(task_id)

            if task_id in (None, ""):
                errors.append(
                    f"Row {idx}: ID is empty"
                )

            if not isinstance(day, int):
                errors.append(
                    f"Row {idx}: Day must be integer"
                )

            platforms = [
                p.strip()
                for p in str(platform).split(",")
                if p.strip()
            ]

            invalid = [
                p for p in platforms
                if p not in VALID_PLATFORMS
            ]

            if invalid:
                errors.append(
                    f"Row {idx}: invalid Platform {invalid}"
                )

            if status not in VALID_STATUS:
                errors.append(
                    f"Row {idx}: invalid Status '{status}'"
                )

        return ValidationResult(
            ok=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

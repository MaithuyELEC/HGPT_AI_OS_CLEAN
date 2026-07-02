from pathlib import Path

from hgpt_ai_os.version import APP_VERSION

ROOT_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = ROOT_DIR / "database" / "hgpt_ai_os.db"

APP_NAME = "HGPT AI OS"
VERSION = APP_VERSION

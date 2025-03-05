from .env import load_environment

load_environment()

from .config import (
    SHEETS_DIR,
    SHOPER_LIMIT,
    SITE,
    CREDENTIALS_FILE,
    SHEET_EXPORT_NAME,
    SHEET_IMPORT_NAME,
    SHEET_IMPORT_NAME_PERCENT,
    SHEET_ID,
    init_directories
)

init_directories()
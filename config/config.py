import os
from pathlib import Path

# Shoper site - can be either TEST (development) or MAIN (deployment)
SITE = 'TEST'

# LIMIT for API requests
SHOPER_LIMIT = 50

# Google Sheets
SHEET_EXPORT_NAME = 'Eksport'
SHEET_IMPORT_NAME = 'Do importu'
CREDENTIALS_FILE = os.path.join('credentials', 'gsheets_credentials.json')
SHEET_ID = os.getenv('SHEET_ID')

ROOT_DIR = Path(__file__).parent.parent
SHEETS_DIR = ROOT_DIR / 'sheets'

def init_directories():
    """Initialize required directories if they don't exist"""
    try:
        SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError(f"Unable to create directory at {SHEETS_DIR}. Check permissions.")
    except Exception as e:
        raise Exception(f"Error creating directory structure: {str(e)}")
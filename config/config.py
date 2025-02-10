import os

# Shoper site - can be either TEST (development) or MAIN (deployment)
SITE = 'MAIN'

# LIMIT for API requests
SHOPER_LIMIT = 50

# Google Sheets
SHEET_ID = os.getenv('SHEET_ID')
SHEET_EXPORT_NAME = 'Eksport'
SHEET_IMPORT_NAME = 'Do importu'

from config import load_environment
from config.config import SITE, CREDENTIALS_FILE, SHEET_EXPORT_NAME, SHEET_IMPORT_NAME, SHEET_ID
from connections import ShoperAPIClient, GSheetsClient
import os
import pandas as pd

def main():

    shoper_client = ShoperAPIClient(
        site_url=os.getenv(f'SHOPERSITE_{SITE}'),
        login=os.getenv(f'LOGIN_{SITE}'),
        password=os.getenv(f'PASSWORD_{SITE}')
    )
    
    export_gsheets_client = GSheetsClient(
        credentials=CREDENTIALS_FILE,
        sheet_id=SHEET_ID,
        sheet_name=SHEET_EXPORT_NAME
    )

    import_gsheets_client = GSheetsClient(
        credentials=CREDENTIALS_FILE,
        sheet_id=SHEET_ID,
        sheet_name=SHEET_IMPORT_NAME
    )

    shoper_client.connect()
    export_gsheets_client.connect()

    df = pd.DataFrame(shoper_client.get_all_products_and_select_special_offers())
    export_gsheets_client.save_data(df)


if __name__ == "__main__":
    main()

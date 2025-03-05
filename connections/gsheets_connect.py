import gspread
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from config import SHEETS_DIR

class GSheetsClient:

    def __init__(self, credentials, sheet_id, sheet_name):
        """
        Initialize the GSheetsClient with credentials and sheet ID.
        Args:
            credentials (str): Path to the service account JSON credentials file.
            sheet_id (str): Name of the environment variable storing the sheet ID.
            sheet_name (str): Name of the specific sheet.
        """

        self.credentials_path = credentials
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.gc = None
        self.sheet = None
        self.worksheet = None

    def connect(self):
        """Authenticate with Google Sheets."""
        try:
            self.gc = gspread.service_account(filename=self.credentials_path)
            self.sheet = self.gc.open_by_key(self.sheet_id)
            self.worksheet = self.sheet.worksheet(self.sheet_name)
            print("Google Authentication successful.")
        except Exception as e:
            print(f"Failed to connect to Google Sheets: {str(e)}")
            raise

    def get_data(self, include_row_numbers=False):
        """Get data from a Google Sheets worksheet as a pandas DataFrame."""
        if not self.sheet:
            raise Exception("Not connected to Google Sheets. Call connect() first.")

        worksheet = self.sheet.worksheet(self.sheet_name)
        data = worksheet.get_all_values()
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data[1:], columns=data[0])  # First row as header
        df.to_excel(os.path.join(SHEETS_DIR, 'google_sheets_all.xlsx'), index=False)
        df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0] != '')]
        df = df[~df['komunikat'].str.contains('Promocja dodana', na=False)]
        
        if include_row_numbers:
            df.insert(0, 'Row Number', range(2, len(df) + 2)) # GSheets rows start at 2

        return df
    
    def save_data(self, df):
        """
        Save DataFrame to Google Sheets.
        """
        try:
            # Convert DataFrame to string values where necessary
            all_values = self.transform_data(df)
            
            print('Cleaning the worksheet...')
            # Clear existing content
            self.worksheet.clear()
            print('Updating the worksheet')
            # Update with new values
            self.worksheet.update(all_values)
            print(f"Successfully updated worksheet: {self.sheet_name}")
            
        except Exception as e:
            print(f"Error saving to Google Sheets: {str(e)}")
            raise

    def transform_data(self, df):
        """
        Transform DataFrame to match Google Sheets format.
        """
        df_string = df.astype(str)
        header = df_string.columns.values.tolist()
        data = df_string.values.tolist()
        
        return [header] + data
    
    def batch_update_by_code(self, update_df):
        """
        Updates multiple rows in the worksheet by matching the 'code' column.
        
        Args:
            update_df (pd.DataFrame): DataFrame containing updates with 'code' column
        """
        if update_df is None or update_df.empty:
            print("No data provided for update")
            return
        
        try:
            # Get all data without filtering
            worksheet_data = self.worksheet.get_all_values()
            headers = worksheet_data[0]
            
            # Find column indices
            try:
                code_col_idx = headers.index('code') + 1  # 1-based column indexing
                komunikat_col_idx = headers.index('komunikat') + 1
            except ValueError:
                raise ValueError("Required columns 'code' or 'komunikat' not found in worksheet")
            
            # Create code to row mapping (2-based row indexing for header)
            code_to_row = {str(row[code_col_idx-1]): idx + 2 
                          for idx, row in enumerate(worksheet_data[1:])}
            
            batch_updates = []
            
            for _, row in update_df.iterrows():
                code = str(row['code'])
                if code in code_to_row:
                    row_num = code_to_row[code]
                    col_letter = chr(64 + komunikat_col_idx)  # Convert column number to letter
                    
                    batch_updates.append({
                        'range': f'{col_letter}{row_num}',
                        'values': [[row['komunikat']]]
                    })
            
            if batch_updates:
                self.worksheet.batch_update(batch_updates)
                print(f"Successfully updated {len(batch_updates)} cells")
            else:
                print("No matching codes found to update")
            
        except Exception as e:
            print(f"Error in batch update: {str(e)}")
            raise
    
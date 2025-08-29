import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import time
from datetime import datetime

db_info = dict(st.secrets.db_info)


class SheetLogger:
    """
    A class to handle logging of spendings and income into Google Sheets.
    """

    def __init__(self, credentials_path:str=None, sheet_id:str=None):
        """
        Initialize the SheetLogger with credentials and sheet ID.

        Args:
            credentials_path (str): Path to the credentials JSON file.
            sheet_id (str): The ID of the Google Sheet.
        """
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        google_api = dict(st.secrets.google_api)
        creds = Credentials.from_service_account_info(google_api, scopes=scopes)
        client = gspread.authorize(creds)
        if sheet_id is None:
            sheet_id = db_info["sheet_id"]
        self.sheet = client.open_by_key(sheet_id)
        self.spendings_sheet = self.sheet.get_worksheet(0)
        self.income_sheet = self.sheet.get_worksheet(1)
        self.cached_spendings = None
        self.cached_income = None

    def safe_api_call(self, func, *args, **kwargs):
        """
        Safely call a Google Sheets API function with retry logic.

        Args:
            func (callable): The API function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the API call.

        Raises:
            Exception: If the API call fails after retries.
        """
        retries = 3
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                if "Quota exceeded" in str(e) and attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    def fetch_spendings(self, conver_date:bool=False) -> list:
        """
        Fetch spendings data from the Google Sheet.

        Returns:
            list: List of spendings records.
        """
        data = self.safe_api_call(self.spendings_sheet.get_all_records)
        if conver_date:
            for i in data:
                i["Date"] = datetime.strptime(i["Date"], '%Y-%m-%d')
        return data

    def fetch_income(self, convert_date:bool=False) -> list:
        """
        Fetch income data from the Google Sheet.

        Returns:
            list: List of income records.
        """
        data = self.safe_api_call(self.income_sheet.get_all_records)
        if convert_date:
            for i in data:
                i["Date"] = datetime.strptime(i["Date"], '%Y-%m-%d')
        return data

    def log_spending(self, data: list[float, str, str, str], date_conversion:bool=False) -> None:
        """
        Log a spending entry into the spendings sheet.

        Args:
            data (list):
                - amount (float): The amount of spending.
                - date (str): The date of spending in the format DD/MM/YYYY.
                - type (str): The type of spending.
                - comments (str): Additional comments or notes.
        """
        if date_conversion:
            data[1] = str(data[1])
        num = len(self.fetch_spendings())+1
        data = [num] + data
        self.spendings_sheet.append_row(data)
        self.cached_spendings = None  # Invalidate cache

    def log_income(self, data: list[float, str, str, str], date_conversion:bool=False) -> None:
        """
        Log an income entry into the income sheet.

        Args:
            data (list):
                - amount (float): The amount of income.
                - date (str): The date of income in the format DD/MM/YYYY.
                - type (str): The type of income.
                - comments (str): Additional comments or notes.
        """
        if date_conversion:
            data[1] = str(data[1])
        num = len(self.fetch_income())+1
        data = [num] + data
        self.income_sheet.append_row(data)
        self.cached_income = None  # Invalidate cache
    
    def update_spenings_sheet(self, changes:list[list[int, int, str]]) -> bool:
        """
            Update the spendings sheet with the provided changes.
            Args:
            data (list):
                objects (list):
                    - row (int): Row of the data
                    - column (int): Column of the data
                    - value (str): Value
        """
        for i in changes:
            self.spendings_sheet.update_cell(i[0], i[1], i[2])
        return True
    
    def update_income_sheet(self, changes:list[list[int, int, str]]) -> bool:
        """
            Update the income sheet with the provided changes.
            Args:
            data (list):
                objects (list):
                    - row (int): Row of the data   
                    - column (int): Column of the data
                    - value (str): Value
        """
        for i in changes:
            self.income_sheet.update_cell(i[0], i[1], i[2])
        return True
    def clear_spending_sheet(self) -> None:
        """
        Clear the spendings sheet except for the first row.
        """
        rows_to_clear = len(self.fetch_spendings())
        if rows_to_clear > 0:
            self.spendings_sheet.delete_rows(2, rows_to_clear + 1)
    def clear_income_sheet(self) -> None:
        """
        Clear the income sheet except for the first row.
        """
        rows_to_clear = len(self.fetch_income())
        if rows_to_clear > 0:
            self.income_sheet.delete_rows(2, rows_to_clear + 1)


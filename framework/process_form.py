#Form processing machanism
from framework import forex_conversion, sheet

def currency_conversion(value:float, original_currency:str, final_currency:str='USD') -> float:
    if original_currency == final_currency:
        return value
    else:
        return forex_conversion.convert_currency(value, original_currency, final_currency)

#data meaning [int:(0 for income, 1 for spendings)]
def process_form(data: list[str, float, str, str, str, str], logger:sheet.SheetLogger) -> bool:
    """
    Process a form submission.

    Args:
        data (list):
            - type (str): Either 'spendings' or 'income'.
            - amount (float): The monetary amount.
            - currency (str): Three-letter currency code (e.g., 'USD').
            - date (str): Date in the format DD/MM/YYYY.
            - type (str): The type of transaction.
            - comment (str): Additional comments or notes.

    Returns:
        bool: True if the form is processed successfully, False otherwise.
    """
    amount = currency_conversion(data[1], data[2])
    date, transaction_type, comments = data[3], data[4], data[5]
    if data[0] == 'spendings':
        logger.log_spending([amount, date, transaction_type, comments], True)
    elif data[0] == 'income':
        logger.log_income([amount, date, transaction_type, comments], True)
    return True
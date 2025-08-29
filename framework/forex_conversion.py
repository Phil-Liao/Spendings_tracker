import requests
import streamlit as st

def convert_currency(amount, original_currency, to_currency, api_key=None):
    """
    Convert an amount from one currency to another using the Exchangerates API.

    :param amount: The amount to convert.
    :param from_currency: The currency code to convert from (e.g., 'USD').
    :param to_currency: The currency code to convert to (e.g., 'EUR').
    :param api_key: Your API key for the Exchangerates API.
    :return: The converted amount.
    """
    if api_key is None:
        api_key = st.secrets.forex_api.api_key
    url = f"https://api.exchangeratesapi.io/v1/latest?access_key={api_key}&symbols={original_currency},{to_currency}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise ValueError(f"API error: {data['error']['info']}")

        rates = data['rates']
        from_rate = rates.get(original_currency)
        to_rate = rates.get(to_currency)

        if from_rate is None or to_rate is None:
            raise ValueError(f"Conversion rate for {original_currency} or {to_currency} not found.")

        # Convert using the rates relative to the base currency
        converted_amount = (amount / from_rate) * to_rate
        return converted_amount

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to the Exchangerates API: {e}")
    except ValueError as e:
        raise ValueError(f"Error in currency conversion: {e}")
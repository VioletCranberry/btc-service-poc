import logging
from typing import List

import yfinance as yf
from database.db import Database
from database.models import BitcoinPrice


def get_current_price(ticker: str, currency: str) -> float:
    """
    Retrieves the current price of ticker in the specified currency.
    """
    logging.info(f"Fetching ticker {ticker} data for {currency} currency")
    btc = yf.Ticker(ticker)
    price_usd = btc.history(period="1d")["Close"].iloc[-1]

    if currency == "EUR":
        # EUR conversion
        eur_usd = yf.Ticker("EURUSD=X")
        rate = eur_usd.history(period="1d")["Close"].iloc[-1]
        return price_usd * rate
    elif currency == "CZK":
        # CZK conversion
        czk_usd = yf.Ticker("CZKUSD=X")
        rate = czk_usd.history(period="1d")["Close"].iloc[-1]
        return price_usd * rate
    else:
        raise ValueError(
            f"Unsupported ticket/currency pair {ticker}/{currency}"
        )


def store_prices(
    db_dir: str, db_name: str, ticker: str, currencies: List[str]
) -> None:
    """
    Stores the current Bitcoin prices in EUR and CZK to the database.
    """
    logging.info(
        f"Storing database data for ticker {ticker} / currencies {currencies}"
    )
    db_instance = Database(db_dir, db_name)
    db = next(db_instance.get_db())
    for currency in currencies:
        try:
            price = get_current_price(ticker, currency=currency)
            logging.info(f"Current {ticker} price in {currency}: {price}")
            new_price = BitcoinPrice(price=price, currency=currency)
            db.add(new_price)
            db.commit()
        except ValueError as e:
            logging.error(f"Failed to store data: {e}")

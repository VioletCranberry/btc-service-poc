import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from database.models import BitcoinPrice
from fastapi import HTTPException
from schemas.prices import AveragePriceDetail, PriceDetail
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_latest_prices(
    db: Session, currencies: List[str], client_time: str
) -> Dict[str, PriceDetail]:
    """
    Retrieves the latest prices for the specified currencies from the database.
    """
    logging.info(
        f"Getting latest prices for currencies {currencies} from the database..."
    )
    prices = {}

    for currency in currencies:
        price_record = (
            db.query(BitcoinPrice)
            .filter(BitcoinPrice.currency == currency)
            .order_by(BitcoinPrice.date.desc())
            .first()
        )
        if price_record:
            data_time = price_record.date.isoformat()
            prices[currency] = PriceDetail(
                price=price_record.price,
                currency=currency,
                request_time=client_time,
                server_data_time=data_time,
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No price data available for {currency}",
            )

    return prices


def get_averages(
    db: Session, currencies: List[str]
) -> Dict[str, AveragePriceDetail]:
    """
    Retrieves the daily and monthly average prices for the specified currencies from the database.
    """
    logging.info(
        f"Getting average prices for currencies {currencies} from the database..."
    )
    averages = {}

    for currency in currencies:

        # Calculate daily average
        today = datetime.now(timezone.utc).date()
        daily_start = datetime.combine(today, datetime.min.time())
        daily_end = daily_start + timedelta(days=1)
        daily_avg = (
            db.query(func.avg(BitcoinPrice.price))
            .filter(BitcoinPrice.currency == currency)
            .filter(BitcoinPrice.date >= daily_start)
            .filter(BitcoinPrice.date < daily_end)
            .scalar()
        )

        # Calculate monthly average
        first_day_of_month = today.replace(day=1)
        monthly_avg = (
            db.query(func.avg(BitcoinPrice.price))
            .filter(BitcoinPrice.currency == currency)
            .filter(BitcoinPrice.date >= first_day_of_month)
            .filter(BitcoinPrice.date < daily_start)
            .scalar()
        )

        if daily_avg is None and monthly_avg is None:
            raise HTTPException(
                status_code=404,
                detail=f"No price data available for {currency}",
            )

        averages[currency] = AveragePriceDetail(
            daily_average=daily_avg if daily_avg is not None else None,
            monthly_average=monthly_avg if monthly_avg is not None else None,
        )

    return averages

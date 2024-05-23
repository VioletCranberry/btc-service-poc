from database.db import Base
from sqlalchemy import Column, DateTime, Float, Integer, String, func


class BitcoinPrice(Base):
    """
    Bitcoin prices table in different currencies along with the timestamp.
    """

    __tablename__ = "bitcoin_prices"

    id: Column = Column(Integer, primary_key=True, index=True)
    price: Column = Column(Float, nullable=False)
    currency: Column = Column(String, nullable=False)
    date: Column = Column(DateTime, default=func.now(), nullable=False)

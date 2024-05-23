from typing import Dict, Optional

from pydantic import BaseModel


class PriceDetail(BaseModel):
    """
    Model to represent detailed information about a specific price.

    Attributes:
        price (float): The price of Bitcoin in the specified currency.
        currency (str): The currency code (e.g., 'EUR', 'CZK').
        request_time (str): The time the client made the request.
        server_data_time (str): The time the price data was recorded on the server.
    """

    price: float
    currency: str
    request_time: str
    server_data_time: str


class CurrentPricesResponse(BaseModel):
    """
    Model to represent the response containing the latest prices for multiple currencies.

    Attributes:
        prices (Dict[str, PriceDetail]): A dictionary where the keys are currency codes
                                         and the values are PriceDetail objects containing
                                         the latest price information for each currency.
    """

    prices: Dict[str, PriceDetail]


class AveragePriceDetail(BaseModel):
    """
    Model to represent average price details for a specific currency.

    Attributes:
        daily_average (Optional[float]): The daily average price of Bitcoin in the specified currency.
                                         This can be None if no data is available.
        monthly_average (Optional[float]): The monthly average price of Bitcoin in the specified currency.
                                           This can be None if no data is available.
    """

    daily_average: Optional[float]
    monthly_average: Optional[float]


class AveragesResponse(BaseModel):
    """
    Model to represent the response containing the average prices for multiple currencies.

    Attributes:
        averages (Dict[str, AveragePriceDetail]): A dictionary where the keys are currency codes
                                                  and the values are AveragePriceDetail objects
                                                  containing the average price information for each currency.
    """

    averages: Dict[str, AveragePriceDetail]

from datetime import datetime
from typing import List

from database.db import Database
from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.prices import AveragesResponse, CurrentPricesResponse
from sqlalchemy.orm import Session

from .db_utils import get_averages, get_latest_prices


def prices_router(
    db_instance: Database, currencies: List[str], api_key: str
) -> APIRouter:
    """
    Creates a router for handling price-related endpoints with authentication and database dependencies.

    Args:
        db_instance (Database): The database instance.
        currencies (List[str]): List of currency codes to handle.
        api_key (str): The API key for request authentication.

    Returns:
        APIRouter: The configured FastAPI router.
    """
    router = APIRouter()

    def get_db():
        """
        Provides a database session for dependency injection.
        """
        db = next(db_instance.get_db())
        try:
            yield db
        finally:
            db.close()

    def authenticate(request: Request):
        """
        Authenticates requests using the provided API key.
        """
        request_api_key = request.headers.get("api-key")
        if request_api_key != api_key:
            raise HTTPException(status_code=403, detail="Invalid API Key")

    @router.get(
        "/prices/current",
        tags=["prices"],
        response_model=CurrentPricesResponse,
        responses={
            200: {"description": "Successful Response"},
            403: {"description": "Invalid API Key"},
            404: {
                "description": "No price data available for the requested currency"
            },
        },
        description="Endpoint to get the current prices for specified currencies.",
    )
    def current_prices(
        request: Request,
        db: Session = Depends(get_db),
        _: None = Depends(authenticate),
    ) -> CurrentPricesResponse:
        """
        Endpoint to get the current prices for specified currencies.
        """
        client_time = datetime.now().isoformat()
        prices = get_latest_prices(db, currencies, client_time)
        return CurrentPricesResponse(prices=prices)

    @router.get(
        "/prices/averages",
        tags=["prices"],
        response_model=AveragesResponse,
        responses={
            200: {"description": "Successful Response"},
            403: {"description": "Invalid API Key"},
            404: {
                "description": "No price data available for the requested currency"
            },
        },
        description="Endpoint to get the daily and monthly average prices for specified currencies.",
    )
    def average_prices(
        request: Request,
        db: Session = Depends(get_db),
        _: None = Depends(authenticate),
    ) -> AveragesResponse:
        """
        Endpoint to get the daily and monthly average prices for specified currencies.
        """
        averages = get_averages(db, currencies)
        return AveragesResponse(averages=averages)

    return router

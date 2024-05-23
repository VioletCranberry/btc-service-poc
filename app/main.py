import argparse
import logging
import os
import signal
import sys
from typing import Any, Dict

import uvicorn
from database.db import Database
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import APIKeyHeader
from routers.health import health_router
from routers.prices import prices_router
from services.scheduler import init_services, shutdown_services

# requirement, allowing users to test endpoints with the "try it out"
# feature by providing the API key.

# TODO: Add validation for the API key. Without proper validation, any
# key would be considered authenticated in the UI, even if it is not
# valid. Note that all endpoints currently work as expected.

API_KEY_NAME = "api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Initialize FastAPI application
app = FastAPI()


def custom_openapi() -> Dict[str, Any]:
    """Customizes the OpenAPI schema to include the API key in the security definitions."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Simple Prices API",
        version="0.0.1",
        description="Yet again, very simple",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        API_KEY_NAME: {
            "type": "apiKey",
            "name": API_KEY_NAME,
            "in": "header",
        }
    }
    openapi_schema["security"] = [{API_KEY_NAME: []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # use custom schema


def get_arguments() -> argparse.Namespace:
    """
    Parse and return command line arguments.
    """

    # Load environment variables from .env file
    load_dotenv()
    parser = argparse.ArgumentParser()

    db_args = parser.add_argument_group(title="Database arguments")
    db_args.add_argument(
        "-d",
        "--dir",
        action="store",
        help="Directory for SqLite database",
        required=False,
        default=os.getenv("DB_DIR", "data"),
    )
    db_args.add_argument(
        "-n",
        "--name",
        action="store",
        help="Name for SqLite database file",
        required=False,
        default=os.getenv("DB_NAME", "btc_prices.db"),
    )
    db_args.add_argument(
        "--retention-days",
        action="store",
        help="Database data retention days",
        required=False,
        default=int(os.getenv("RETENTION_DAYS", 365)),
    )

    curr_args = parser.add_argument_group(title="Currency parameters")
    curr_args.add_argument(
        "-t",
        "--ticker",
        action="store",
        help="Ticker symbol for the cryptocurrency",
        required=False,
        default=os.getenv("TICKER", "BTC-USD"),
    )
    curr_args.add_argument(
        "-c",
        "--currencies",
        action="store",
        nargs="+",
        help="List of currencies to store prices for",
        required=False,
        default=os.getenv("CURRENCIES", "EUR CZK").split(),
    )

    svc_args = parser.add_argument_group(title="Service(s) parameters")
    svc_args.add_argument(
        "--clean-up-interval-mins",
        action="store",
        help="Interval (in minutes) to run DB clean up",
        required=False,
        default=int(os.getenv("CLEAN_UP_INTERVAL_MINS", 5)),
    )
    svc_args.add_argument(
        "--fetch-interval-mins",
        action="store",
        help="Interval (in minutes) to retrieve prices",
        required=False,
        default=int(os.getenv("FETCH_INTERVAL_MINS", 1)),
    )

    parser.add_argument(
        "--api-key",
        action="store",
        help="API key for accessing the service",
        required=False,
        default=os.getenv("API_KEY"),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Should we run the script in debug mode?",
        required=False,
        default=os.getenv("DEBUG", "false").lower() == "true",
    )

    parser.add_argument(
        "--host",
        action="store",
        help="Bind socket to this host",
        required=False,
        default=os.getenv("HOST", "0.0.0.0"),
    )

    parser.add_argument(
        "--port",
        action="store",
        help="Bind socket to this port",
        required=False,
        default=int(os.getenv("PORT", 8000)),
    )

    return parser.parse_args()


def signal_handler(sig, frame) -> None:
    """
    Handles termination signals (SIGTERM, SIGINT) to shut down the application gracefully.
    """
    logging.info(f"Received signal {sig}. Shutting down...")
    shutdown_services(scheduler)
    sys.exit(0)


if __name__ == "__main__":
    global scheduler
    args = get_arguments()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - " "%(name)s - " "%(levelname)s - " "%(message)s",
    )

    # Initialize the database
    db_instance = Database(args.dir, args.name)
    db_instance.init_db()

    # Initialize services
    scheduler = init_services(args)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Add routers to FastAPI application
    app.include_router(
        prices_router(db_instance, args.currencies, args.api_key),
    )
    app.include_router(health_router())

    uvicorn.run(app, host=args.host, port=args.port)

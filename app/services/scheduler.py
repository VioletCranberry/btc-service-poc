import argparse
import logging
import signal
from datetime import datetime
from typing import Dict, List, Union

from apscheduler.schedulers.background import BackgroundScheduler
from services.cleanup import cleanup_db_data
from services.price_data import store_prices


def init_services(args: argparse.Namespace) -> BackgroundScheduler:
    """Initialize the background services"""
    # TODO: provide a better way how to configure background services.
    logging.info("Initializing services...")
    scheduler = BackgroundScheduler()

    # Prepare arguments for the cleanup_db_data job
    db_args: Dict[str, Union[str, int]] = {
        "db_dir": args.dir,
        "retention_days": args.retention_days,
        "db_name": args.name,
    }
    scheduler.add_job(
        cleanup_db_data,
        "interval",
        minutes=args.clean_up_interval_mins,
        kwargs=db_args,
        next_run_time=datetime.now(),  # Start immediately
    )

    # Prepare arguments for the store_prices job
    price_args: Dict[str, Union[str, List[str]]] = {
        "db_dir": args.dir,
        "currencies": args.currencies,
        "db_name": args.name,
        "ticker": args.ticker,
    }
    scheduler.add_job(
        store_prices,
        "interval",
        minutes=args.fetch_interval_mins,
        kwargs=price_args,
        next_run_time=datetime.now(),  # Start immediately
    )

    scheduler.start()
    return scheduler


def shutdown_services(scheduler: BackgroundScheduler) -> None:
    logging.info("Shutting down services...")
    scheduler.shutdown() 

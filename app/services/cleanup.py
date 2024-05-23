import logging
from datetime import datetime, timedelta, timezone

from database.db import Database
from database.models import BitcoinPrice


def cleanup_db_data(db_dir: str, db_name: str, retention_days: int) -> None:
    logging.info(f"Cleaning up database {db_dir}/{db_name} data")
    db_instance = Database(db_dir, db_name)
    db = next(db_instance.get_db())

    final_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    db.query(BitcoinPrice).filter(BitcoinPrice.date < final_date).delete()
    db.commit()

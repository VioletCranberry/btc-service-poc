import logging
import os
from typing import Generator

from config import get_database_uri
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for declarative class definitions
Base = declarative_base()


class Database:
    def __init__(self, db_dir: str, db_name: str) -> None:
        """
        Initializes the Database object with the specified directory and database name.
        """
        self.db_dir = db_dir
        self.db_name = db_name
        self.engine = None
        self.setup_db()

    def setup_db(self) -> None:
        """
        Sets up the database by creating the engine and sessionmaker.
        """
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        database_uri = get_database_uri(self.db_dir, self.db_name)
        self.engine = create_engine(database_uri)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def init_db(self) -> None:
        """
        Initializes the database by creating all tables.
        """
        logging.info("Initialising database")
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator:
        """
        Provides a database session generator.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

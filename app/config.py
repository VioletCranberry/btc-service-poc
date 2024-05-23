import os


def get_database_uri(db_dir: str, db_name: str) -> str:
    return f"sqlite:///{os.path.join(db_dir, db_name)}"

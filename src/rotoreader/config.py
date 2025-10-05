import os

import git

ROOT_DIR = str(git.Repo(".", search_parent_directories=True).working_tree_dir)
DATA_DIR = os.path.join(ROOT_DIR, "data")


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5445")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rotoreader")


APP_PORT = int(os.environ.get("APP_PORT", 8001))


def get_pg_url(db: str | None = None) -> str:
    db = db or POSTGRES_DB
    return (
        f"postgresql://{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{db}"
    )

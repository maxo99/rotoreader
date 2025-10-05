import os

import git

ROOT_DIR = str(git.Repo(".", search_parent_directories=True).working_tree_dir)
DATA_DIR = os.path.join(ROOT_DIR, "data")


APP_PORT = int(os.environ.get("APP_PORT", 8001))

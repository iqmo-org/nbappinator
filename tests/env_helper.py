import os

import dotenv

# universal_path extends PathLib to allow S3 paths
from upath import UPath as Path

# Load defaults
dotenv.load_dotenv(dotenv_path="tests/.default_env", override=False)

# Load local .env
dotenv.load_dotenv(override=True)

NOTEBOOK_DIR = Path(os.environ["NOTEBOOK_DIR"])
SKIP_NOTEBOOKS = os.environ["SKIP_NOTEBOOKS"].split(" ")  # ["1_readme_example.ipynb"]
NOTEBOOK_TIMEOUT = int(os.environ.get("NOTEBOOK_TIMEOUT", 600))
SEARCH = os.environ["SEARCH"]

BASELINE_DIR = Path(os.environ.get("BASELINE_DIR", NOTEBOOK_DIR / "baseline"))
RUNTIME_DIR = Path(os.environ.get("RUNTIME_DIR", NOTEBOOK_DIR / "checkpoint"))

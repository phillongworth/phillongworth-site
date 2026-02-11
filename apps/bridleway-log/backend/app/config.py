import os
from pathlib import Path

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bridleway:changeme@localhost:5432/bridleway_log"
)

# GPX file storage directory
# Default to /var/www/phillongworth-site/data/gpx/activities
# Can be overridden with GPX_STORAGE_DIR environment variable
DEFAULT_GPX_DIR = Path(__file__).parent.parent.parent.parent.parent / "data" / "gpx" / "activities"
GPX_STORAGE_DIR = Path(os.getenv("GPX_STORAGE_DIR", str(DEFAULT_GPX_DIR)))

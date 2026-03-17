from datetime import datetime, timezone

MONGO_URI = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000"
DB_NAME = "fisiodesk"

REFERENCE_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)  # upper bound esclusivo
WINDOW_START = datetime(2024, 10, 1, tzinfo=timezone.utc)

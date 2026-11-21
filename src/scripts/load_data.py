from pathlib import Path
import pandas as pd
from src.database.db import engine

ROOT_DIR = Path(__file__).resolve().parents[2]
SQL_FILE = ROOT_DIR / "src" / "database" / "combined.sql"


def main() -> None:
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found at: {SQL_FILE}")

    sql_script = SQL_FILE.read_text(encoding="utf-8")

    with engine.begin() as conn:
        conn.exec_driver_sql(sql_script)

    tables = ["routes", "route_variants", "stops", "timetable_entries"]
    for table in tables:
        df = pd.read_sql(f"SELECT COUNT(*) AS count FROM {table}", con=engine)
        print(f"[OK] {table}: {df['count'].iloc[0]} rows")


if __name__ == "__main__":
    main()

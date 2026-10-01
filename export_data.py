from pathlib import Path
import csv
import sqlite3

root = Path(__file__).resolve().parent
output = root / "powerbi_data"
output.mkdir(exist_ok=True)

with sqlite3.connect(
    (root / "data" / "igaming.db").as_uri() + "?mode=ro",
    uri=True
) as connection:
    for table in ["players", "deposits", "player_daily"]:
        cursor = connection.execute(f"SELECT * FROM {table}")

        with (output / f"{table}.csv").open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(column[0] for column in cursor.description)
            writer.writerows(cursor)

        print(f"Exported {table}.csv")
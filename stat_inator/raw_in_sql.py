from pathlib import Path
import json
import pandas as pd
from sqlalchemy import create_engine

def load_raw_into_sql():
   configs = json.loads((Path(__file__).resolve().parent.joinpath("config.json").read_text()))
   dump_dir = Path(configs["file_dump"])
   archive_dir = Path(configs["file_archive"])

   engine = create_engine('mssql+pyodbc://@' + configs["sql_server"] + '/' + configs["sql_db"] + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')

   for f in Path(dump_dir).glob("*.json"):
      print(f)
      guid, date, time = f.parts[-1].replace(".json", "").split("_")

      timestamp = f"{date[:4]}-{date[4:6]}-{date[6:8]} {time[:2]}:{time[2:4]}:{time[4:6]}"

      file_text = f.read_text()
      file_clean = file_text.replace("minecraft:", "")
      file_json = json.loads(file_clean)

      df = pd.DataFrame(columns=["guid", "timestamp", "type", "stat", "value"])
      for type, stats in file_json["stats"].items():
         temp = pd.DataFrame(list(stats.items()), columns=["stat", "value"])
         temp.insert(0, "guid", guid)
         temp.insert(1, "timestamp", timestamp)
         temp.insert(3, "type", type)
         df = pd.concat([df if not df.empty else None, temp])

      df.to_sql(con=engine, schema="raw", name="snapshots", if_exists="append", index=False)
      f.rename(archive_dir.joinpath(f.parts[-1]))


   engine.dispose()


if __name__ == "__main__":
   load_raw_into_sql()
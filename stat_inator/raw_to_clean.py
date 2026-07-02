from pathlib import Path
import json
import pandas as pd
from sqlalchemy import Engine, create_engine, text

def clean_data_in_sql():
   configs = json.loads((Path(__file__).resolve().parent.joinpath("config.json").read_text()))

   engine = create_engine('mssql+pyodbc://@' + configs["sql_server"] + '/' + configs["sql_db"] + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
   
   # Get new dim values
   get_new_dim(engine, "guid")
   get_new_dim(engine, "type")
   get_new_dim(engine, "stat")

   get_new_fact(engine)


def get_new_dim(engine: Engine, dim: str):
   with engine.connect() as conn:
      query = text(f"SELECT {dim} FROM dbo.dim_{dim}")
      result = conn.execute(query)
      existing = pd.DataFrame(result)

      query = text(f"SELECT DISTINCT {dim} FROM raw.snapshots")
      result = conn.execute(query)
      raw = pd.DataFrame(result)

      if existing.empty:
         print(f"{raw.count(axis=1)} new {dim}(s)")
         raw.to_sql(con=engine, schema="dbo", name=f"dim_{dim}", if_exists="append", index=False)
      else:
         new = pd.concat([raw, existing]).drop_duplicates(keep=False)
         print(f"{new.count(axis=1)} new {dim}(s)")
         new.to_sql(con=engine, schema="dbo", name=f"dim_{dim}", if_exists="append", index=False)


def get_new_fact(engine: Engine):
   with engine.connect() as conn:
      raw = pd.DataFrame(conn.execute(text("SELECT guid, timestamp, type, stat, CAST(value AS INT) AS snap FROM raw.snapshots WHERE timestamp > (SELECT COALESCE(MAX(timestamp),'2026-01-01 00:00:00') FROM dbo.fact_value)")))

      if raw.empty:
         return
      
      # Get id/value mappings for dims
      dim_guid = pd.DataFrame(conn.execute(text("SELECT id as dim_guid_id, guid FROM dbo.dim_guid")))
      dim_type = pd.DataFrame(conn.execute(text("SELECT id as dim_type_id, type FROM dbo.dim_type")))
      dim_stat = pd.DataFrame(conn.execute(text("SELECT id as dim_stat_id, stat FROM dbo.dim_stat")))

      # Join dim ids onto new data
      new = raw.merge(dim_guid, how="left", on="guid")
      new = new.merge(dim_type, how="left", on="type")
      new = new.merge(dim_stat, how="left", on="stat")

      # Keep only relevant columns
      new = new[["dim_guid_id", "dim_type_id", "dim_stat_id", "timestamp", "snap"]]

      query = text("""SELECT 
    dim_guid_id
  , dim_type_id
  , dim_stat_id
  , '2026-01-01 00:00:00' AS timestamp
  , SUM(value) AS snap
FROM dbo.fact_value
GROUP BY
    dim_guid_id
  , dim_type_id
  , dim_stat_id""")

      existing = pd.DataFrame(conn.execute(query))

      # Concat existing and new data, sorted by dims and timestamp
      fact = pd.concat([existing, new], ignore_index=True).sort_values(by=["dim_guid_id", "dim_type_id", "dim_stat_id", "timestamp"])

      # Add check if each dim is equal to prior row
      fact["guid_check"] = fact["dim_guid_id"].eq(fact["dim_guid_id"].shift())
      fact["type_check"] = fact["dim_type_id"].eq(fact["dim_type_id"].shift())
      fact["stat_check"] = fact["dim_stat_id"].eq(fact["dim_stat_id"].shift())

      # Add check if all dims are equal to prior row
      fact["check"] = sum([fact["guid_check"], fact["type_check"], fact["stat_check"]])

      # Create value column that is the delta between current and prior row
      fact["value"] = fact["snap"] - fact["snap"].shift()

      # For rows where not all dims are equal to prior row, overwrite delta with raw value
      fact.loc[fact["check"] < 3, "value"] = fact["snap"]

      # Filter out 0 and existing values
      fact = fact.loc[(fact["value"] != 0) & (fact["timestamp"] > "2026-01-01 00:00:00"), ["dim_guid_id", "dim_type_id", "dim_stat_id", "timestamp", "value"]]

      print(f"{fact.count(axis=1)} new fact rows")
      fact.to_sql(con=engine, schema="dbo", name="fact_value", if_exists="append", index=False)

if __name__ == "__main__":
   clean_data_in_sql()
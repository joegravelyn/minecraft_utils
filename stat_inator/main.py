from paramiko import Transport, SFTPClient, SFTPAttributes
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

def main():
   cur_date = datetime.now()

   configs = json.loads((Path(__file__).resolve().parent.joinpath("config.json").read_text()))
   df = combine_files_into_df(configs)
   if df is None: return
   
   if df.empty:
      df = pd.DataFrame([(cur_date, "filler", pd.NA, "filler", 0)], columns=["timestamp", "player_guid", "group", "stat", "value"])

   existing_df = pd.concat((pd.read_csv(f) for f in Path(configs["out"]).glob("*.csv")))
   existing_df = existing_df.groupby(["player_guid", "group", "stat"], as_index=False)["value"].sum()
   
   combined = df.merge(existing_df, how="left", on=["player_guid", "group", "stat"], suffixes=["_new", "_old"])
   combined["value"] = combined["value_new"] - combined["value_old"]
   combined = combined.drop(["value_new", "value_old"], axis=1)
   combined = combined[combined["value"] != 0]

   combined.to_csv(Path(configs["out"]).joinpath(f"{cur_date.strftime("%Y%m%d_%H%M%S")}.csv"), index=False)


def combine_files_into_df(configs):
   trans = Transport((configs["host"], configs["port"]))
   trans.connect(username=configs["user"], password=configs["pass"])

   sftp = SFTPClient.from_transport(trans)
   if sftp is None:
      return
   
   last_check_date = datetime.fromtimestamp(max([f.stat().st_mtime for f in Path(configs["out"]).glob("*.csv")]))

   df = pd.DataFrame(columns=["timestamp", "player_guid", "group", "stat", "value"])
   files = sftp.listdir_attr(configs["stats_dir"])
   for f in files:
      temp_df = process_file(sftp, f, configs["stats_dir"], last_check_date)
      df = pd.concat([df, temp_df if not temp_df.empty else None]) if not df.empty else temp_df

   sftp.close()
   trans.close()

   return df


def process_file(sftp: SFTPClient, f: SFTPAttributes, dir: str, check_date: datetime) -> pd.DataFrame:
   df = pd.DataFrame(columns=["timestamp", "player_guid", "group", "stat", "value"])

   guid = f.filename.replace(".json", "")
   time = datetime.fromtimestamp(f.st_mtime) if f.st_mtime is not None else check_date

   if time <= check_date: return df

   file_byte = sftp.open(dir + "/" + f.filename).read()
   file_text = file_byte.decode()
   file_clean = file_text.replace("minecraft:", "")
   file_json = json.loads(file_clean)

   for group, stats in file_json["stats"].items():
      # print(group)
      temp = pd.DataFrame(list(stats.items()), columns=["stat", "value"])
      temp.insert(0, "timestamp", time)
      temp.insert(1, "player_guid", guid)
      temp.insert(2, "group", group)
      df = pd.concat([df if not df.empty else None, temp])

   return df


if __name__ == "__main__":
   main()
from pathlib import Path
import json
from datetime import datetime
import hashlib
import pandas as pd


def main(check_all = False):
   cur_date = datetime.now()

   configs = json.loads((Path(__file__).resolve().parent.joinpath("config.json").read_text()))
   
   target_dir = Path(configs["target_dir"])
   if not target_dir.exists(): target_dir.mkdir(parents=True)

   list_dir = target_dir.joinpath("list.csv")
   list_df = pd.read_csv(list_dir) if list_dir.exists() else pd.DataFrame(columns=["hash","timestamp","name","original_dir"])

   date_dir = target_dir.joinpath("last_run.csv")
   last_date = datetime.fromisoformat(date_dir.read_text()) if date_dir.exists() else datetime(2009, 5, 10)

   appdata = Path.home().joinpath("AppData", "Roaming")

   if configs["bedrock"]:
      bedrock_user_folder = appdata.joinpath("Minecraft Bedrock", "Users")
      for p in bedrock_user_folder.glob("*/games/com.mojang/Screenshots/*"):
         list_df = copy_screenshots(p, target_dir, list_df, last_date)

   if configs["java"]:
      java_folder = appdata.joinpath(".minecraft", "screenshots")
      list_df = copy_screenshots(java_folder, target_dir, list_df, last_date)

   if any(configs["other_java_installs"]):
      for i in configs["other_java_installs"]:
         for p in Path(i).glob("*"):
            p_ = p.joinpath("screenshots")
            list_df = copy_screenshots(p_, target_dir, list_df, last_date)

   list_df.to_csv(list_dir, index=False)
   target_dir.joinpath("last_run.txt").write_text(cur_date.isoformat())


def copy_screenshots(mc_path: Path, target_path: Path, check_df: pd.DataFrame, check_time: datetime) -> pd.DataFrame:
   for pic in [f for f in mc_path.glob("*") if f.suffix in {".jpeg", ".png"}]:
      dt = datetime.fromtimestamp(pic.stat().st_mtime)
      if dt <= check_time: continue

      hash = image_hash(pic)
      if any(check_df["hash"] == hash): continue
      
      dt_count = len(check_df[check_df["timestamp"] == dt])

      new_name = dt.strftime("%Y-%m-%d-%H-%M-%S") + (f"-{dt_count}" if dt_count > 0 else "")

      new_file = target_path.joinpath(f"{new_name}{pic.suffix}")

      new_file.write_bytes(pic.read_bytes())
      check_df = pd.concat((check_df, pd.DataFrame([[hash, dt, new_name, pic]], columns=["hash","timestamp","name","original_dir"])))
   return check_df  


def image_hash(p: Path) -> str:
   sha256 = hashlib.sha256()
   with p.open("rb") as file:
      while chunk := file.read(65536):
         sha256.update(chunk)
   return sha256.hexdigest()
   
if __name__ == "__main__":
   main()
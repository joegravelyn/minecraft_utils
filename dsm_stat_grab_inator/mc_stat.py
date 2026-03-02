from pathlib import Path
from datetime import datetime
import json
from paramiko import Transport, SFTPClient, SFTPAttributes

def main():
   cur_date = datetime.now()

   configs = json.loads((Path(__file__).resolve().parent.joinpath("config.json").read_text()))

   trans = Transport((configs["host"], configs["port"]))
   trans.connect(username=configs["user"], password=configs["pass"])
   
   sftp = SFTPClient.from_transport(trans)
   if sftp is None:
      return
   
   local_dir = configs["out"]
   last_check_date = datetime.fromtimestamp(max([f.stat().st_mtime for f in Path(local_dir).glob("*.json")]))
   
   files = sftp.listdir_attr(configs["stats_dir"])
   for f in files:
      time = datetime.fromtimestamp(f.st_mtime) if f.st_mtime is not None else cur_date
      if time >= last_check_date:
         remote_file = configs["stats_dir"] + f.filename
         local_file = local_dir + f.filename.removesuffix(".json") + "_" + cur_date.strftime('%Y%m%d_%H%M%S') + ".json"
         sftp.get(remote_file, local_file)

if __name__ == "__main__":
   main()
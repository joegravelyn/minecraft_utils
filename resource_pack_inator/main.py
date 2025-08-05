from pathlib import Path
import pandas as pd
import json

rpi_dir = Path.cwd().joinpath("resource_pack_inator")
output_dir = rpi_dir.joinpath("output")

for x in output_dir.iterdir():
   for y in x.iterdir():
      y.unlink()
   x.rmdir()

# input_list = pd.read_csv(rpi_dir.joinpath("input.csv"))

# for n in input_list["namespace"].drop_duplicates():
#    output_dir.joinpath(n).mkdir(exist_ok=True)

# for i, c in input_list[["namespace", "path", "name"]].drop_duplicates().iterrows():
#    item_model_json = {"model": {"type": "minecraft:model", "model": f"{c["namespace"]}:item/{c["name"]}"}}
#    item_model_file = output_dir.joinpath(c["namespace"], "items", f"{c["name"]}.json")
#    item_model_file.write_text(json.dumps(item_model_json, indent=3))

# input_list["mc_item_index"] = input_list.groupby("mc_item")["custom_index"].rank()






# print(input_list)



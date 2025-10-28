from pathlib import Path
import pandas as pd
import json

from item_specifics import item_bow, item_bundle, item_music_disc, item_painting

def main():
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   input_dir = rpi_dir.joinpath("input")
   output_dir = rpi_dir.joinpath("output")

   item_bow.create_item_model(input_dir, output_dir)
   item_bundle.create_item_model(input_dir, output_dir)
   item_music_disc.create_item_model(input_dir, output_dir)
   item_painting.create_item_model(input_dir, output_dir)

   create_item_model(input_dir, output_dir)


def create_item_model(input_dir: Path, output_dir: Path):
   mc_items_dir = output_dir.joinpath("minecraft", "items")
   mc_items_dir.mkdir(exist_ok=True, parents=True)

   input_list = pd.read_csv(input_dir.joinpath("_general.csv"))

   for mc_item in input_list["__minecraft_item"].drop_duplicates():
      if pd.isna(mc_item): continue
      if mc_item in ["bow", "bundle", "painting"]: continue
      if mc_item in [d.name.removesuffix(".json") for d in output_dir.parent.joinpath("mc_defaults").glob("**/music_disc_*.json")]: continue

      custom_items = input_list[input_list["__minecraft_item"] == mc_item]
      custom_items["mc_item_index"] = custom_items[pd.notna(input_list["__minecraft_item"])].groupby("__minecraft_item")["__num"].rank().astype(int)

      if len(custom_items) > 0:
         cmd_cases, name_cases = create_cases(custom_items)

         fallback = json.loads(output_dir.parent.joinpath("mc_defaults").joinpath(f"{mc_item}.json").read_text())["model"]

         if len(name_cases) > 0:
            cmd_cases.insert(0, {
               "threshold": 0, 
               "model": {
                  "type": "minecraft:select",
                  "property": "minecraft:component",
                  "component": "minecraft:custom_name",
                  "cases": name_cases,
                  "fallback": fallback
               }
            })

         item_model = {"model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "entries": cmd_cases,
            "fallback": fallback
            }
         }

         if __name__ == "__main__": print(item_model)
         mc_items_dir.joinpath(f"{mc_item}.json").write_text(json.dumps(item_model, indent=2))


def create_cases(inputs: pd.DataFrame) -> tuple[list, list]:
   cmd_cases = []
   name_cases = []

   max_num = max(inputs["mc_item_index"])

   for i, input in inputs.iterrows():
      i_num = int(input["mc_item_index"]) if pd.notna(input["mc_item_index"]) else max_num + i
      i_path = f"{input["__item_path"]}/" if pd.notna(input["__item_path"]) else ""
      i_full_path = f"{input["item_namespace"]}:item/{i_path}"
      i_model = f"{i_full_path}{input["item_name"]}"

      cmd_cases.append({"threshold": i_num, "model": {"type": "minecraft:model", "model": i_model}})

      if pd.notna(input["__in_game_name"]):
         name_cases.append({"when": input["__in_game_name"], "model": {"type": "minecraft:model", "model": i_model}})

   return cmd_cases, name_cases

if __name__ == "__main__":
   main()
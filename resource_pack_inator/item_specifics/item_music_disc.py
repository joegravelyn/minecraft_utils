from pathlib import Path
import pandas as pd
import json

def main():
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   input_dir = rpi_dir.joinpath("input")
   output_dir = rpi_dir.joinpath("output")

   create_item_model(input_dir, output_dir)


def create_item_model(input_dir: Path, output_dir: Path):
   input_list = pd.read_csv(input_dir.joinpath("music_disc.csv"))
   if len(input_list) > 0:

      mc_items_dir = output_dir.joinpath("minecraft", "items")
      mc_items_dir.mkdir(exist_ok=True, parents=True)

      cmd_cases, name_cases = create_cases(input_list)

      # if len(name_cases) > 0:
      #    cmd_cases.insert(0, {
      #       "threshold": 0, 
      #       "model": {
      #          "type": "minecraft:select",
      #          "property": "minecraft:component",
      #          "component": "minecraft:custom_name",
      #          "cases": name_cases,
      #          "fallback": {}
      #       }
      #    })

      item_model = {"model": {
         "type": "minecraft:range_dispatch",
         "property": "minecraft:custom_model_data",
         "entries": cmd_cases,
         "fallback": {}
         }
      }

      if __name__ == "__main__": print(item_model)

      discs = output_dir.parent.joinpath("mc_defaults").glob("**/music_disc_*.json")
      for d_file in discs:
         print(d_file)
         fallback = json.loads(d_file.read_text())["model"]
         item_model["model"]["fallback"] = fallback
         mc_items_dir.joinpath(d_file.name).write_text(json.dumps(item_model, indent=2))


def create_cases(inputs: pd.DataFrame) -> tuple[list, list]:
   cmd_cases = []
   name_cases = []

   max_num = max(inputs["__num"])

   for i, input in inputs.iterrows():
      i_num = int(input["__num"]) if pd.notna(input["__num"]) else max_num + i
      i_path = f"{input["__item_path"]}/" if pd.notna(input["__item_path"]) else ""
      i_model = f"{input["item_namespace"]}:item/{i_path}{input["item_name"]}"

      cmd_cases.append({"threshold": i_num, "model": {"type": "minecraft:model", "model": i_model}})

      if pd.notna(input["__in_game_name"]):
         name_cases.append({"when": input["__in_game_name"], "model": {"type": "minecraft:model", "model": i_model}})

   return cmd_cases, name_cases

if __name__ == "__main__":
   main()
from pathlib import Path
import pandas as pd
import json

def main():
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   output_dir = rpi_dir.joinpath("output")

   # Clear output folder
   for x in output_dir.iterdir():
      clear_dir(x)

   # Read input csv
   input_list = pd.read_csv(rpi_dir.joinpath("input.csv"))
   input_list["mc_item_index"] = input_list.groupby("mc_item")["custom_index"].rank().astype(int)

   input_list.to_csv(output_dir.joinpath("inputs_with_custom_index.csv"), index=False)

   create_custom_item_models(input_list, output_dir)
   create_mc_item_models(input_list, output_dir)


# Create custom item models
def create_custom_item_models(inputs: pd.DataFrame, output_dir: Path):
   for namespace in inputs["namespace"].drop_duplicates():
      # Create items folder for each namespace
      items_dir = output_dir.joinpath(namespace, "items")
      items_dir.mkdir(exist_ok=True, parents=True)

      for path in inputs[inputs["namespace"] == namespace]["path"].drop_duplicates():

         if pd.notna(path):
            target_dir = items_dir.joinpath(path)
            items_dir.joinpath(path).mkdir(exist_ok=True, parents=True)
            filtered_inputs = inputs[(inputs["namespace"] == namespace) & (inputs["path"] == path)][["name", "mc_item"]].drop_duplicates()
         else:
            target_dir = items_dir
            filtered_inputs = inputs[(inputs["namespace"] == namespace) & (inputs["path"].isna())][["name", "mc_item"]].drop_duplicates()


         for i, item in filtered_inputs.iterrows():
            if item["mc_item"] == "bow":
               pass

            elif item["mc_item"] == "bundle":
               pass

            else:
               item_model_json = {"model": {"type": "minecraft:model", "model": f"{namespace}:item/{item["name"]}"}}

               target_dir.joinpath(f"{item["name"]}.json").write_text(json.dumps(item_model_json, indent=3))



# Create minecraft item models
def create_mc_item_models(inputs: pd.DataFrame, output_dir: Path):
   mc_defaults = output_dir.parent.joinpath("mc_defaults")
   mc_items_dir = output_dir.joinpath("minecraft", "items")
   mc_items_dir.mkdir(exist_ok=True, parents=True)

   for mc_item in inputs["mc_item"].drop_duplicates():
      custom_items = inputs[inputs["mc_item"] == mc_item]
      cmd_cases = make_custom_model_data_cases(custom_items)
      custom_name = make_custom_name_part(mc_item, custom_items)

      if custom_name != {}: cmd_cases.insert(0, custom_name)

      if mc_item == "bow":
         pass

      elif mc_item == "bundle":
         pass

      else:
         mc_item_model = {
            "model": {
               "type": "minecraft:range_dispatch",
               "property": "minecraft:custom_model_data",
               "entries": cmd_cases,
               "fallback": {}
            }
         }


         if mc_item == "$ALL_MUSIC_DISCS$":
            discs = mc_defaults.glob("**/music_disc*.json")
            for d_file in discs:
               d = d_file.name.removesuffix(".json")
               mc_item_model["model"]["fallback"]["model"] = json.loads(mc_defaults.joinpath(d_file.name).read_text())["model"]
               mc_items_dir.joinpath(f"{d}.json").write_text(json.dumps(mc_item_model, indent=3))

         else:
            mc_item_model["model"]["fallback"] = json.loads(mc_defaults.joinpath(f"{mc_item}.json").read_text())["model"]
            mc_items_dir.joinpath(f"{mc_item}.json").write_text(json.dumps(mc_item_model, indent=3))


def make_custom_model_data_cases(inputs: pd.DataFrame) -> list[dict]:
   cases = []
   for i, input in inputs.iterrows():
      custom_model_string = f"{input["namespace"]}:{input["type"]}/{f"{input["path"]}/" if pd.notna(input["path"]) else ""}{input["name"]}"
      cases.append({
         "threshold": input["mc_item_index"], 
         "model": {
            "type": "minecraft:model", 
            "model": custom_model_string
         }
      })
   return cases

def make_custom_name_cases(inputs: pd.DataFrame) -> list[dict]:
   cases = []
   for i, input in inputs.iterrows():
      if pd.notna(input["in_game_name"]):
         custom_model_string = f"{input["namespace"]}:{input["type"]}/{f"{input["path"]}/" if pd.notna(input["path"]) else ""}{input["name"]}"
         cases.append({
            "when": input["in_game_name"], 
            "model": {
               "type": "minecraft:model", 
               "model": custom_model_string
            }
         })
   return cases

def make_custom_name_part(mc_item: str, inputs: pd.DataFrame) -> dict:
   cases = make_custom_name_cases(inputs)
   if len(cases) > 0:
      return {
         "threshold": 0, 
         "model": {
            "type": "minecraft:select",
            "property": "minecraft:component",
            "component": "minecraft:item_name",
            "cases": cases,
            "fallback": {
               "type": "minecraft:model",
               "model": f"minecraft:item/{mc_item}"
            }
         }
      }

   else: return {}

def clear_dir(p: Path):
   if p.is_file():
      p.unlink()
   else:
      for d in p.iterdir():
         clear_dir(d)
      p.rmdir()

if __name__ == "__main__":
   main()
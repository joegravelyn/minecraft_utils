from pathlib import Path
import pandas as pd
import json

from item_specifics import item_bow, item_bundle, item_music_disc, item_painting, dp_painting
pd.options.mode.chained_assignment = None

def main():
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   input_dir = rpi_dir.joinpath("input")
   output_dir = rpi_dir.joinpath("output")
   
   mc_items_dir = output_dir.joinpath("minecraft", "items")
   mc_items_dir.mkdir(exist_ok=True, parents=True)
   clear_dir(mc_items_dir)

   item_bow.create_item_model(input_dir, output_dir)
   item_bundle.create_item_model(input_dir, output_dir)
   item_music_disc.create_item_model(input_dir, output_dir)
   item_painting.create_item_model(input_dir, output_dir)
   dp_painting.creating_painting_dp_files(input_dir, output_dir)

   create_item_model(input_dir, output_dir)


def create_item_model(input_dir: Path, output_dir: Path):
   input_list = pd.read_csv(input_dir.joinpath("_general.csv"))

   for mc_item in input_list["__minecraft_item"].drop_duplicates():
      if pd.isna(mc_item): continue
      if mc_item in ["bow", "bundle", "painting"]: continue
      if mc_item in [d.name.removesuffix(".json") for d in output_dir.parent.joinpath("mc_defaults").glob("**/music_disc_*.json")]: continue

      custom_items = input_list[input_list["__minecraft_item"] == mc_item]
      custom_items["mc_item_index"] = custom_items.loc[pd.notna(input_list["__minecraft_item"])].groupby("__minecraft_item")["__num"].rank().astype(int)

      cmd_cases, name_cases, user_list = create_cases(custom_items)

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

      # if __name__ == "__main__": print(item_model)
      output_dir.joinpath("minecraft", "items", f"{mc_item}.json").write_text(json.dumps(item_model, indent=2))

      create_custom_item(cmd_cases, output_dir)
   
      update_user_list_file(mc_item, user_list, output_dir)


def create_cases(inputs: pd.DataFrame) -> tuple[list, list, list]:
   cmd_cases = []
   name_cases = []
   user_list = []

   max_num = max(inputs["mc_item_index"])

   for i, input in inputs.iterrows():
      i_num = int(input["mc_item_index"]) if pd.notna(input["mc_item_index"]) else max_num + i
      i_path = f"{input["__item_path"]}/" if pd.notna(input["__item_path"]) else ""
      i_full_path = f"{input["item_namespace"]}:item/{i_path}"
      i_model = f"{i_full_path}{input["item_name"]}"

      cmd_cases.append({"threshold": i_num, "model": {"type": "minecraft:model", "model": i_model}})

      if pd.notna(input["__in_game_name"]):
         name_cases.append({"when": input["__in_game_name"], "model": {"type": "minecraft:model", "model": i_model}})

      user_list.append(["", i_num, input["__in_game_name"], i_model.replace(":item/", ":")])

   return cmd_cases, name_cases, user_list

def update_user_list_file(mc_item: str, user_list: list, output_dir: Path):
   # if __name__ == "__main__": print(user_list)
   ul_file = output_dir.joinpath("user_list.csv")
   ul_df = pd.read_csv(ul_file)
   ul_df = ul_df[ul_df["minecraft_item"] != mc_item]
   update_df = pd.DataFrame(user_list, columns=["minecraft_item", "custom_model_data", "custom_name", "custom_model"])
   update_df["minecraft_item"] = mc_item
   ul_df = pd.concat([ul_df, update_df])
   ul_df.to_csv(ul_file, index=False)

def create_custom_item(custom_models: list[dict], output_dir: Path):
   for cm in custom_models:
      threshold = cm.pop("threshold", 0)
      if threshold > 0:
         full_model = str(cm["model"]["model"])
         colon = full_model.find(":")
         namespace = full_model[:colon]
         model_path = full_model[colon + 1:].split("/")
         model_path.remove("item")
         model_path[-1] = model_path[-1] + ".json"
         
         model_file = output_dir.joinpath(namespace, "items", *model_path)
         model_file.parent.mkdir(exist_ok=True, parents=True)
         model_file.write_text(json.dumps(cm, indent=2))


def clear_dir(p: Path):
   for d in p.iterdir():
      delete_dir(d)

def delete_dir(p: Path):
   if p.is_file():
      p.unlink()
   else:
      for d in p.iterdir():
         delete_dir(d)
      p.rmdir()

if __name__ == "__main__":
   main()
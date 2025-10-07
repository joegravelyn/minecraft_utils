from pathlib import Path
import pandas as pd
import json

# Input asset folder that contains custom models and minecraft models with overrides
rp_dir = Path(input("Assets folder: "))

# Look through custom item models to get list of all custom items
items = []
item_index = 1
for namespace_folder in rp_dir.iterdir():
    namespace = namespace_folder.name

    if namespace != "minecraft":
        item_folder = namespace_folder.joinpath("models", "item")
        for item_file in item_folder.glob("**/*.json"):
            item_dict = dict.fromkeys(["namespace", "path", "custom_name", "custom_index", "custom_key"])
            item_dict["namespace"] = namespace
            item_dict["custom_index"] = item_index

            item_name_with_path = str(item_file.relative_to(item_folder)).removesuffix(".json")
            item_name_parts = item_name_with_path.split("\\")
            item_dict["custom_name"] = item_name_parts[-1]

            item_name_parts.remove(item_dict["custom_name"])
            item_dict["path"] = "/".join(item_name_parts)

            item_dict["custom_key"] = f"{namespace}:item/{item_dict["path"]}{"/" if item_dict["path"] != "" else ""}{item_dict["custom_name"]}"
            items.append(item_dict)
            item_index += 1

custom_df = pd.DataFrame(items)

# Look through minecraft models with overrides to get custom item to minecraft item mappings
mc_models = []
mc_dir = rp_dir.joinpath("minecraft")
model_folder = mc_dir.joinpath("items")
for model_file in model_folder.glob("**/*.json"):
   mc_item = model_file.name.removesuffix(".json")
   
   if mc_item == "shield": continue

   model_json = json.loads(model_file.read_text())

   fallback = model_json["model"]["fallback"]

   if fallback["type"] == "minecraft:model":
      mc_item_type = fallback["model"].removesuffix(f"/{mc_item}")
   else:
      mc_item_type = None

   if str(model_json["model"]["type"]).endswith("range_dispatch"):
      for r in model_json["model"]["entries"]:
         if r["threshold"] != 0:
            # print(r)

            mc_models.append({"mc_item": mc_item, "mc_item_type": mc_item_type, "custom_key": r["model"]["model"]})

mc_df = pd.DataFrame(mc_models)

# Put the two together and save to a csv
df = pd.merge(left=mc_df, right=custom_df, how="outer", on="custom_key")
df.to_csv(Path.cwd().joinpath("resource_pack_inator", "generated.csv"), index=False)
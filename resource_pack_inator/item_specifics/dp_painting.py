from pathlib import Path
import pandas as pd
import json

def main():
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   input_dir = rpi_dir.joinpath("input")
   output_dir = rpi_dir.joinpath("output")

   creating_painting_dp_files(input_dir, output_dir)


def creating_painting_dp_files(input_dir: Path, output_dir: Path):
   input_list = pd.read_csv(input_dir.joinpath("painting.csv"))

   placeable_list = []

   for namespace in input_list["_painting_namespace"].drop_duplicates():
      if pd.isna(namespace): continue
      if namespace == "minecraft": continue

      custom_items = input_list[input_list["_painting_namespace"] == namespace]

      if len(custom_items) == 0: continue

      paint_var_dir = output_dir.joinpath(namespace, "painting_variant")
      paint_var_dir.mkdir(exist_ok=True, parents=True)

      paint_recipe_dir = output_dir.joinpath(namespace, "recipe", "painting_variant")
      paint_recipe_dir.mkdir(exist_ok=True, parents=True)
      
      for i, input in custom_items.iterrows():
         p_namespace = input["_painting_namespace"]
         p_path = f"{input["__painting_path"]}/" if pd.notna(input["__painting_path"]) else ""
         p_name = input["painting_name"]
         p_fqn = f"{p_namespace}:{p_path}{p_name}"

         p_width = int(input["width"]) if pd.notna(input["width"]) else 1
         p_height = int(input["height"]) if pd.notna(input["height"]) else 1

         p_title = {"text": input["_title_text"] if pd.notna(input["_title_text"]) else p_name}
         if pd.notna(input["__title_color"]): p_title["color"] = input["__title_color"]

         p_author = {"text": input["_author_text"] if pd.notna(input["_author_text"]) else "Custom"}
         if pd.notna(input["__author_color"]): p_author["color"] = input["__author_color"]


         paint_var = {
            "asset_id": p_fqn,
            "width": p_width,
            "height": p_height,
            "title": p_title,
            "author": p_author
         }
         paint_var_dir.joinpath(f"{p_name}.json").write_text(json.dumps(paint_var, indent=2))

         paint_recipe = {"type": "minecraft:stonecutting", "ingredient": "minecraft:painting", "result": {"components": {
            "minecraft:painting/variant": p_fqn}, "count": 1, "id": "minecraft:painting"}}
         paint_recipe_dir.joinpath(f"{p_name}.json").write_text(json.dumps(paint_recipe, indent=2))

         if (input["_placeable"] if pd.notna(input["_placeable"]) else False): placeable_list.append(p_fqn)

   if len(placeable_list) > 0:
      placeable_dir = output_dir.joinpath("minecraft", "tags", "painting_variant")
      placeable_dir.mkdir(exist_ok=True, parents=True)

      placeable_dir.joinpath("placeable.json").write_text(json.dumps({"replace": False, "values": placeable_list}, indent=2))


if __name__ == "__main__":
   main()
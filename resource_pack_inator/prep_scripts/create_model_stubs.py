from pathlib import Path
import pandas as pd
import json

def main():
   # Input asset folder that contains sorted custom textures
   texture_dir = Path(input("Assets folder: "))
   create_stubs(texture_dir)

def create_stubs(texture_dir):
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   output_dir = rpi_dir.joinpath("output")

   for namespace_folder in texture_dir.iterdir():
      namespace = namespace_folder.name

      if namespace == "minecraft": continue

      t_dir = namespace_folder.joinpath("textures")
      for t_file in t_dir.glob("**/*.png"):
         item_parts = str(t_file.relative_to(t_dir)).removesuffix(".png").split("\\")
         model = {"parent": "item/generated", "textures": {"layer0": f"{namespace}:{"/".join(item_parts)}"}}
         o_dir = output_dir.joinpath(namespace, "models", *item_parts[:-1])
         o_dir.mkdir(exist_ok=True, parents=True)
         o_dir.joinpath(f"{item_parts[-1]}.json").write_text(json.dumps(model, indent=3))

if __name__ == "__main__":
   main()
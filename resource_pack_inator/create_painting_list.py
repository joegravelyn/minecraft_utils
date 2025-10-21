from pathlib import Path
import pandas as pd
import json

def main():
   # Input asset folder that contains custom models and minecraft models with overrides
   rp_dir = Path(input("Assets folder: "))
   create_list(rp_dir)

def create_list(dir):
   # Get list of all painting textures
   paintings = []
   painting_index = 1
   for namespace_folder in dir.iterdir():
      namespace = namespace_folder.name

      painting_folder = namespace_folder.joinpath("textures", "painting")

      for painting_file in painting_folder.glob("**/*.png"):
         painting_dict = dict.fromkeys(["namespace", "path", "custom_name", "custom_index"])
         painting_dict["namespace"] = namespace
         painting_dict["custom_index"] = painting_index

         painting_name_parts = str(painting_file.relative_to(painting_folder)).removesuffix(".png").split("\\")
         painting_dict["custom_name"] = painting_name_parts[-1]
         painting_dict["path"] = "/".join(painting_name_parts[:-1])

         paintings.append(painting_dict)
         painting_index += 1

   custom_df = pd.DataFrame(paintings)
   custom_df.to_csv(Path.cwd().joinpath("resource_pack_inator", "input", "__generated_painting.csv"), index=False)

if __name__ == "__main__":
   main()
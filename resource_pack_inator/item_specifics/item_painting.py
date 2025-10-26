from pathlib import Path
import pandas as pd
import json

def main():
   rpi_dir = Path.cwd().joinpath("resource_pack_inator")
   input_dir = rpi_dir.joinpath("input")
   output_dir = rpi_dir.joinpath("output")

   create_painting_model(input_dir, output_dir)


def create_painting_model(input_dir: Path, output_dir: Path):
   painting_list = pd.read_csv(input_dir.joinpath("painting.csv"))
   if len(painting_list) > 0:

      mc_items_dir = output_dir.joinpath("minecraft", "items")
      mc_items_dir.mkdir(exist_ok=True, parents=True)

      model = {"model": {
         "type": "minecraft:select",
         "property": "minecraft:component",
         "component": "minecraft:painting/variant",
         "cases": make_custom_painting_variant_cases(painting_list),
         "fallback": json.loads(output_dir.parent.joinpath("mc_defaults").joinpath("painting.json").read_text())["model"]
         }
      }

      if __name__ == "__main__": print(model)
      mc_items_dir.joinpath("painting.json").write_text(json.dumps(model, indent=3))


def make_custom_painting_variant_cases(inputs: pd.DataFrame) -> list[dict]:
   cases = []
   for i, input in inputs.iterrows():
      p_namespace = input["_painting_namespace"] if pd.notna(input["_painting_namespace"]) else "minecraft"
      p_path = f"{input["__painting_path"]}/" if pd.notna(input["__painting_path"]) else ""
      p_case = f"{p_namespace}:{p_path}{input["painting_name"]}"

      i_path = f"{input["__item_path"]}/" if pd.notna(input["__item_path"]) else ""
      i_model = f"{input["item_namespace"]}:item/{i_path}{input["item_name"]}"

      case = {"when": p_case, "model": {"type": "minecraft:model", "model": i_model}}

      cases.append(case)
   return cases

if __name__ == "__main__":
   main()
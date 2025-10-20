from pathlib import Path
import json
import pyperclip

def main():
   requesting_input = True
   while requesting_input:
      file = Path(input("File or folder to format: "))

      if file.exists():
         if file.is_file():
            if file.suffix == ".json":
               content = json.loads(file.read_text())
               result = make_pretty_json(content)
               file.write_text(result)
               print("Done")
            else:
               print("File is not .json")

         elif file.is_dir():
            for f in file.glob("**/*.json"):
               content = json.loads(f.read_text())
               result = make_pretty_json(content)
               f.write_text(result)
            print("Done")
      
      else:
         print("Cannot find file or folder with given input")

   # pyperclip.copy(result)
   # print(result)

def make_pretty_json(val, level: int = 1, compact: bool = False, indent: int = 3) -> str:
   location = "" if compact else "\n"
   spacing = " " * (0 if compact else level * indent)
   prev_spacing = " " * (0 if compact else (level - 1) * indent)

   val_type = type(val)

   if val_type is dict:
      return f"""{{{f", ".join(f"{location}{spacing}\"{e}\": {mc_logic(e, v, level + 1, compact)}" for e, v in val.items())}{location}{prev_spacing}}}"""

   elif val_type is list:
      if all(isinstance(x, (int, float)) for x in val):
         return f"[{", ".join(map(str, val))}]"
      else:
         return f"""[{f",".join(f"{location}{spacing}{make_pretty_json(v, level + 1, compact)}" for v in val)}{location}{prev_spacing}]"""

   elif val_type is str:
      return f"\"{val}\""

   elif val_type is int or val_type is float:
      return f"{val}"
   
   else:
      return ""

def mc_logic(ele, val, l, compact, indent: int = 3) -> str:
   if ele in ["north", "south", "east", "west", "up", "down", "rotation"]:
      return make_pretty_json(val, l, True, indent)
   else:
      return make_pretty_json(val, l, compact, indent)

if __name__ == "__main__":
   main()
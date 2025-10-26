from pathlib import Path

# Fields with "__" prefix are truly optional. If "__num" is omitted, resulting order cannot be guaranteed
# Fields with "_" prefix are optional with a default (usually "minecraft")

files = {
   "_general": {
      "__num",
      "item_namespace",
      "__item_path",
      "item_name",
      "__in_game_name",
      "__minecraft_item"
   },
   "bow": {
      "__num",
      "item_namespace",
      "__item_path",
      "__item_name",
      "__in_game_name",
      "model_standby",
      "model_using_0",
      "model_using_1",
      "model_using_2"
   },
   "bundle": {
      "__num",
      "item_namespace",
      "__item_path",
      "__item_name",
      "__in_game_name",
      "model_empty",
      "model_filled"
   },
   "music_disc": {
      "__num",
      "item_namespace",
      "__item_path",
      "item_name",
      "__in_game_name"
   },
   "painting": {
      "__num",
      "item_namespace",
      "__item_path",
      "item_name",
      "_painting_namespace",
      "__painting_path",
      "painting_name"
   },
   "shield": {
      "__num",
      "item_namespace",
      "__item_path",
      "__item_name",
      "__in_game_name",
      "model_standby",
      "model_using"
   }
}

def main():
   input_dir = Path.cwd().joinpath("resource_pack_inator", "input")
   for f, cols_def in files.items():
      file = input_dir.joinpath(f"{f}.csv")
      # If the file exists, check columns from file to make sure they match definition and add any missing columns at the end
      if file.exists():
         text = file.read_text().split("\n")
         cols = text[0].split(",")
         if set(cols).difference(cols_def) == set():
            continue
         else:
            cols.extend(cols_def.difference(cols))
            text[0] = ",".join(cols)
            file.write_text("\n".join(text))
            
      # If the file doesn't exist, create a new file with columns
      else:
         file.write_text(",".join(cols_def))


if __name__ == "__main__":
   main()
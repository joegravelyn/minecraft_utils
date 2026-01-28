# Minecraft Inators

A collection of random utilities and scripts to help automate various activities related to Minecraft.

- [Resource Pack Inator](#resource-pack-inator)
- [Resource Pack Hash Inator](#resource-pack-hash-inator)
- [Model Format Inator](#model-format-inator)
- [Server Stat Inator](#server-stat-inator)
- [Screenshot Grab Inator](#screenshot-grab-inator)
<!--- - [Vanilla Inspect Inator](#vanilla-inspect-inator) --->

---

These Inators have *not* been widely tested. 
- If there are any questions or feedback, please start a discussion [here](https://github.com/joegravelyn/minecraft_utils/discussions).
- If there are any issues, please create an issue [here](https://github.com/joegravelyn/minecraft_utils/issues). 

---

## Resource Pack Inator

*more info coming soon*

#### Prep Scripts
- **`create_model_stubs`**: provided a resource pack asset folder, checks the `texture` folder of all namespaces and creates basic item model files in the output folder under the respective namespace folder
- **`create_painting_list`**: provided a resource pack asset folder, checks the `texture/painting` folder of all namespaces and saves a list of all painting textures in the input folder as `__generated_painting.csv`
- **`create_input_file_stubs`**: creates any missing input files and adds any missing columns to existing files
- **`create_working_list`**: 

#### Input Files

*more info coming soon*

#### Main Inator

*more info coming soon*

#### Output

*more info coming soon*


## Resource Pack Hash Inator

Prints the sha1 hash for a provided resource pack zip file. This is the hash required for the `resource-pack-sha1` field in `server.properties`.


## Model Format Inator

Applies custom formatting to model json files. Works on an individual file or will apply to all json files in a folder (including subfolders).

<details>
<summary>Sample of formatted file</summary>

```json
{
   "texture_size": [48, 32],
   "textures": {
      "0": "tps:item/winter_hat",
      "particle": "tps:item/winter_hat"
   },
   "elements": [
      {
         "from": [2, 5, 3],
         "to": [14, 10, 13],
         "rotation": {"angle": 0, "axis": "y", "origin": [8, 5, 6]},
         "faces": {
            "north": {"uv": [3.33333, 5, 7.33333, 7.5], "texture": "#0"},
            "east": {"uv": [4, 12.5, 7.33333, 15], "texture": "#0"},
            "south": {"uv": [0, 12.5, 4, 15], "texture": "#0"},
            "west": {"uv": [7.33333, 12.5, 4, 15], "texture": "#0"},
            "up": {"uv": [3.33333, 0, 7.33333, 5], "texture": "#0"},
            "down": {"uv": [3.33333, 7.5, 7.33333, 12.5], "texture": "#0"}
         }
      },
      ...
      {
         "from": [2.816, 0.864, 12.4],
         "to": [13.184, 2.784, 14.128],
         "rotation": {"angle": 0, "axis": "y", "origin": [2.816, 1.824, 12.416]},
         "faces": {
            "north": {"uv": [11.33333, 14, 15.33333, 15], "texture": "#0"},
            "east": {"uv": [15.33333, 12, 16, 13], "texture": "#0"},
            "south": {"uv": [11.33333, 12, 15.33333, 13], "texture": "#0"},
            "west": {"uv": [10.66667, 12, 11.33333, 13], "texture": "#0"},
            "up": {"uv": [11.33333, 11, 15.33333, 12], "texture": "#0"},
            "down": {"uv": [11.33333, 13, 15.33333, 14], "texture": "#0"}
         }
      }
   ],
   "gui_light": "front",
   "display": {
      "thirdperson_righthand": {
         "rotation": [71.47, -2.31, -14.35],
         "translation": [0, 0.5, -1.5],
         "scale": [0.8, 0.8, 0.8]
      },
      ...
      "fixed": {
         "rotation": [-25.25, 0, 0],
         "translation": [0.5, 6.25, -8.5],
         "scale": [1.6, 1.6, 1.6]
      }
   },
   "groups": [
      {
         "name": "group",
         "origin": [8, 8, 8],
         "color": 0,
         "children": [
            0,
            1,
            2,
            {
               "name": "group",
               "origin": [8, 4.5, 6.5],
               "color": 0,
               "children": [3, 4, 5, 6, 7]
            }
         ]
      }
   ]
}
```
</details>


## Server Stat Inator

Uses SFTP to connect to a Minecraft server and reads user stat csv files. Uses previously recorded stats to determine and save deltas to a local csv file.

Copy `config_template.json` and rename to `config.json`. Inside the config file:
- Set server connection, port, username, and password
- Provide directory to `world/stats` folder
- Set the output directory where stat delta csv files are saved

``` json
   "host": "",
   "port": 0,
   "user": "",
   "pass": "",
   "stats_dir": "",
   "out": ""
```

## Screenshot Grab Inator

Copies screenshots from Java and Bedrock directories, into a single location. Renames all pictures to be consistent format based on their creation time. If multiple, unique* pictures are taken within the same second, file names will be suffixed with `_1, _2, etc`.

\* Uniquness is determined by hashing the image.

Copy `config_template.json` and rename to `config.json`. Inside the config file:
- Set the target directory (where the screenshot copies will go)
- Set if the Bedrock and vanilla Java locations will be searched
- Provide a list of other Java installs (**Note:** this has only been tested with Modrinth instances. Please create a new issue if there are problems with other launchers)

``` json
   "target_dir": "", 
   "bedrock": false,
   "java": false,
   "other_java_installs": []
```


<!--- ## Vanilla Inspect Inator --->

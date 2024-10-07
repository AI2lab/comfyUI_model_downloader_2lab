import json
import os
from pathlib import Path
import configparser


# PATH
comfyUI_root = Path(__file__).parent.parent.parent.parent
comfyUI_models_root = os.path.join(comfyUI_root,"models")
custom_nodes_root = Path(__file__).parent.parent.parent
project_root = Path(__file__).parent.parent
# models
configs_folder = os.path.join(project_root, 'configs')
model_file = os.path.join(configs_folder, 'model.json')

models = {}
if os.path.exists(model_file):
    with open(model_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            models[item['custom_node']] = item

auto_download_model = False
china_mirror = False
model_folder = comfyUI_models_root

# read config from 2lab.ini
file_path = os.path.join(project_root, "2lab.ini")
# print("file_path ini = ", file_path)
if os.path.exists(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    auto_download_model = config.get("download_models", "auto_download_model", fallback=False)
    china_mirror = config.get("download_models", "china_mirror", fallback=True)
    model_folder = config.get("download_models", "model_folder", fallback=comfyUI_models_root)



import filecmp
import shutil
import os
import sys
import __main__
import importlib.util
import server
from aiohttp import web
from .nodes.constants import PROJECT_NAME, project_root, auto_download_model, javascript_folder, asset_folder

from .nodes.utils import download_model, print_console

python = sys.executable

print_console("[comfyUI_model_downloader_2lab] start")

# 如果config中指定自动下载模型，则执行下载
download_model('')

print_console("[comfyUI_model_downloader_2lab] finished")
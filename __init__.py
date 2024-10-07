

import sys

from .nodes.constants import auto_download_model
from .nodes.utils import download_model,print_console

python = sys.executable

print_console("[comfyUI_model_downloader_2lab] start")

# 如果config中指定自动下载模型，则执行下载
if auto_download_model:
    download_model('')

print_console("[comfyUI_model_downloader_2lab] finished")


NODE_CLASS_MAPPINGS = {
}

# display name
NODE_DISPLAY_NAME_MAPPINGS = {
}

__all__ = [NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS]

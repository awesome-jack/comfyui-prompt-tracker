"""
ComfyUI Prompt Tracker Node
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .nodes import (
        PromptTrackerUpload,
        PromptTrackerDownload,
        PromptTrackerSelect,
        PromptTrackerList,
    )

    NODE_CLASS_MAPPINGS = {
        "PromptTrackerUpload": PromptTrackerUpload,
        "PromptTrackerDownload": PromptTrackerDownload,
        "PromptTrackerSelect": PromptTrackerSelect,
        "PromptTrackerList": PromptTrackerList,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "PromptTrackerUpload": "Prompt Tracker 上传",
        "PromptTrackerDownload": "Prompt Tracker 下载",
        "PromptTrackerSelect": "Prompt Tracker 选择",
        "PromptTrackerList": "Prompt Tracker 列表",
    }

    print("\033[92m[Prompt Tracker] 节点加载成功!\033[0m")
    print("\033[92m[Prompt Tracker] 可用节点: Prompt Tracker 上传, Prompt Tracker 下载, Prompt Tracker 选择, Prompt Tracker 列表\033[0m")

except Exception as e:
    print(f"\033[91m[Prompt Tracker] 节点加载失败: {e}\033[0m")
    import traceback
    traceback.print_exc()
    
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

WEB_DIRECTORY = None

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

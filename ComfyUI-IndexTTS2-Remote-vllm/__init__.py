# 目录结构：
# custom_nodes/tts_request/
# ├── __init__.py
# └── tts_request_node.py

# __init__.py 文件内容：
from .tts_request_node import TTSRequest

NODE_CLASS_MAPPINGS = {
    "TTSRequest": TTSRequest
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TTSRequest": "TTS Request"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
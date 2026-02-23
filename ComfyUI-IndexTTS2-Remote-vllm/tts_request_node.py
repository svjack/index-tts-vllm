# tts_request_node.py 文件内容：
import os
import requests
import json
import folder_paths

class TTSRequest:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"default": "这是一段王翔和小白猫的故事，王翔非常喜欢小白猫。", "multiline": True}),
                "spk_audio_path": ("STRING", {"default": "王翔音频.wav"}),
                "emo_control_method": ("INT", {"default": 0, "min": 0, "max": 2}),
                "emo_weight": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_text_tokens_per_sentence": ("INT", {"default": 120, "min": 1, "max": 200}),
                "server_url": ("STRING", {"default": "http://10.50.3.7:6006/tts_url"}),
                "output_filename": ("STRING", {"default": "output.wav"}),
            },
            "optional": {
                "emo_vec": ("STRING", {"default": "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"}),
            }
        }

    RETURN_TYPES = ("STRING",)  # 返回音频文件路径
    RETURN_NAMES = ("audio_path",)
    FUNCTION = "generate_audio"
    CATEGORY = "audio/tts"

    def generate_audio(self, text, spk_audio_path, emo_control_method, emo_weight, max_text_tokens_per_sentence, server_url, output_filename, emo_vec="[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"):
        try:
            # Parse emotion vector
            emo_vec_parsed = json.loads(emo_vec)
            
            # Prepare request data
            data = {
                "text": text,
                "spk_audio_path": spk_audio_path,
                "emo_control_method": emo_control_method,
                "emo_weight": emo_weight,
                "emo_vec": emo_vec_parsed,
                "max_text_tokens_per_sentence": max_text_tokens_per_sentence
            }
            
            # Make POST request
            response = requests.post(server_url, json=data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            
            # 确定输出目录
            output_dir = folder_paths.get_output_directory()
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成唯一文件名
            if not output_filename.endswith('.wav'):
                output_filename += '.wav'
            
            # 确保文件名唯一
            counter = 1
            original_filename = output_filename
            while os.path.exists(os.path.join(output_dir, output_filename)):
                name, ext = os.path.splitext(original_filename)
                output_filename = f"{name}_{counter:05d}{ext}"
                counter += 1
            
            output_path = os.path.join(output_dir, output_filename)
            
            # 保存音频文件
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Audio saved to: {output_path}")
            
            return (output_path,)
            
        except Exception as e:
            print(f"Error in TTS request: {e}")
            # 返回空路径
            return ("",)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "TTSRequest": TTSRequest
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TTSRequest": "TTS Request (File Output)"
}
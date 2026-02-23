根据您提供的链接内容和问题描述，我理解您需要了解如何部署和使用IndexTTS-2-vLLM模型。以下是完整的操作步骤：

## 环境准备与模型部署

1. **克隆仓库**：
   ```bash
   git clone https://github.com/svjack/index-tts-vllm.git
   cd index-tts-vllm
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   pip install "transformers<5"
   pip install -U protobuf
   ```

3. **下载模型**：
   ```bash
   modelscope download --model kusuriuri/IndexTTS-2-vLLM --local_dir ./checkpoints/IndexTTS-2-vLLM
   ```

4. **启动API服务**：
   ```bash
   python api_server_v2.py --model_dir "./checkpoints/IndexTTS-2-vLLM"
   ```

## 使用说明

**音频文件准备**：
- 将参考音频文件（如"王翔音频.wav"）放置在工程根目录下

**API调用示例**：
```bash
curl -X POST "http://10.50.3.7:6006/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一段王翔和小白猫的故事，王翔非常喜欢小白猫。",
    "spk_audio_path": "王翔音频.wav",
    "emo_control_method": 0,
    "emo_weight": 1.0,
    "emo_vec": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "max_text_tokens_per_sentence": 120
  }' \
  --output output.wav
```

**Comfyui 使用**：
```bash
git clone https://github.com/svjack/index-tts-vllm
cp -r index-tts-vllm/ComfyUI-IndexTTS2-Remote-vllm ComfyUI/custom_nodes
# 使用工作流 indextts2-remote-vllm.json
```


## 注意事项
- 请将API地址中的`http://10.50.3.7:6006/generate`替换为实际的服务地址 （0.0.0.0：6006 或 ifconfig 内网服务器地址）
- 确保参考音频文件存在且可访问
- 情感控制参数可根据需要调整
- 输出文件将保存为output.wav

如果您需要生成英文README文件，请提供更多具体需求信息。

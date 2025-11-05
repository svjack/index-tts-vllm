'''
python run_api_iter.py 怪盗弗拉努尔的巡回\(怪盗系列\)\ -\ 西尾维新\ -\ 20230508 怪盗弗拉努尔的巡回\(怪盗系列\)\ -\ 西尾维新\ -\ 20230508_wav
'''

from dataclasses import asdict, dataclass
import os
from typing import List, Optional
import requests
from pathlib import Path
import argparse
import time
from pydub import AudioSegment
import re

SERVER_PORT = 6006
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

url = f"http://localhost:{SERVER_PORT}/tts_url"

@dataclass
class IndexTTS2RequestData:
    text: str
    spk_audio_path: str
    emo_control_method: int = 0
    emo_ref_path: Optional[str] = None
    emo_weight: float = 1.0
    emo_vec: List[float] = None
    emo_text: Optional[str] = None
    emo_random: bool = False
    max_text_tokens_per_sentence: int = 120

    def __post_init__(self):
        # 保证 emo_vec 默认长度为 8 的 0 向量
        if self.emo_vec is None:
            self.emo_vec = [0.0] * 8

    def to_dict(self) -> dict:
        return asdict(self)

def clean_text(text):
    """清理单行文本，只保留中英文逗号、句号和问号，并去除所有空格"""
    pattern = r'[^\w\s,，.。？?]'
    cleaned_text = re.sub(pattern, '', text)
    cleaned_text = re.sub(r'\s+', '', cleaned_text)
    return cleaned_text

def split_text(text, lines_per_chunk=10):
    """先将文本按行分割，然后对每一行进行清理，最后每若干行合并为一个段落"""
    lines = text.split('\n')
    cleaned_lines = [clean_text(line) for line in lines if line.strip()]
    
    chunks = []
    for i in range(0, len(cleaned_lines), lines_per_chunk):
        chunk = ''.join(cleaned_lines[i:i+lines_per_chunk])
        chunk = re.sub(r'。+', '。', chunk)
        chunk = re.sub(r'\s+', '', chunk)
        chunks.append(chunk)
    
    return chunks

def generate_audio_index_tts2(api_url, text, spk_audio_path, output_path):
    """调用IndexTTS2 API生成音频"""
    data = IndexTTS2RequestData(
        text=text,
        spk_audio_path=spk_audio_path
    )
    
    try:
        response = requests.post(api_url, json=data.to_dict())
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ 请求失败: {e}")
        return False

def merge_audio_files(audio_files, output_path, sort_by_number=True):
    """
    合并多个音频文件为一个文件 [1,3](@ref)
    
    Args:
        audio_files: 音频文件路径列表
        output_path: 合并后的输出路径
        sort_by_number: 是否按文件名中的数字排序 [1](@ref)
    """
    if not audio_files:
        print("⚠️ 没有音频文件可合并")
        return False
    
    # 按文件名排序 [1](@ref)
    if sort_by_number:
        try:
            # 尝试按文件名中的数字排序（适用于 part1.wav, part2.wav 等格式）
            audio_files.sort(key=lambda x: int(''.join(filter(str.isdigit, Path(x).stem))))
        except:
            # 如果数字提取失败，使用字母排序
            audio_files.sort()
    
    print(f"合并 {len(audio_files)} 个音频文件...")
    
    try:
        # 使用pydub合并音频 [3](@ref)
        combined_audio = AudioSegment.empty()
        
        for i, audio_file in enumerate(audio_files):
            print(f"合并进度: {i+1}/{len(audio_files)} - {Path(audio_file).name}")
            segment = AudioSegment.from_wav(audio_file)
            combined_audio += segment
        
        # 导出合并后的音频 [3](@ref)
        combined_audio.export(output_path, format="wav")
        print(f"✓ 音频合并完成! 总时长: {len(combined_audio)/1000:.2f}秒")
        return True
        
    except Exception as e:
        print(f"✗ 音频合并失败: {e}")
        return False

def process_txt_file(txt_path, output_dir, api_url, spk_audio_path, lines_per_chunk=10, merge_final=True):
    """处理单个txt文件并生成合并音频"""
    print(f"\n处理文件: {txt_path}")
    
    # 读取文本文件
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(txt_path, 'r', encoding='gbk') as f:
                text = f.read()
        except Exception as e:
            print(f"✗ 无法读取文件 {txt_path}: {e}")
            return
    
    print(f"原始文本长度: {len(text)} 字符")
    
    # 分割文本为指定行数一段
    text_chunks = split_text(text, lines_per_chunk)
    print(f"分割为 {len(text_chunks)} 个段落")
    
    if len(text_chunks) == 0:
        print("⚠️ 警告: 文本分割后没有有效内容")
        return
    
    # 创建临时目录存储分段音频
    temp_dir = Path(output_dir) / "temp_parts"
    temp_dir.mkdir(exist_ok=True)
    
    part_files = []
    successful_chunks = 0
    
    for i, chunk in enumerate(text_chunks):
        if not chunk.strip():
            continue
            
        print(f"\n生成第 {i+1}/{len(text_chunks)} 段音频...")
        print(f"段落内容预览: {chunk[:80]}..." if len(chunk) > 80 else f"段落内容: {chunk}")
        
        # 生成分段音频文件名
        part_filename = f"{txt_path.stem}_part{i+1:03d}.wav"
        part_path = temp_dir / part_filename
        
        # 生成音频
        success = generate_audio_index_tts2(api_url, chunk, spk_audio_path, part_path)
        
        if success:
            part_files.append(part_path)
            successful_chunks += 1
            print(f"✓ 第 {i+1} 段音频生成成功")
        else:
            print(f"✗ 第 {i+1} 段音频生成失败")
        
        time.sleep(1)  # 避免服务器过载
    
    # 合并所有分段音频 [1,3](@ref)
    if merge_final and part_files:
        print(f"\n开始合并 {len(part_files)} 个音频片段...")
        final_output_path = Path(output_dir) / f"{txt_path.stem}.wav"
        
        if merge_audio_files(part_files, final_output_path):
            print(f"✓ 最终合并音频保存到: {final_output_path}")
            
            # 清理临时文件
            if temp_dir.exists():
                for temp_file in temp_dir.glob("*.wav"):
                    temp_file.unlink()
                temp_dir.rmdir()
        else:
            print("✗ 音频合并失败，保留分段文件")
    
    print(f"\n✓ 文件处理完成! 成功生成 {successful_chunks}/{len(text_chunks)} 段音频")

def main():
    parser = argparse.ArgumentParser(description='批量处理txt文件生成音频（IndexTTS2版本）')
    parser.add_argument('--input_dir', type=str, required=True, 
                       help='包含txt文件的输入目录')
    parser.add_argument('--output_dir', type=str, required=True, 
                       help='输出wav文件的目录')
    parser.add_argument('--server_port', type=int, default=SERVER_PORT,
                       help='IndexTTS2服务器端口（默认：6006）')
    parser.add_argument('--spk_audio', type=str, default="类王翔音频_vocals.wav", 
                       help='说话人音频文件路径')
    parser.add_argument('--lines_per_chunk', type=int, default=10,
                       help='每个音频段落的行数（默认：10）')
    parser.add_argument('--no_merge', action='store_true',
                       help='不合并最终音频，保留分段文件')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"错误: 输入目录 {input_dir} 不存在")
        return
    
    if not Path(args.spk_audio).exists():
        print(f"错误: 说话人音频文件 {args.spk_audio} 不存在")
        return
    
    api_url = f"http://localhost:{args.server_port}/tts_url"
    
    txt_files = list(input_dir.glob('*.txt'))
    print(f"找到 {len(txt_files)} 个txt文件")
    
    if len(txt_files) == 0:
        print(f"在目录 {input_dir} 中未找到txt文件")
        return
    
    total_start_time = time.time()
    
    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n{'='*60}")
        print(f"处理进度: {i}/{len(txt_files)} - {txt_file.name}")
        print(f"{'='*60}")
        
        file_start_time = time.time()
        process_txt_file(txt_file, output_dir, api_url, 
                        args.spk_audio, args.lines_per_chunk, not args.no_merge)
        file_time = time.time() - file_start_time
        print(f"文件处理时间: {file_time:.2f}秒")
    
    total_time = time.time() - total_start_time
    print(f"\n{'='*60}")
    print(f"所有文件处理完成!")
    print(f"总处理时间: {total_time:.2f}秒")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
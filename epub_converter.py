'''
# 基本用法：转换为单个文件，自动去重
python epub_converter.py input.epub output.txt

# 分割为多个文件（每64行一个文件）
python epub_converter.py input.epub output_dir --lines 64

# 保留相邻重复行
python epub_converter.py input.epub output.txt --keep-duplicates

# 不分割文件（生成单个TXT）
python epub_converter.py input.epub output.txt --lines 0

python epub_converter.py xxxHOLiC\ -\ 西尾维新\ -\ 20090318.epub xxxHOLiC\ -\ 西尾维新\ -\ 20090318.txt

python epub_converter.py xxxHOLiC\ -\ 西尾维新\ -\ 20090318.epub xxxHOLiC\ -\ 西尾维新\ -\ 20090318 --lines 64
'''

import os
import re
from pathlib import Path
from ebooklib import epub
import ebooklib  # 正确导入 ITEM_DOCUMENT 的模块
from bs4 import BeautifulSoup
import argparse

def convert_epub_to_txt(epub_path, output_path, lines_per_file=64, remove_adjacent_duplicates=True):
    """
    将EPUB文件转换为TXT文件，支持相邻行去重和按行数分割。

    Args:
        epub_path (str): 输入的EPUB文件路径。
        output_path (str): 输出的TXT文件路径或目录路径。
        lines_per_file (int, optional): 每个分割文件包含的行数。默认为64。如果为0，则输出单个文件。
        remove_adjacent_duplicates (bool, optional): 是否移除相邻的重复行。默认为True。
    """
    try:
        # 读取EPUB文件
        book = epub.read_epub(epub_path)
        all_lines = []  # 用于存储提取出的所有文本行

        # 遍历EPUB中的所有项目
        for item in book.get_items():
            # 修正：使用 ebooklib.ITEM_DOCUMENT 而不是 ebooklib.epub.ITEM_DOCUMENT
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # 使用BeautifulSoup解析HTML内容，提取纯文本
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                text = soup.get_text()

                # 按行分割，并清理每一行的空白字符
                lines = text.splitlines()
                cleaned_lines = [line.strip() for line in lines if line.strip()]
                all_lines.extend(cleaned_lines)

        if not all_lines:
            print("警告: 未从EPUB文件中提取到任何文本内容。")
            return False

        # 处理相邻重复行
        if remove_adjacent_duplicates:
            unique_lines = []
            previous_line = None
            for line in all_lines:
                if line != previous_line:  # 只保留与上一行不同的行
                    unique_lines.append(line)
                    previous_line = line
            all_lines = unique_lines
            print(f"相邻去重后，总行数: {len(all_lines)}")

        # 确定输出模式并保存
        output_dir = Path(output_path)
        if lines_per_file > 0 and len(all_lines) > lines_per_file:
            # 模式1：分割成多个文件
            output_dir.mkdir(parents=True, exist_ok=True)
            return _save_split_files(all_lines, output_dir, lines_per_file)
        else:
            # 模式2：保存为单个文件
            output_dir.parent.mkdir(parents=True, exist_ok=True)
            return _save_single_file(all_lines, output_dir)

    except Exception as e:
        print(f"处理EPUB文件时出错: {e}")
        return False

def _save_single_file(lines, output_path):
    """将所有行保存到单个TXT文件中。"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')
        print(f"✓ 已生成单个TXT文件: {output_path}")
        print(f"✓ 文件总行数: {len(lines)}")
        return True
    except Exception as e:
        print(f"保存单个文件时出错: {e}")
        return False

def _save_split_files(lines, output_dir, lines_per_file):
    """将行列表按指定行数分割，并保存为多个编号的TXT文件。"""
    try:
        total_files = (len(lines) + lines_per_file - 1) // lines_per_file
        files_created = 0

        for i in range(0, len(lines), lines_per_file):
            chunk = lines[i:i + lines_per_file]
            file_number = str(files_created).zfill(6)  # 生成如 000001 的编号
            filename = f"{file_number}.txt"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                for line in chunk:
                    f.write(line + '\n')

            files_created += 1
            print(f"✓ 生成分割文件: {filepath} (包含 {len(chunk)} 行)")

        print(f"✓ 分割完成! 共生成 {files_created} 个文件到目录 {output_dir}")
        print(f"✓ 所有文件总行数: {len(lines)}")
        return True

    except Exception as e:
        print(f"分割文件时出错: {e}")
        return False

def main():
    """主函数，处理命令行参数并执行转换。"""
    parser = argparse.ArgumentParser(description='将EPUB文件转换为TXT文件，支持去重和分割。')
    parser.add_argument('input_epub', help='输入的EPUB文件路径')
    parser.add_argument('output_path', help='输出的TXT文件路径（若不分割）或存放分割文件的目录路径')
    parser.add_argument('--lines', type=int, default=64,
                       help='每个分割文件的行数。设置为0则输出单个TXT文件。默认: 64')
    parser.add_argument('--keep-duplicates', action='store_true',
                       help='使用此选项将保留相邻的重复行，默认行为是去除相邻重复行。')

    args = parser.parse_args()

    input_path = Path(args.input_epub)
    if not input_path.exists():
        print(f"错误: 输入的EPUB文件不存在: {args.input_epub}")
        return

    # 执行转换
    success = convert_epub_to_txt(
        epub_path=args.input_epub,
        output_path=args.output_path,
        lines_per_file=args.lines,
        remove_adjacent_duplicates=not args.keep_duplicates  # 命令行选项与函数参数逻辑相反
    )

    if success:
        print("✨ 转换成功完成！")
    else:
        print("❌ 转换过程中出现问题。")

if __name__ == "__main__":
    main()
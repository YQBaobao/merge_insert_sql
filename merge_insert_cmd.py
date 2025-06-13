# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : tools
@ File        : merge_insert_cmd.py
@ Author      : yqbao
@ version     : V1.0.0
@ Description : 合并 SQL INSERT 支持标准 INSERT 和带字段版本，支持命令行文件/目录参数
"""
import argparse
import re
import os


def read_file_with_encoding(file_path):
    try:
        # 优先尝试 utf-8
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # 回退使用 utf-16le
            with open(file_path, 'r', encoding='utf-16le') as f:
                return f.read()
        except Exception as e:
            print(f"文件无法读取: {file_path}\n错误: {e}")
            return None


def merge_insert_statements_in_file(file_path, output_folder):
    content = read_file_with_encoding(file_path)
    if content is None:
        return

    # 强化支持带字段、跨行 INSERT INTO
    insert_pattern = re.compile(
        r'INSERT INTO\s+'
        r'(?:(`(?P<schema>[^`]+)`|(?P<schema2>\w+))\.)?'
        r'(`(?P<table1>[^`]+)`|(?P<table2>\w+))\s*'
        r'(?P<fields>\([^;]+?\))?\s*VALUES\s*\((?P<values>.*?)\);',
        re.IGNORECASE | re.DOTALL
    )

    all_matches = list(insert_pattern.finditer(content))
    if not all_matches:
        file_name: str = os.path.basename(file_path)
        output_path = os.path.join(output_folder, file_name.replace('.sql', '_merged.sql'))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"跳过（无有效 INSERT），已保存原始：{output_path}")
        return

    # 提取参数
    first = all_matches[0]
    table_name = first.group('table1') or first.group('table2')
    field_block = first.group('fields') or ''
    values = [m.group('values') for m in all_matches]

    merged_insert = f"INSERT INTO `{table_name}` {field_block} VALUES\n" + ",\n".join(f"({v})" for v in values) + ";\n"

    # 删除所有 INSERT 语句（避免空行问题）
    new_parts = []
    last_end = 0
    for m in all_matches:
        new_parts.append(content[last_end:m.start()])
        last_end = m.end()
    new_parts.append(content[last_end:])
    cleaned_content = ''.join(new_parts)

    # 插入新 INSERT 到 FOREIGN_KEY_CHECKS = 1; 前
    fk_match = re.search(r'SET FOREIGN_KEY_CHECKS\s*=\s*1\s*;', cleaned_content, re.IGNORECASE)
    if fk_match:
        insert_pos = fk_match.start()
        final_content = (
                cleaned_content[:insert_pos].rstrip() +
                "\n\n-- 合并后的 INSERT 语句\n" +
                merged_insert +
                "\n\n" +
                cleaned_content[insert_pos:]
        )
    else:
        final_content = cleaned_content + "\n\n-- 合并后的 INSERT 语句\n" + merged_insert

    # 保存文件
    os.makedirs(output_folder, exist_ok=True)
    file_name = os.path.basename(file_path)
    output_path = os.path.join(output_folder, file_name.replace('.sql', '_merged.sql'))
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"已处理：{file_path} → {output_path}")


def process_path(path, output_folder='merged_sql'):
    if os.path.isfile(path) and path.lower().endswith('.sql'):
        merge_insert_statements_in_file(path, output_folder)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path) and file.lower().endswith('.sql'):
                merge_insert_statements_in_file(full_path, output_folder)
    else:
        print(f"❌ 无效路径或不支持的文件类型：{path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="将多个 INSERT INTO 合并为一条 SQL 插入语句")
    parser.add_argument('path', help="SQL 文件路径或文件夹路径")
    parser.add_argument('-o', '--output', default='merged_sql', help="输出文件夹（默认：merged_sql）")

    args = parser.parse_args()
    process_path(args.path, args.output)

# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : tools
@ File        : merge_insert_gui.py
@ Author      : yqbao
@ version     : V1.1.0
@ Description : 合并 SQL INSERT 支持标准 INSERT 和带字段版本，GUI版本
"""
import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt


def read_file_with_encoding(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='utf-16le') as f:
            return f.read()
    except Exception as e:
        print(f"文件无法读取: {file_path}\n错误: {e}")
        return None


def merge_insert_statements_in_file(file_path, output_folder, log_callback=None):
    content = read_file_with_encoding(file_path)
    if content is None:
        return

    # 正则表达式
    insert_pattern = re.compile(
        r'INSERT INTO\s+'
        r'(?:(`(?P<schema>[^`]+)`|(?P<schema2>\w+))\.)?'
        r'(`(?P<table1>[^`]+)`|(?P<table2>\w+))\s*'
        r'(?P<fields>\([^;]+?\))?\s*VALUES\s*\((?P<values>.*?)\);',
        re.IGNORECASE | re.DOTALL
    )
    all_matches = list(insert_pattern.finditer(content))
    if not all_matches:
        write_output(file_path, output_folder, content)
        if log_callback:
            log_callback(f"跳过（无 INSERT）,已直接保存原文件：{file_path}")
        return

    # 提取参数
    table_name = all_matches[0].group('table1') or all_matches[0].group('table2')
    field_block = all_matches[0].group('fields') or ''
    values_list = [m.group('values') for m in all_matches]

    merged_insert = f"INSERT INTO `{table_name}` {field_block} VALUES\n" + ",\n".join(
        f"({v})" for v in values_list) + ";\n"

    # 删除所有 INSERT 语句
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

    write_output(file_path, output_folder, final_content)
    if log_callback:
        log_callback(f"处理完成：{file_path}")


def write_output(file_path, output_folder, content):
    os.makedirs(output_folder, exist_ok=True)
    file_name = os.path.basename(file_path).replace('.sql', '_merged.sql')
    output_path = os.path.join(output_folder, file_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def process_path(path, output_folder, log_callback=None):
    if os.path.isfile(path) and path.lower().endswith('.sql'):
        merge_insert_statements_in_file(path, output_folder, log_callback)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path) and file.lower().endswith('.sql'):
                merge_insert_statements_in_file(full_path, output_folder, log_callback)


class MergeInsertGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL INSERT 合并工具")
        self.resize(640, 240)
        self.setAcceptDrops(True)

        self.output_folder = os.path.join(os.getcwd(), "merged_sql")

        layout = QVBoxLayout()
        self.label = QLabel("请将 .SQL文件 或 文件夹 拖入此窗口")
        self.label.setAlignment(Qt.AlignCenter)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        for path in paths:
            process_path(path, self.output_folder, self.append_log)

    def append_log(self, message):
        self.text_edit.append(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MergeInsertGUI()
    gui.show()
    sys.exit(app.exec_())

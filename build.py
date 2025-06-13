#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : tools
@ File        : build.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description :
"""
import os
from PyInstaller.__main__ import run

dir_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    opts = [
        'merge_insert_cmd.py',
        '--name=merge_insert',
        # 'merge_insert_gui.py',
        # '--name=merge_insert_gui',
        '-F',
        '-w',
        '-y',
        '-p .',
        '--clean',
        # '--noupx',  # 不使用upx,即使可用
        '--upx-exclude=api-ms-win-core*.dll',
        '--upx-exclude=python3.dll',
        '--upx-exclude=_uuid.pyd',
        '--upx-exclude=WinDivert32.sys',
        '--upx-exclude=WinDivert64.sys',
    ]

    run(opts)

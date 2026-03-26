# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# 添加数据文件
datas = [
    ('thonny', 'thonny'),
    ('plugins', 'plugins'),
    ('res', 'res'),
    ('locale', 'locale'),
    ('data', 'data'),
    ('licenses', 'licenses'),
]

# 添加二进制文件
binaries = []

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'thonny.main',
        'thonny.workbench',
        'thonny.shell',
        'thonny.shell_threading',
        'thonny.threading_utils',
        'thonny.codeview',
        'thonny.editors',
        'thonny.ui_utils',
        'thonny.tktextext',
        'thonny.lsp_proxy',
        'thonny.lsp_types',
        'thonny.plugins',
        'thonny.plugins.chat',
        'thonny.plugins.glass_ui_themes',
        'thonny.plugins.calltip',
        'thonny.plugins.coloring',
        'thonny.plugins.debugger',
        'thonny.plugins.files',
        'thonny.plugins.heap',
        'thonny.plugins.notes',
        'thonny.plugins.outline',
        'thonny.plugins.pip_gui',
        'thonny.plugins.problems',
        'thonny.plugins.pyright',
        'thonny.plugins.ruff',
        'thonny.plugins.replayer',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BBCode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='res/bbc.ico',
)

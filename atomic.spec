# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['todo_app.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\venv\\Lib\\site-packages\\PySide6\\plugins\\platforms', 'PySide6\\plugins\\platforms'), ('atom.ico', '.')],
    hiddenimports=['PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtCharts'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='atomic',
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
    icon=['atom.ico'],
)

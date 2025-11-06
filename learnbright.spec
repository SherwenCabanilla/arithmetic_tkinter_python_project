# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),           # Include all assets (images, icons)
        ('data', 'data'),               # Include data folder with highscores.json
        ('app', 'app'),                 # Include all app code and .kv files
    ],
    hiddenimports=[
        'kivy',
        'kivy.core.window',
        'kivy.core.text',
        'kivy.core.image',
        'kivy.uix.screenmanager',
        'kivy.uix.boxlayout',
        'kivy.uix.label',
        'kivy.uix.button',
        'kivy.uix.image',
        'kivy.uix.textinput',
        'kivy.uix.scrollview',
        'kivy.uix.gridlayout',
        'kivy.uix.anchorlayout',
        'kivy.uix.popup',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='LearnBright Math',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                      # No console window - clean app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


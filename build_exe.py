"""
Build configuration for auto-py-to-exe
Run: auto-py-to-exe
Then load this configuration
"""

config = {
    "version": "auto-py-to-exe-configuration_v1",
    "pyinstallerOptions": [
        {
            "optionDest": "filenames",
            "value": "src/main.py"
        },
        {
            "optionDest": "onefile",
            "value": True
        },
        {
            "optionDest": "console",
            "value": False
        },
        {
            "optionDest": "name",
            "value": "MBOXEmailViewer"
        },
        {
            "optionDest": "icon_file",
            "value": "assets/icon.ico"
        },
        {
            "optionDest": "distpath",
            "value": "./dist"
        },
        {
            "optionDest": "workpath",
            "value": "./build"
        },
        {
            "optionDest": "clean",
            "value": True
        },
        {
            "optionDest": "noconfirm",
            "value": True
        },
        {
            "optionDest": "windowed",
            "value": True
        },
        {
            "optionDest": "hiddenimports",
            "value": "email.mime.multipart,email.mime.text,email.mime.base"
        }
    ],
    "nonPyinstallerOptions": {
        "increaseRecursionLimit": True,
        "outputDirectory": "./output"
    }
}

# Alternatively, use this spec file for manual PyInstaller:
SPEC_TEMPLATE = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),
    ],
    hiddenimports=[
        'email.mime.multipart',
        'email.mime.text',
        'email.mime.base',
        'pandas',
        'openpyxl',
        'xlsxwriter'
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
    name='MBOXEmailViewer',
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
    icon='assets/icon.ico'
)
"""
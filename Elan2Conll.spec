# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Elan2Conll.py'],
    pathex=['.'],  # Chemin vers votre script
    binaries=[],
    datas=[],
    hiddenimports=[
        'wx', 'wx.adv','wx._core', 'wx.html', 'wx.lib.pubsub'
    ],
    hookspath=[],
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
    [],
    exclude_binaries=True,
    name='Elan2Conll',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mettre à False pour une application GUI sans console
    #icon='icon.ico'  # Chemin vers votre icône si nécessaire
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MonProgramme',
)

# -*- mode: python ; coding: utf-8 -*-
import shutil
import sys
import os

block_cipher = None

 
 
a = Analysis(['main.py'],
             pathex=['/media/migoya/01D4A94738F92050/PROJECTS-2021/pywebviewBet365app'],
             binaries=[],
             datas =[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += Tree('./assets', prefix='assets')
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='bet365golfnotifyme',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None ,
          icon='./golf.png')

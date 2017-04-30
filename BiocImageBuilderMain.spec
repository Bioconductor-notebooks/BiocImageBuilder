# -*- mode: python -*-

block_cipher = None


a = Analysis(['BiocImageBuilderMain.py'],
             pathex=['/Library/Frameworks/Python.framework/Versions/3.5', '/Users/Jimmy/Developer/bioinfomatics/BiocImageBuilder'],
             binaries=[],
             datas=[('DockerFiles/*.Dockerfile', 'DockerFiles'),
                    ('icons/*.png', 'icons')],
             hiddenimports=['queue'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BiocImageBuilderMain',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='BiocImageBuilderMain')
app = BUNDLE(coll,
             name='Docker Image Builder.app',
             icon='biocbuilder.icns',
             bundle_identifier=None, 
             info_plist={
                    'NSHighResolutionCapable': 'True'
                },
            )

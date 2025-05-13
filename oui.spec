# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['oui.py'],
    pathex=['C:\\Users\\estho\\Desktop\\Nouveau dossier'],
    binaries=[],  # Supprimez la ligne des DLLs problématiques
    datas=[
        (r'C:\Users\estho\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\mysql\connector\*', 'mysql/connector'),
        (r'C:\Users\estho\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\mysql\connector\locales\*', 'mysql/connector/locales')
    ],
    hiddenimports=[
        'mysql.connector.connection',
        'mysql.connector.connection_cext',
        'mysql.connector.locales',
        'mysql.connector.pooling',
        'mysql.connector.django',
        'mysql.connector.version'
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='oui',
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
    onefile=True,
    icon='logo.ico'
)
# PyInstaller spec of the Itch.io build:  pyinstaller --noconfirm pac-man.spec
# Then:  cp config.json README.md dist/pac-man/
# Result: dist/pac-man/ (the game + config.json + README.md).
# Zip this folder and upload it on Itch.io.
# The game starts with a double click: it reads the config.json next to it.

a = Analysis(
    ['pac-man.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['mazegenerator'],
    excludes=['numpy', 'pkg_resources', 'setuptools'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pac-man',
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='pac-man',
)

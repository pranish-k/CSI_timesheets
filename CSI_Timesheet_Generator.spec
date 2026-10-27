# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# The real roster is kept out of git; bundle the local copy as the app's starting roster if present.
roster = os.path.join(SPECPATH, 'employees.json')
roster_datas = [(roster, '.')] if os.path.exists(roster) else []

a = Analysis(
    ['generate_timesheets.py'],
    pathex=[],
    binaries=[],
    datas=[
        *collect_data_files('tkcalendar'),
        *collect_data_files('babel'),
        *roster_datas,
    ],
    hiddenimports=['babel.numbers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CSI Timesheet Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    # Must stay False: argv emulation's Apple Event loop breaks Tk's menu setup
    # and crashes the app on launch from Finder (NSMenuItem assertion in TkpInit).
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='CSI Timesheet Generator',
)

app = BUNDLE(
    coll,
    name='CSI Timesheet Generator.app',
    icon='icon.icns',
    bundle_identifier='com.csi.timesheetgenerator',
    info_plist={
        'CFBundleName': 'CSI Timesheet Generator',
        'CFBundleDisplayName': 'CSI Timesheet Generator',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)

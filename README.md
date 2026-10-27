# CSI Timesheet Generator

A small desktop app that prints a two-week paper timesheet for every student employee, combined into a single PDF.
It is built with Python, Tkinter and ReportLab, and ships as a signed macOS app.

## What it does

- Pick the Saturday that starts the pay period from a calendar.
- Choose an output folder.
- Click **Generate Timesheets** to get one PDF with a page per employee, named like `Timesheets_2026-10-24_to_2026-11-06.pdf`.

Each page has the employee's name and work area pre-filled, daily rows for both weeks, week-ending dates, a special notes area and signature lines.

The **Edit Employees** screen lets you add, update and delete employees (work area, first name, last name) without touching any files.

## Employee data

The roster is stored in `employees.json`, which is not committed to this repository because it contains real names.

- When running from source, the file lives next to `generate_timesheets.py`.
- In the macOS app, it lives in `~/Library/Application Support/CSI Timesheet Generator/`.

If no roster exists yet, the app starts with a few sample employees that you can replace from the Edit Employees screen.
When building the macOS app, a local `employees.json` in the project folder is bundled in as the starting roster for new installs.

## Running from source

Requires Python 3.10 or newer with Tkinter (the python.org installer includes it).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generate_timesheets.py
```

## Building the macOS app

`build_dmg.sh` builds the app with PyInstaller, code signs it, packages it into a DMG and notarizes it with Apple.

Before running it, edit the variables at the top of the script:

- `SIGN_IDENTITY`: your "Developer ID Application" certificate name.
- `NOTARY_PROFILE`: a notarytool keychain profile, created once with `xcrun notarytool store-credentials`.

Then run:

```bash
./build_dmg.sh
```

The signed and notarized `CSI_Timesheet_Generator.dmg` is written to the project folder.

To build an unsigned app only, run `pyinstaller CSI_Timesheet_Generator.spec --clean` and find it in `dist/`.

## Project layout

| File | Purpose |
| --- | --- |
| `generate_timesheets.py` | The app: GUI, roster storage and PDF drawing |
| `requirements.txt` | Python dependencies |
| `CSI_Timesheet_Generator.spec` | PyInstaller build configuration |
| `build_dmg.sh` | Build, sign, package and notarize script |
| `entitlements.plist` | Hardened runtime entitlements needed by the bundled Python |
| `icon.icns`, `Logo.jpg` | App icon and logo |

## License

Released under the [MIT License](LICENSE).

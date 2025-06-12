# DPSTool
A tool to analyse DPS from World of Warcraft logs.

## Idiot’s Guide to Building on Windows

1. Download and install Python from the official website. Make sure to check the box for **Add Python to PATH** during the setup.
2. Download this repository as a ZIP file and extract it to a folder you can easily find.
3. Open **Command Prompt** and `cd` into the folder you extracted.
4. Run `pip install -r requirements.txt` to grab the required packages.
5. Install PyInstaller by running `pip install pyinstaller`.
6. Build the tool with `pyinstaller --onefile dpstool.py`.
7. Look in the new `dist` folder for `dpstool.exe`, then double‑click it to start the program.

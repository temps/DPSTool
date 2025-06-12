# DPSTool
A tool to analyse DPS from World of Warcraft logs.

## Idiot’s Guide to Building on Windows

1. Download and install Python from the official website. Make sure to check the box for **Add Python to PATH** during the setup.
2. Download this repository as a ZIP file and extract it to a folder you can easily find.
3. Open **Command Prompt** and `cd` into the folder you extracted.
4. Run `pip install -r requirements.txt` to grab the required packages.
5. Install PyInstaller by running `pip install pyinstaller`.
6. Build the tool with `pyinstaller --onefile dpstool.py`.
7. Look in the new `dist` folder for `dpstool.exe`.
8. Double‑click `dpstool.exe` (or run it from the command line) to start the program. A console window will appear, showing the tool in action.

### Running the program

When you double‑click the executable, Windows will open a terminal window that runs `dpstool.exe`. You can also launch it from **Command Prompt** by navigating to the `dist` folder and typing `dpstool.exe`. Close the program by pressing `Ctrl+C` or closing the window when you’re done.

## Usage

`dpstool` expects a World of Warcraft `CombatLog.txt` file. Run the script and
provide the path to the log. You can optionally filter by player name using the
`--player` option:

```bash
python dpstool.py C:\\Path\\to\\CombatLog.txt --player MyCharacter
```

The program prints the total damage and the calculated DPS. Omitting
`--player` aggregates all damage events in the log.

# DPSTool
A simple GUI tool written in Python to analyse DPS from
World of Warcraft combat logs.

## Requirements

- Python 3.x
- Tkinter (bundled with the default Python installation)
- requests
- beautifulsoup4

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

   ```bash
   python dpstool.py
   ```

2. Click **Open Combat Log** and select a log file (e.g. `WowCombatLog.txt` or
   the provided `sample_log.txt`).
3. Choose your character from the drop-down list and click **Analyze** to see a
   detailed summary including rotation, downtime, and consumable usage.

The app also fetches the latest raid DPS information from
[SimulationCraft](https://www.simulationcraft.org/).

## Building a Stand-Alone Executable (Windows)

To build a stand-alone `.exe`, install `pyinstaller` and run:

```bash
pip install pyinstaller
pyinstaller --onefile dpstool.py
```

The executable will appear in the `dist` folder.

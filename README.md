# Elite-Dangerous-Rich-Presence
A standalone Discord Rich Presence application which hides in the System Tray
![](https://raw.githubusercontent.com/wiki/Lasa2/Elite-Dangerous-Rich-Presence/images/Rich-Presence.jpg)

At the start its check if the game or launcher is running and starts the launcher if not. Please check the config.ini if the path matches for you.  
It automatically closes when the game and the launcher are closed.
Check the [Wiki](https://github.com/Lasa2/Elite-Dangerous-Rich-Presence/wiki) to get a more detailed explanation for the config.

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)


# Build from Source
I tested this using Powershell and Python 3.8  
Clone the reposity and install the requirements:
```
git clone https://github.com/Lasa2/Elite-Dangerous-Rich-Presence.git
Set-Location Elite-Dangerous-Rich-Presence
python -m venv .venv
.venv/scripts/activate
pip install -r requirements.txt
```
To create a executable you can use pyinstaller:
```
.venv/scripts/activate
pip install pyinstaller
.venv/scripts/pyinstaller gui.py -n 'Elite Dangerous Rich Presence' -i elite-dangerous-clean.ico -w `
    --add-data 'elite-dangerous-clean.ico;.' --add-data 'logging.yaml;.' --add-data 'config.ini;.' `
    -p '.venv/lib/site-packages' --add-binary '.venv/lib/site-packages/pywin32_system32/pythoncom38.dll;.' `
    --add-binary '.venv/lib/site-packages/pywin32_system32/pywintypes38.dll;.' `
    --exclude-module altgraph --exclude-module future --exclude-module pefile --exclude-module pyinstaller

```

@ECHO OFF
ECHO "Releasing The Kraken!"

call C:\Users\Eric\Documents\fabric\FabricEngine-2.2.0-Windows-x86_64\environment.bat


set KRAKEN_PATH=C:\Users\Eric\Documents\dev\kraken
set FABRIC_EXTS_PATH=%FABRIC_EXTS_PATH%;%KRAKEN_PATH%\Exts;
set FABRIC_DFG_PATH=%FABRIC_DFG_PATH%;%KRAKEN_PATH%\Presets\DFG;
set PYTHONPATH=%PYTHONPATH%;%KRAKEN_PATH%\Python;


cd /d %KRAKEN_PATH%\Python\kraken\ui

call cmd /k "python kraken_window.py"


PAUSE
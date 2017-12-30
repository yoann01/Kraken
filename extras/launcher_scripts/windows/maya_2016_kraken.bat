@ECHO OFF
ECHO "Releasing The Kraken!"

set KRAKEN_PATH=C:\Users\Eric\Documents\dev\kraken
set FABRIC_EXTS_PATH=%FABRIC_EXTS_PATH%;%KRAKEN_PATH%\Exts;
set FABRIC_DFG_PATH=%FABRIC_DFG_PATH%;%KRAKEN_PATH%\Presets\DFG;
set PYTHONPATH=%PYTHONPATH%;%KRAKEN_PATH%\Python;


set MAYA_MODULE_PATH=C:\Users\Eric\Documents\fabric\FabricEngine-2.2.0-Windows-x86_64\DCCIntegrations\FabricMaya2016;%KRAKEN_PATH%\DCCIntegrations\maya;

start /d "C:\Program Files\Autodesk\Maya2016\bin" maya.exe


echo OFF
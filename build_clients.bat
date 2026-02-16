@echo off
echo Building Monitor Core...
pyinstaller --onefile --noconsole src/client/monitor_core.py

echo Building Start Script...
pyinstaller --onefile --noconsole src/client/iniciar_trabajo.py

echo Building Stop Script...
pyinstaller --onefile --noconsole src/client/finalizar_trabajo.py

echo Build Complete. Executables are in the dist folder.
pause

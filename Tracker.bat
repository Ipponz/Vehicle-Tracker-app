@echo off
cd /apps/1b Mobile App

echo Starting the Python web server...
rem The 'start' command runs app.py in a new window and immediately continues to the next line.
start "Python Server" python app.py

rem OPTIONAL BUT RECOMMENDED: Wait a few seconds for the server to start up.
echo Waiting 5 seconds for the server to initialize...
timeout /t 5 /nobreak >nul

echo Launching browser at http://localhost:5000
start http://localhost:5000

echo.
echo The server should be running in a separate window. This window can now be closed.
pause
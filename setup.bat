@echo off
echo ====================================================
echo        DIKSHA AUTOMATION SETUP SCRIPT
echo ====================================================
echo.
echo Installing Python dependencies...
python -m pip install -r requirements.txt
echo.
echo Installing Playwright Chromium browser...
python -m playwright install chromium
echo.
echo Setup completed successfully!
pause

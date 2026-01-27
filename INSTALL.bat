@echo off
echo ====================================================
echo 小红书 Content Generator - Installation
echo ====================================================
echo.
echo Installing required Python packages...
echo.

pip install -r requirements.txt

echo.
echo ====================================================
echo Installation complete!
echo ====================================================
echo.
echo Next steps:
echo 1. Create a .env file with your DEEPSEEK_API_KEY
echo 2. Run START_WEB.bat to start the web interface
echo 3. Or run START_GENERATOR.bat to generate content
echo.

pause

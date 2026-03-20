@echo off
TITLE Django Server Launcher

:: 1. Use double quotes here to handle the space in "MY Learning"
SET "VENV_PATH=D:\MY Learning\.venv"

echo ---------------------------------------
echo Starting Django Development Server...
echo ---------------------------------------

:: 2. Wrapped in quotes to ensure Windows reads the full path
IF NOT EXIST "%VENV_PATH%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment "%VENV_PATH%" not found.
    pause
    exit /b
)

:: 3. Activation with quotes
echo [1/3] Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

:: 4. Run migrations
echo [2/3] Checking for database migrations...
python manage.py migrate

:: 5. Launch the server
echo [3/3] Launching server at http://115.241.34.210:8000
python manage.py runserver 

pause
@echo off
REM Check if the virtual environment folder exists
if exist mxl-converter (
    echo Virtual environment already exists. Skipping creation...
) else (
    echo Creating virtual environment...
    python -m venv mxl-converter
)

REM Activate the virtual environment
call .\mxl-converter\Scripts\activate

REM Check if requirements are already installed
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Run the main Python file
echo Running the application...
python main.py

REM Pause the terminal to see any output
PAUSE

@echo off

REM Create virtual environment
python -m venv env

REM Activate virtual environment
call env\Scripts\activate

REM Install requirements
pip install -r requirements.txt

REM Done
echo Virtual environment created and requirements installed.

python main.py
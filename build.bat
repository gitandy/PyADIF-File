@echo off

call venv\Scripts\activate.bat

python -m pip install --upgrade build
python -m build
pause

@echo off
REM --- Buat virtual environment ---
py -3 -m venv .venv

REM --- Aktifkan venv ---
call .venv\Scripts\activate

REM --- Install package Python ---
python -m pip install --upgrade pip
pip install -r laptop\requirements-laptop.txt

echo.
echo ✅ Laptop venv ready (Windows). To activate later:
echo    .venv\Scripts\activate

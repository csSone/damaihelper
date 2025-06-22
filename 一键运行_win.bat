@echo off
setlocal

:: 1. 检查Python环境
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please download it from:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 2. 检查Conda环境
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo Conda is not installed. Please download Miniconda from:
    echo https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

:: 3. 检查damai_env是否存在
conda env list | find "damai_env" >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating damai_env...
    call conda create -n damai_env python=3.9 -y
    if %errorlevel% neq 0 (
        echo Failed to create damai_env.
        pause
        exit /b 1
    )
)

:: 4. 激活环境并运行
call conda activate damai_env
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

python GUI.py
if %errorlevel% neq 0 (
    echo Failed to run GUI.py.
    pause
    exit /b 1
)

pause
endlocal
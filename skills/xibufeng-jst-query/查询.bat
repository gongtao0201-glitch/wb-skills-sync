@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

rem 依次探测：系统 python → py 启动器 → WorkBuddy 内置 python
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (where py >nul 2>nul && set "PY=py")
if not defined PY (
  if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" (
    set "PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
  )
)
if not defined PY (
  echo.
  echo   [!] 没有检测到 Python
  echo.
  echo   请在自己电脑的 WorkBuddy 里直接提问，由 AI 帮你查询，
  echo   或者先安装 Python 后重新双击本文件。
  echo.
  pause
  exit /b 1
)

echo 使用 %PY%
echo.
%PY% query.py %*
echo.
pause

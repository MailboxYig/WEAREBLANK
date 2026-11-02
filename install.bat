@echo off
TITLE WEAREBLANK - CODM Auto-Updater PC Installer
COLOR 0A
echo ====================================================================
echo   WEAREBLANK CODM Auto-Updater - PC Hard Drive Setup
echo ====================================================================
echo.

set "PC_TOOLS_DIR=C:\WEAREBLANK_ADB"
set "ADB_PATH=%PC_TOOLS_DIR%\platform-tools\adb.exe"

:: 1. Check for system ADB
where adb >nul 2>&1
if %errorlevel% equ 0 (
    set "ADB_PATH=adb"
    echo [+] Using system-wide ADB found on PC.
    goto :CHECK_APKS
)

:: 2. Check for local hard drive ADB
if exist "%ADB_PATH%" (
    echo [+] Using existing WEAREBLANK ADB toolkit.
    goto :CHECK_APKS
)

:: 3. Download ADB if missing
echo [!] ADB not found. Installing portable ADB to PC (%PC_TOOLS_DIR%)...
if not exist "%PC_TOOLS_DIR%" mkdir "%PC_TOOLS_DIR%"
powershell -Command "Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile '%PC_TOOLS_DIR%\tools.zip'"
powershell -Command "Expand-Archive -Path '%PC_TOOLS_DIR%\tools.zip' -DestinationPath '%PC_TOOLS_DIR%' -Force"
del "%PC_TOOLS_DIR%\tools.zip"
echo [+] ADB installed successfully!

:CHECK_APKS
:: 4. Auto-download Termux from F-Droid if missing
if not exist "termux.apk" (
    echo [+] Downloading Termux from F-Droid...
    powershell -Command "Invoke-WebRequest -Uri 'https://f-droid.org/repo/com.termux_1002.apk' -OutFile 'termux.apk'"
)

:: 5. Auto-download Termux:Boot if missing
if not exist "termux-boot.apk" (
    echo [+] Downloading Termux:Boot from F-Droid...
    powershell -Command "Invoke-WebRequest -Uri 'https://f-droid.org/repo/com.termux.boot_7.apk' -OutFile 'termux-boot.apk'"
)

echo.
echo [1/5] Waiting for Meta Quest to connect via USB...
"%ADB_PATH%" wait-for-device
echo [+] Quest connected successfully!

echo.
echo [2/5] Sideloading Termux and Termux:Boot...
"%ADB_PATH%" install termux.apk
"%ADB_PATH%" install termux-boot.apk

echo.
echo [3/5] Staging automation scripts to headset storage (/sdcard/Download/)...
"%ADB_PATH%" push setup.sh /sdcard/Download/setup.sh
"%ADB_PATH%" push codm_checker.py /sdcard/Download/codm_checker.py
"%ADB_PATH%" push codm_boot.sh /sdcard/Download/codm_boot.sh
"%ADB_PATH%" push start_codm.sh /sdcard/Download/start_codm.sh

echo.
echo [4/5] Automatically launching Termux on the headset...
"%ADB_PATH%" shell am start -n com.termux/.App

echo.
echo ====================================================================
echo   SETUP ALMOST COMPLETE! 
echo   Put on your Quest headset now. Termux should be open.
echo.
echo   Type these TWO commands inside Termux in order and press Enter:
echo   ----------------------------------------------------------------
echo   termux-setup-storage
echo   sh /sdcard/Download/setup.sh
echo   ----------------------------------------------------------------
echo   *(Accept the Android storage permission popup when it appears)*
echo   Once finished, you are done! All tools are now fully deployed.
echo ====================================================================
pause
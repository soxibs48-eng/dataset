@echo off
chcp 65001 > nul
echo ==============================================================
echo   SmartPrice AI - GitHub'ga Avtomatik Yuklash (Push Helper)
echo ==============================================================
echo.
set /p REPO_URL="GitHub repozitoriyangiz URL havolasini kiriting (masalan: https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo [XATO] Havola kiritilmadi! Dastur to'xtatildi.
    pause
    exit /b
)

echo.
echo [1/3] Git remote tekshirilmoqda...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2/3] Branch main ga sozlanmoqda...
git branch -M main

echo [3/3] GitHub'ga push qilinmoqda...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==============================================================
    echo   [MUVAFFAQIYAT] Barcha kodlar GitHub'ga muvaffaqiyatli yuklandi!
    echo ==============================================================
) else (
    echo.
    echo [DIQQAT] Push qilishda xatolik yuz berdi. Iltimos GitHub login/token yoki havolani tekshiring.
)
echo.
pause

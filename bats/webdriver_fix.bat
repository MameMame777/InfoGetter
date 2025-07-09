@echo off
:: WebDriver修復ツール起動スクリプト
title WebDriver修復ツール

echo ==========================================
echo WebDriver 修復ツール
echo ==========================================
echo.

echo Pythonパッケージを確認中...
python -c "import selenium" 2>nul
if errorlevel 1 (
    echo Seleniumがインストールされていません。インストール中...
    pip install selenium webdriver-manager
    if errorlevel 1 (
        echo エラー: Seleniumのインストールに失敗しました。
        pause
        exit /b 1
    )
    echo Seleniumのインストールが完了しました。
)

echo webdriver-managerを確認中...
python -c "import webdriver_manager" 2>nul
if errorlevel 1 (
    echo webdriver-managerがインストールされていません。インストール中...
    pip install webdriver-manager
    if errorlevel 1 (
        echo エラー: webdriver-managerのインストールに失敗しました。
        pause
        exit /b 1
    )
)

echo.
echo 修復ツールを起動しています...
echo.

:: 統合修復ツールを実行
python webdriver_master.py

if errorlevel 1 (
    echo.
    echo エラーが発生しました。ログを確認してください。
)

echo.
echo 処理が完了しました。
pause

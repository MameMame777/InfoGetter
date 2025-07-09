@echo off
:: InfoGatherer自動実行バッチファイル（基本版）
:: タスクスケジューラー用

cd /d "e:\Nautilus\workspace\pythonworks\InfoGetter"

echo [%date% %time%] InfoGatherer自動実行開始
echo =============================================

:: Python環境の確認
echo Python環境確認中...
python --version
if errorlevel 1 (
    echo エラー: Python環境が見つかりません
    exit /b 1
)

:: 必要なパッケージの確認
echo 必要なパッケージ確認中...
python -c "import yaml, requests, selenium" 2>nul
if errorlevel 1 (
    echo 必要なパッケージをインストール中...
    pip install pyyaml requests selenium webdriver-manager
)

:: WebDriver状態確認（簡易）
echo WebDriver状態確認中...
python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; print('WebDriver OK')" 2>nul
if errorlevel 1 (
    echo WebDriver問題検出 - 修復実行中...
    python webdriver_repair.py
)

:: メインスクリプト実行
echo [%date% %time%] スクレイピング開始
python -m src.main

if errorlevel 1 (
    echo [%date% %time%] エラー: スクレイピング実行に失敗
    exit /b 1
) else (
    echo [%date% %time%] スクレイピング正常完了
)

echo [%date% %time%] InfoGatherer自動実行完了
echo =============================================

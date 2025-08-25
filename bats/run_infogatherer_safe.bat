@echo off
:: InfoGatherer自動実行バッチファイル（安全版）
:: エラーハンドリング強化・ログ出力付き

setlocal EnableDelayedExpansion

:: 設定
set WORK_DIR=e:\Nautilus\workspace\pythonworks\InfoGetter
set LOG_DIR=%WORK_DIR%\logs
set LOG_FILE=%LOG_DIR%\scheduler_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.log

:: 時刻のコロンを削除（ファイル名用）
set LOG_FILE=%LOG_FILE::=%

:: ログディレクトリ作成
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: ログ関数の定義
call :log "InfoGatherer自動実行開始"
call :log "作業ディレクトリ: %WORK_DIR%"
call :log "ログファイル: %LOG_FILE%"

:: 作業ディレクトリに移動
cd /d "%WORK_DIR%"
if errorlevel 1 (
    call :log "エラー: 作業ディレクトリへの移動に失敗"
    exit /b 1
)

:: Python環境確認
call :log "Python環境確認中..."
python --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "エラー: Python環境が見つかりません"
    exit /b 1
)

:: 必要なパッケージ確認
call :log "必要なパッケージ確認中..."
python -c "import yaml, requests, selenium, webdriver_manager" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "パッケージが不足しています - インストール中..."
    pip install pyyaml requests selenium webdriver-manager >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "エラー: パッケージインストールに失敗"
        exit /b 1
    )
)

:: WebDriver状態確認
call :log "WebDriver状態確認中..."
python test_webdriver.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "WebDriver問題検出 - 修復実行中..."
    python webdriver_repair.py >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "警告: WebDriver修復に失敗 - 継続実行"
    ) else (
        call :log "WebDriver修復完了"
    )
)

:: メインスクリプト実行
call :log "スクレイピング実行開始"
python -m src.main >> "%LOG_FILE%" 2>&1
set RESULT=%errorlevel%

:: 結果確認
if %RESULT% equ 0 (
    call :log "スクレイピング正常完了"
    
    :: 結果ファイルの確認
    if exist "results\fpga_documents.json" (
        call :log "結果ファイル生成確認: results\fpga_documents.json"
        for %%f in ("results\fpga_documents.json") do (
            call :log "ファイルサイズ: %%~zf bytes"
        )
    ) else (
        call :log "警告: 結果ファイルが見つかりません"
    )
) else (
    call :log "エラー: スクレイピング実行に失敗 (終了コード: %RESULT%)"
)

call :log "InfoGatherer自動実行完了"

:: 古いログファイルのクリーンアップ（30日以上前）
call :log "ログファイルクリーンアップ実行中..."
forfiles /p "%LOG_DIR%" /s /m scheduler_*.log /d -30 /c "cmd /c del @path" 2>nul
if not errorlevel 1 call :log "古いログファイルを削除しました"

exit /b %RESULT%

:: ログ出力関数
:log
set timestamp=%date% %time%
echo [%timestamp%] %~1
echo [%timestamp%] %~1 >> "%LOG_FILE%"
goto :eof

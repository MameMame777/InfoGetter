# InfoGatherer自動実行スクリプト (PowerShell)
# タスクスケジューラー用 - 推奨版

param(
    [string]$ConfigPath = "config\settings.yaml",
    [switch]$TestMode = $false,
    [switch]$EmailNotification = $true,
    [switch]$Verbose = $false
)

# 設定
$WorkDir = "e:\Nautilus\workspace\pythonworks\InfoGetter"
$LogDir = Join-Path $WorkDir "logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "scheduler_$Timestamp.log"

# ログ関数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # コンソールとファイルの両方に出力
    Write-Output $logMessage
    Add-Content -Path $LogFile -Value $logMessage
    
    # 詳細モードでの追加情報
    if ($Verbose -and $Level -eq "ERROR") {
        Write-Error $Message
    }
}

# エラーハンドリング関数
function Handle-Error {
    param(
        [string]$ErrorMessage,
        [int]$ExitCode = 1
    )
    Write-Log "エラー: $ErrorMessage" "ERROR"
    Write-Log "InfoGatherer自動実行異常終了" "ERROR"
    
    # エラー時のメール通知（オプション）
    if ($EmailNotification) {
        Send-ErrorNotification -ErrorMessage $ErrorMessage -LogFile $LogFile
    }
    
    exit $ExitCode
}

# 成功通知関数
function Send-SuccessNotification {
    param(
        [string]$ResultFile,
        [string]$LogFile
    )
    
    # 実際のメール送信はここに実装
    # 今回は簡易ログ出力のみ
    Write-Log "成功通知: 結果ファイル=$ResultFile, ログ=$LogFile" "INFO"
}

# エラー通知関数
function Send-ErrorNotification {
    param(
        [string]$ErrorMessage,
        [string]$LogFile
    )
    
    # 実際のメール送信はここに実装
    # 今回は簡易ログ出力のみ
    Write-Log "エラー通知: $ErrorMessage, ログ=$LogFile" "ERROR"
}

# メイン処理
try {
    # ログディレクトリ作成
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    Write-Log "InfoGatherer自動実行開始"
    Write-Log "PowerShellバージョン: $($PSVersionTable.PSVersion)"
    Write-Log "作業ディレクトリ: $WorkDir"
    Write-Log "設定ファイル: $ConfigPath"
    Write-Log "テストモード: $TestMode"
    Write-Log "メール通知: $EmailNotification"

    # 作業ディレクトリに移動
    if (-not (Test-Path $WorkDir)) {
        Handle-Error "作業ディレクトリが見つかりません: $WorkDir"
    }
    
    Set-Location $WorkDir
    Write-Log "作業ディレクトリに移動完了"

    # Python環境確認
    Write-Log "Python環境確認中..."
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Python環境が見つかりません"
        }
        Write-Log "Python環境: $pythonVersion"
    }
    catch {
        Handle-Error "Python実行エラー: $($_.Exception.Message)"
    }

    # 必要なパッケージ確認
    Write-Log "必要なパッケージ確認中..."
    $packageCheck = python -c "import yaml, requests, selenium, webdriver_manager; print('All packages OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "パッケージが不足しています - インストール中..."
        pip install pyyaml requests selenium webdriver-manager
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "パッケージインストールに失敗"
        }
        Write-Log "パッケージインストール完了"
    } else {
        Write-Log "必要なパッケージ確認完了"
    }

    # WebDriver健全性チェック
    Write-Log "WebDriver状態確認中..."
    $webdriverCheck = python -c "
try:
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('data:text/html,<html><body>Test</body></html>')
    driver.quit()
    print('WebDriver OK')
except Exception as e:
    print(f'WebDriver Error: {e}')
    exit(1)
" 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Log "WebDriver問題検出: $webdriverCheck"
        Write-Log "WebDriver修復実行中..."
        
        python webdriver_repair.py *>&1 | Tee-Object -Append -FilePath $LogFile
        if ($LASTEXITCODE -eq 0) {
            Write-Log "WebDriver修復完了"
        } else {
            Write-Log "WebDriver修復失敗 - 継続実行" "WARN"
        }
    } else {
        Write-Log "WebDriver状態正常"
    }

    # メインスクリプト実行
    Write-Log "スクレイピング実行開始"
    
    if ($TestMode) {
        Write-Log "テストモード - arXivのみ実行"
        python test_arxiv.py *>&1 | Tee-Object -Append -FilePath $LogFile
    } else {
        Write-Log "通常モード - 全スクレイピング実行"
        python -m src.main *>&1 | Tee-Object -Append -FilePath $LogFile
    }

    $scriptResult = $LASTEXITCODE

    if ($scriptResult -eq 0) {
        Write-Log "スクレイピング正常完了"
        
        # 結果ファイルの確認
        $resultFile = "results\fpga_documents.json"
        if (Test-Path $resultFile) {
            $fileInfo = Get-Item $resultFile
            Write-Log "結果ファイル: $($fileInfo.FullName)"
            Write-Log "更新日時: $($fileInfo.LastWriteTime)"
            
            $fileSizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
            Write-Log "ファイルサイズ: $fileSizeKB KB"
            
            # 成功通知
            if ($EmailNotification) {
                Send-SuccessNotification -ResultFile $resultFile -LogFile $LogFile
            }
        } else {
            Write-Log "警告: 結果ファイルが見つかりません" "WARN"
        }
        
        Write-Log "InfoGatherer自動実行正常完了"
        
        # 古いログファイルのクリーンアップ（30日以上前）
        Write-Log "ログファイルクリーンアップ実行中..."
        $oldLogs = Get-ChildItem $LogDir -Filter "scheduler_*.log" | Where-Object { 
            $_.LastWriteTime -lt (Get-Date).AddDays(-30) 
        }
        
        if ($oldLogs.Count -gt 0) {
            $oldLogs | Remove-Item -Force
            Write-Log "古いログファイル $($oldLogs.Count) 件を削除"
        }
        
        exit 0
        
    } else {
        Handle-Error "スクレイピング実行エラー (終了コード: $scriptResult)" $scriptResult
    }

} catch {
    Handle-Error "予期しないエラー: $($_.Exception.Message)"
}

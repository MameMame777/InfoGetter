# タスクスケジューラー自動実行設定ガイド

## 📋 概要

このガイドでは、FPGAドキュメント収集システム（InfoGetter）をWindowsタスクスケジューラーで自動実行する手順を説明します。定期的な自動実行により、最新のドキュメント情報を継続的に収集できます。

---

## 🎯 自動実行のメリット

- **継続的監視**: 新しいドキュメントの自動検出
- **定期レポート**: スケジュールされたメール通知
- **運用効率化**: 手動実行の不要
- **データ鮮度**: 常に最新情報の維持

---

## 🔧 事前準備

### 1. スクリプトファイルの準備

まず、タスクスケジューラー用の実行スクリプトを作成します。

**`run_infogatherer.bat`**
```batch
@echo off
cd /d "e:\NAME\workspace\pythonworks\InfoGetter"

echo [%date% %time%] InfoGatherer自動実行開始
echo =============================================

:: Python環境の確認
python --version
if errorlevel 1 (
    echo Python環境エラー
    exit /b 1
)

:: 必要なパッケージの確認
python -c "import yaml, requests, selenium" 2>nul
if errorlevel 1 (
    echo 必要なパッケージが不足しています
    pip install pyyaml requests selenium webdriver-manager
)

:: メインスクリプト実行
echo [%date% %time%] スクレイピング開始
python -m src.main

echo [%date% %time%] InfoGatherer自動実行完了
echo =============================================
```

**`run_infogatherer_safe.bat`** (エラーハンドリング強化版)
```batch
@echo off
setlocal EnableDelayedExpansion

:: 作業ディレクトリ設定
set WORK_DIR=e:\NAME\workspace\pythonworks\InfoGetter
set LOG_DIR=%WORK_DIR%\logs
set LOG_FILE=%LOG_DIR%\scheduler_%date:~0,4%%date:~5,2%%date:~8,2%.log

:: ログディレクトリ作成
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: ログ関数
call :log "InfoGatherer自動実行開始"
call :log "作業ディレクトリ: %WORK_DIR%"

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

:: WebDriver修復（必要に応じて）
call :log "WebDriver状態確認中..."
python test_webdriver.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "WebDriver問題検出 - 修復実行中..."
    python webdriver_repair.py >> "%LOG_FILE%" 2>&1
)

:: メインスクリプト実行
call :log "スクレイピング実行開始"
python -m src.main >> "%LOG_FILE%" 2>&1
set RESULT=%errorlevel%

if %RESULT% equ 0 (
    call :log "スクレイピング正常完了"
) else (
    call :log "エラー: スクレイピング実行に失敗 (終了コード: %RESULT%)"
)

call :log "InfoGatherer自動実行完了"
exit /b %RESULT%

:log
echo [%date% %time%] %~1
echo [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof
```

### 2. PowerShell実行スクリプト（推奨）

**`run_infogatherer.ps1`**
```powershell
# InfoGatherer自動実行スクリプト (PowerShell)
param(
    [string]$ConfigPath = "config\settings.yaml",
    [switch]$TestMode = $false,
    [switch]$EmailNotification = $true
)

# 設定
$WorkDir = "e:\NAME\workspace\pythonworks\InfoGetter"
$LogDir = Join-Path $WorkDir "logs"
$LogFile = Join-Path $LogDir "scheduler_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# ログ関数
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Output $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# メイン処理
try {
    # ログディレクトリ作成
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force
    }

    Write-Log "InfoGatherer自動実行開始"
    Write-Log "作業ディレクトリ: $WorkDir"
    Write-Log "設定ファイル: $ConfigPath"
    Write-Log "テストモード: $TestMode"

    # 作業ディレクトリに移動
    Set-Location $WorkDir
    
    # Python環境確認
    Write-Log "Python環境確認中..."
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python環境が見つかりません"
    }
    Write-Log "Python環境: $pythonVersion"

    # 必要なパッケージ確認
    Write-Log "必要なパッケージ確認中..."
    python -c "import yaml, requests, selenium, webdriver_manager" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "パッケージが不足しています - インストール中..."
        pip install pyyaml requests selenium webdriver-manager
    }

    # WebDriver健全性チェック
    Write-Log "WebDriver状態確認中..."
    python test_webdriver.py *>&1 | Tee-Object -Append -FilePath $LogFile
    if ($LASTEXITCODE -ne 0) {
        Write-Log "WebDriver問題検出 - 修復実行中..."
        python webdriver_repair.py *>&1 | Tee-Object -Append -FilePath $LogFile
    }

    # メインスクリプト実行
    Write-Log "スクレイピング実行開始"
    
    if ($TestMode) {
        # テストモード - arXivのみ
        python test_arxiv.py *>&1 | Tee-Object -Append -FilePath $LogFile
    } else {
        # 通常モード - 全スクレイピング
        python -m src.main *>&1 | Tee-Object -Append -FilePath $LogFile
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Log "スクレイピング正常完了"
        
        # 結果ファイルの確認
        $resultFile = "results\fpga_documents.json"
        if (Test-Path $resultFile) {
            $fileInfo = Get-Item $resultFile
            Write-Log "結果ファイル: $($fileInfo.FullName) (更新日時: $($fileInfo.LastWriteTime))"
            
            # ファイルサイズ確認
            $fileSizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
            Write-Log "結果ファイルサイズ: $fileSizeKB KB"
        }
        
        Write-Log "InfoGatherer自動実行正常完了"
        exit 0
    } else {
        throw "スクレイピング実行エラー (終了コード: $LASTEXITCODE)"
    }

} catch {
    Write-Log "エラー: $($_.Exception.Message)"
    Write-Log "InfoGatherer自動実行異常終了"
    exit 1
}
```

---

## 📅 タスクスケジューラー設定手順

### Step 1: タスクスケジューラーを開く

1. **Windows + R** キーを押して「ファイル名を指定して実行」を開く
2. `taskschd.msc` と入力してEnterキーを押す
3. または、スタートメニューから「タスクスケジューラー」を検索

### Step 2: 基本タスクの作成

1. 右側の「操作」パネルで **「基本タスクの作成」** をクリック
2. **タスク名**: `InfoGatherer-AutoRun`
3. **説明**: `FPGA文書自動収集システムの定期実行`
4. **「次へ」** をクリック

### Step 3: トリガー設定

#### 毎日実行の場合
1. **「毎日」** を選択
2. **開始日時**: 実行開始日を設定
3. **開始時刻**: `09:00:00` (業務開始時刻)
4. **「毎日」**: 1日おき

#### 毎週実行の場合
1. **「毎週」** を選択
2. **曜日**: 月曜日と金曜日にチェック
3. **開始時刻**: `08:30:00`

#### カスタムスケジュール例
```
毎週月曜日 08:30 - 週次レポート生成
毎日 18:00 - 日次更新確認
毎月第1月曜日 07:00 - 月次集計
```

### Step 4: 操作設定

#### バッチファイル実行の場合
1. **「プログラムの開始」** を選択
2. **プログラム/スクリプト**: 
   ```
   C:\Windows\System32\cmd.exe
   ```
3. **引数の追加**: 
   ```
   /c "e:\NAME\workspace\pythonworks\InfoGetter\run_infogatherer_safe.bat"
   ```
4. **開始場所**: 
   ```
   e:\NAME\workspace\pythonworks\InfoGetter
   ```

#### PowerShell実行の場合（推奨）
1. **プログラム/スクリプト**: 
   ```
   C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
   ```
2. **引数の追加**: 
   ```
   -ExecutionPolicy Bypass -File "e:\NAME\workspace\pythonworks\InfoGetter\run_infogatherer.ps1"
   ```
3. **開始場所**: 
   ```
   e:\NAME\workspace\pythonworks\InfoGetter
   ```

### Step 5: 詳細設定

1. タスク作成完了後、タスクを右クリックして **「プロパティ」** を選択

#### 「全般」タブ
- ☑ **「ユーザーがログオンしているかどうかにかかわらず実行する」**
- ☑ **「最上位の特権で実行する」**
- **「構成」**: Windows 10

#### 「トリガー」タブ
- **詳細設定**:
  - ☑ **「有効」**
  - **「タスクを停止するまでの時間」**: 2時間
  - **「タスクを繰り返す間隔」**: 1時間（必要に応じて）

#### 「操作」タブ
- 設定済みの操作を確認・編集

#### 「条件」タブ
- ☑ **「コンピューターをAC電源で使用している場合のみタスクを開始する」** (ラップトップの場合)
- ☑ **「ネットワーク接続が利用可能な場合のみタスクを開始する」**
- **ネットワーク**: 任意の接続

#### 「設定」タブ
- ☑ **「要求時にタスクを実行する」**
- ☑ **「スケジュールされた開始時刻にタスクが実行されなかった場合、すぐにタスクを開始する」**
- **「タスクが失敗した場合の再起動の間隔」**: 1分
- **「再起動の試行回数」**: 3回

---

## 🔍 動作確認とテスト

### Step 1: 手動実行テスト

1. タスクスケジューラーでタスクを選択
2. 右クリックして **「実行」** を選択
3. **「最後の実行結果」** が `0x0` (成功) になることを確認

### Step 2: ログ確認

#### PowerShell実行ログ
```
logs\scheduler_20250709_090000.log
```

#### バッチファイル実行ログ
```
logs\scheduler_20250709.log
```

#### 確認すべき内容
```
[2025-07-09 09:00:01] InfoGatherer自動実行開始
[2025-07-09 09:00:02] Python環境: Python 3.10.6
[2025-07-09 09:00:05] WebDriver状態確認中...
[2025-07-09 09:00:10] スクレイピング実行開始
[2025-07-09 09:05:30] 結果ファイル: results\fpga_documents.json
[2025-07-09 09:05:31] InfoGatherer自動実行正常完了
```

### Step 3: 結果ファイル確認

```powershell
# 最新の結果ファイル確認
Get-ChildItem "results\*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

---

## 📧 メール通知の自動化

### 設定ファイルでの通知有効化

**`config/settings.yaml`**
```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    recipients_file: "config/recipients.yaml"
    credentials_file: "config/email_credentials.yaml"
    # 自動実行時の追加設定
    subject_prefix: "[自動実行]"
    attach_results: true
    send_on_error: true
```

### PowerShellでの高度な通知

**`send_notification.ps1`** (追加スクリプト)
```powershell
param(
    [string]$ResultFile,
    [string]$LogFile,
    [int]$ExitCode = 0
)

# SMTP設定（環境変数から取得推奨）
$SmtpServer = "smtp.gmail.com"
$SmtpPort = 587
$FromEmail = $env:INFOGATHERER_EMAIL
$ToEmails = @("NAME@example.com", "NAME@example.com")
$Password = $env:INFOGATHERER_EMAIL_PASSWORD

if ($ExitCode -eq 0) {
    $Subject = "[成功] InfoGatherer自動実行完了 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    $Body = @"
InfoGathererの自動実行が正常に完了しました。

実行日時: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
結果ファイル: $ResultFile
ログファイル: $LogFile

詳細は添付ファイルをご確認ください。
"@
} else {
    $Subject = "[エラー] InfoGatherer自動実行失敗 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    $Body = @"
InfoGathererの自動実行でエラーが発生しました。

実行日時: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
終了コード: $ExitCode
ログファイル: $LogFile

ログファイルを確認してください。
"@
}

# メール送信
try {
    $SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force
    $Credential = New-Object System.Management.Automation.PSCredential($FromEmail, $SecurePassword)

    Send-MailMessage -SmtpServer $SmtpServer -Port $SmtpPort -UseSsl -Credential $Credential `
                     -From $FromEmail -To $ToEmails -Subject $Subject -Body $Body `
                     -Attachments $LogFile

    Write-Output "通知メール送信完了"
} catch {
    Write-Error "メール送信エラー: $($_.Exception.Message)"
}
```

---

## 🛠️ トラブルシューティング

### よくある問題と解決策

#### 1. タスクが実行されない

**原因**: 権限不足
**解決策**: 
- 「最上位の特権で実行する」にチェック
- 管理者権限でタスクスケジューラーを実行

#### 2. WebDriverエラーが発生する

**原因**: ChromeDriverの問題
**解決策**:
```batch
:: スクリプト内でWebDriver修復を追加
python webdriver_repair.py
if errorlevel 1 (
    python firefox_setup.py
)
```

#### 3. ネットワーク接続エラー

**原因**: プロキシ設定
**解決策**:
```yaml
# settings.yamlに追加
network:
  proxy:
    http: "http://proxy.company.com:8080"
    https: "https://proxy.company.com:8080"
  timeout: 30
  retry_count: 3
```

#### 4. メール送信失敗

**原因**: 認証設定
**解決策**:
```powershell
# 環境変数の設定
[Environment]::SetEnvironmentVariable("INFOGATHERER_EMAIL", "NAME@gmail.com", "Machine")
[Environment]::SetEnvironmentVariable("INFOGATHERER_EMAIL_PASSWORD", "NAME-app-password", "Machine")
```

### ログ分析スクリプト

**`analyze_logs.ps1`**
```powershell
param([string]$LogDir = "logs")

$logFiles = Get-ChildItem $LogDir -Filter "scheduler_*.log" | Sort-Object LastWriteTime -Descending

foreach ($logFile in $logFiles) {
    Write-Output "=== $($logFile.Name) ==="
    
    $content = Get-Content $logFile.FullName
    
    # 成功・失敗の判定
    if ($content -match "正常完了") {
        Write-Output "✅ 実行成功"
    } elseif ($content -match "異常終了|エラー") {
        Write-Output "❌ 実行失敗"
        
        # エラー内容の抽出
        $errors = $content | Where-Object { $_ -match "エラー|Error|Exception" }
        $errors | ForEach-Object { Write-Output "  $_" }
    } else {
        Write-Output "⚠️ 状態不明"
    }
    
    Write-Output ""
}
```

---

## 📊 監視とメンテナンス

### 定期メンテナンススクリプト

**`maintenance.ps1`**
```powershell
# InfoGatherer定期メンテナンス

# 古いログファイルの削除（30日以上）
$oldLogs = Get-ChildItem "logs" -Filter "*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
$oldLogs | Remove-Item -Force
Write-Output "古いログファイル $($oldLogs.Count) 件を削除"

# 古い結果ファイルのアーカイブ（7日以上）
$oldResults = Get-ChildItem "results" -Filter "*.backup_*" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
if ($oldResults.Count -gt 0) {
    $archiveDir = "results\archive\$(Get-Date -Format 'yyyy-MM')"
    if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Path $archiveDir -Force }
    $oldResults | Move-Item -Destination $archiveDir
    Write-Output "古い結果ファイル $($oldResults.Count) 件をアーカイブ"
}

# WebDriverキャッシュサイズ確認
$wdmCache = "$env:USERPROFILE\.wdm"
if (Test-Path $wdmCache) {
    $cacheSize = (Get-ChildItem $wdmCache -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    if ($cacheSize -gt 500) {
        Write-Output "WebDriverキャッシュサイズ大: $([math]::Round($cacheSize, 2)) MB"
        # 必要に応じてキャッシュクリア
        # Remove-Item $wdmCache -Recurse -Force
    }
}
```

### パフォーマンス監視

**`performance_monitor.ps1`**
```powershell
# 実行時間とリソース使用量の監視

$logFiles = Get-ChildItem "logs" -Filter "scheduler_*.log" | Sort-Object LastWriteTime -Descending -First 10

foreach ($logFile in $logFiles) {
    $content = Get-Content $logFile.FullName
    
    # 開始・終了時刻の抽出
    $startTime = ($content | Where-Object { $_ -match "自動実行開始" } | Select-Object -First 1) -replace '.*\[(.*?)\].*', '$1'
    $endTime = ($content | Where-Object { $_ -match "自動実行.*完了" } | Select-Object -First 1) -replace '.*\[(.*?)\].*', '$1'
    
    if ($startTime -and $endTime) {
        $start = [DateTime]::ParseExact($startTime, "yyyy-MM-dd HH:mm:ss", $null)
        $end = [DateTime]::ParseExact($endTime, "yyyy-MM-dd HH:mm:ss", $null)
        $duration = $end - $start
        
        Write-Output "$($logFile.Name): 実行時間 $($duration.TotalMinutes.ToString('F1')) 分"
    }
}
```

---

## 🎯 まとめ

### 推奨設定

1. **実行頻度**: 毎日朝8時30分（業務開始前）
2. **実行方法**: PowerShellスクリプト（エラーハンドリング強化）
3. **ログ保持**: 30日間
4. **メール通知**: 成功時は週次サマリー、エラー時は即座に通知
5. **メンテナンス**: 月次でのログクリーンアップ

### チェックリスト

- [ ] 実行スクリプトの作成とテスト
- [ ] タスクスケジューラーでの基本タスク作成
- [ ] 権限設定（最上位特権での実行）
- [ ] 条件設定（ネットワーク接続、電源）
- [ ] 手動実行での動作確認
- [ ] ログファイルの確認
- [ ] メール通知のテスト
- [ ] エラー時の自動修復動作確認
- [ ] 定期メンテナンススクリプトの設定

この設定により、InfoGathererシステムが安定して自動実行され、継続的にFPGAドキュメント情報を収集できます。

# タスクスケジューラー クイックスタートガイド

## 🚀 5分で設定完了

### Step 1: スクリプトの準備
1. 以下のファイルが存在することを確認:
   - `run_infogatherer.bat` (基本版)
   - `run_infogatherer_safe.bat` (安全版)
   - `run_infogatherer.ps1` (PowerShell版・推奨)

### Step 2: タスクスケジューラーを開く
1. **Windows + R** → `taskschd.msc` → Enter

### Step 3: 基本タスクを作成
1. 右クリック → **「基本タスクの作成」**
2. **名前**: `InfoGatherer-Daily`
3. **説明**: `FPGA文書自動収集 - 毎日実行`

### Step 4: スケジュール設定
1. **「毎日」** を選択
2. **開始時刻**: `08:30:00`
3. **間隔**: 1日おき

### Step 5: 実行設定（PowerShell推奨）
1. **「プログラムの開始」** を選択
2. **プログラム**: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
3. **引数**: `-ExecutionPolicy Bypass -File "e:\NAME\workspace\pythonworks\InfoGetter\run_infogatherer.ps1"`
4. **開始場所**: `e:\NAME\workspace\pythonworks\InfoGetter`

### Step 6: 詳細設定
1. タスク右クリック → **「プロパティ」**
2. **「全般」** タブ:
   - ☑ **「ユーザーがログオンしているかどうかにかかわらず実行する」**
   - ☑ **「最上位の特権で実行する」**
3. **「条件」** タブ:
   - ☑ **「ネットワーク接続が利用可能な場合のみタスクを開始する」**

### Step 7: テスト実行
1. タスクを右クリック → **「実行」**
2. **「最後の実行結果」** が `0x0` になることを確認
3. `logs\` フォルダにログファイルが作成されることを確認

## 🔧 トラブルシューティング

### 実行されない場合
- [ ] 「最上位の特権で実行する」にチェックが入っているか
- [ ] パスが正しく設定されているか
- [ ] Pythonがシステムパスに登録されているか

### WebDriverエラーの場合
- [ ] `python webdriver_repair.py` を手動実行
- [ ] Chrome/Firefoxが最新版か確認

### ログ確認
```
logs\scheduler_YYYYMMDD_HHMMSS.log
```

## 📧 メール通知設定（オプション）

### 環境変数設定
```powershell
[Environment]::SetEnvironmentVariable("INFOGATHERER_EMAIL", "NAME@gmail.com", "Machine")
[Environment]::SetEnvironmentVariable("INFOGATHERER_EMAIL_PASSWORD", "NAME-app-password", "Machine")
```

### 通知の有効化
`config\settings.yaml` で `notifications.email.enabled: true` に設定

---

**これで完了！毎日自動でFPGAドキュメントが収集されます。**

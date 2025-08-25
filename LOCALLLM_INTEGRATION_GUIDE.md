# LocalLLM API統合ガイド

## 概要

InfoGetterプロジェクトにLocalLLM APIを統合して、スクレイピング結果の AI要約・日本語翻訳機能を追加しました。

## 統合アプローチ

**API Client方式**を採用しています：
- InfoGetter: 軽量なAPIクライアント
- LocalLLM: 独立したAPIサーバー
- 両プロジェクトの独立性を保持

## セットアップ手順

### 1. LocalLLMサーバーの準備

```bash
# LocalLLMリポジトリのクローン
git clone https://github.com/MameMame777/LocalLLM.git
cd LocalLLM

# 依存関係のインストール
pip install -r requirements.txt

# LLMモデルのダウンロード（例：Llama 2 7B）
mkdir models
# モデルファイルをmodelsディレクトリに配置

# APIサーバーを起動
python -m src.api.server --host localhost --port 8000
```

### 2. InfoGetterの設定

**config/settings.yaml**にLLM API設定を追加：

```yaml
# LLM API設定（LocalLLM連携）
llm_api:
  enabled: true  # LLM要約機能を有効化
  api_base_url: "http://localhost:8000"  # LocalLLM APIサーバーのURL
  timeout: 300  # APIタイムアウト（秒）
  summary_config:
    language: "japanese"  # 要約言語
    summary_type: "detailed"  # 要約タイプ（concise, detailed, academic）
    max_length: 800  # 最大文字数
    include_translation: true  # 英日翻訳を含める
    focus_areas:  # 重点分析領域
      - "key_findings"
      - "document_categories" 
      - "source_comparison"
      - "technical_insights"
```

### 3. 使用方法

#### 基本的な使用
```bash
# LLM要約機能を有効にしてスクレイピング実行
python -m src.main

# LLM要約なしで実行（従来通り）
# config/settings.yamlでllm_api.enabled: falseに設定
```

#### メール通知での確認
- LLM要約が生成された場合、メール本文に AI要約レポートが含まれます
- 日本語要約、主要な知見、統計情報が自動的に追加されます

### 4. APIエンドポイント仕様

LocalLLM APIサーバーが提供すべきエンドポイント：

```http
# ヘルスチェック
GET /health

# 要約生成
POST /api/v1/summarize
Content-Type: application/json

{
  "data": {
    "text": "要約対象のテキスト",
    "metadata": {...}
  },
  "config": {
    "language": "japanese",
    "summary_type": "detailed",
    "max_length": 800,
    "include_translation": true,
    "focus_areas": [...]
  }
}
```

### 5. エラーハンドリング

- LocalLLM APIサーバーが利用できない場合、フォールバック要約を生成
- タイムアウト発生時は警告ログを出力し、処理は継続
- LLM要約の失敗はスクレイピング全体の処理に影響しません

## 技術的詳細

### 実装ファイル

1. **src/utils/llm_api_client.py**: LocalLLM APIクライアント
2. **src/main.py**: LLM要約機能を統合したメインワークフロー  
3. **src/utils/email_sender.py**: LLM要約対応のメール送信
4. **config/settings.yaml**: LLM API設定

### フロー

1. スクレイピング実行
2. 結果をJSON形式に変換
3. LocalLLM APIに送信
4. AI要約・日本語翻訳を取得
5. メール通知に含めて送信

### CPU最適化

- LocalLLM側でCPU専用実行を設定
- 推論時間を考慮したタイムアウト設定（5分）
- メモリ使用量の制限

## トラブルシューティング

### APIサーバー接続エラー
```bash
# LocalLLMサーバーの状態確認
curl http://localhost:8000/health
```

### メモリ不足
- LocalLLMの設定でメモリ使用量を制限
- より軽量なモデルの使用を検討

### タイムアウト
- config/settings.yamlでtimeout値を調整
- LocalLLMサーバーのCPUスレッド数を最適化

## 今後の拡張

1. **バッチ処理**: 複数の要約リクエストを効率的に処理
2. **キャッシュ機能**: 類似の結果の要約をキャッシュ
3. **モデル選択**: 用途に応じたLLMモデルの動的選択
4. **多言語対応**: 英語以外の言語への翻訳対応

## 設定例

### 軽量設定（低スペックPC向け）
```yaml
llm_api:
  enabled: true
  timeout: 600  # 10分
  summary_config:
    summary_type: "concise"
    max_length: 400
```

### 高性能設定（高スペックPC向け）
```yaml
llm_api:
  enabled: true
  timeout: 180  # 3分
  summary_config:
    summary_type: "academic"
    max_length: 1200
```

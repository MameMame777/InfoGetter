# 🚨 PROJECT REQUIREMENTS - 絶対に変更不可 🚨

## ⚠️ 重要な制約事項 ⚠️

### LLMライブラリ要件
- **使用必須ライブラリ**: `https://github.com/MameMame777/LocalLLM`
- **変更禁止**: 他のLLMライブラリ（llama-cpp-python、transformers等）への変更は禁止
- **理由**: プロジェクト仕様として指定されたライブラリ

### システム要件
1. Web scrapingした情報をJSONにまとめる
2. JSONをLLM（LocalLLM）に渡し、要約のMarkdownが生成される  
3. その要約と収集した情報の概要をメールで送る

### 安全要件
- LLMエラー時はメール送信を絶対に行わない（重大なクレーム防止）
- `email_safe=True`の場合のみメール送信可能

## 🔒 変更履歴
- 2025-08-23: 初回作成（LocalLLM要件の明文化）

## ⚡ エンジニア向け注意事項
**このファイルを必ず読んでから作業を開始すること**
**要件変更時は必ずクライアント確認を取ること**

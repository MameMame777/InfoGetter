# LocalLLM 手動統合ガイド

## 🚨 **Issue報告済み**

LocalLLMリポジトリのpip installに関する問題をGitHub Issueで報告しました。
- **Issue**: https://github.com/MameMame777/LocalLLM/issues/1

## 🔧 **現在の手動統合方法**

### 1. LocalLLMリポジトリをクローン

```bash
cd e:\Nautilus\workspace\pythonworks
git clone https://github.com/MameMame777/LocalLLM.git
```

### 2. LLMSummarizerを更新

InfoGetterの`src/utils/llm_summarizer.py`を以下のように修正：

```python
import sys
from pathlib import Path

class LLMSummarizer:
    def __init__(self):
        # LocalLLMパスを設定
        self.localllm_path = Path("../LocalLLM")
        if not self.localllm_path.exists():
            raise FileNotFoundError("LocalLLM repository not found. Please clone it manually.")
        
        # Pythonパスに追加
        if str(self.localllm_path) not in sys.path:
            sys.path.insert(0, str(self.localllm_path))
        
        # LocalLLM APIをインポート
        try:
            from src.api.enhanced_api import summarize_json, SummaryConfig
            self.summarize_json = summarize_json
            self.SummaryConfig = SummaryConfig
        except ImportError as e:
            raise ImportError(f"Failed to import LocalLLM: {e}")
```

### 3. 設定ファイル更新

`config/settings.yaml`：

```yaml
llm_integration:
  enabled: true
  method: "manual_path"  # pip_package | manual_path
  localllm_path: "../LocalLLM"
  summary_config:
    language: "ja"
    summary_type: "detailed"
    max_length: 2000
```

## 🎯 **将来の改善予定**

LocalLLMの作者が以下のいずれかを実装すれば、pip installが可能になります：

1. **適切なパッケージ構造**
   - `__init__.py`ファイルの追加
   - setup.pyの簡素化

2. **外部統合用パッケージ**
   - 軽量版パッケージの作成
   - コア機能のみの分離

3. **統合ドキュメント**
   - 公式の統合ガイド
   - ベストプラクティス

## 🤝 **コミュニティ協力**

この問題の解決にはコミュニティの協力が重要です：

- ⭐ LocalLLMリポジトリにスター
- 👍 Issueにリアクション
- 💬 統合ニーズの共有

---

**LocalLLMは素晴らしいプロジェクトです。統合問題が解決されれば、より多くのプロジェクトで活用できるようになります！**

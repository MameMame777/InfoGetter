#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開発日記作成ツール
./diary/{date}.md形式で技術的な知見や学びを含めて、日々の進捗を記録する
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

class DevelopmentDiary:
    def __init__(self, base_dir="./diary"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_diary_entry(self, date=None, template_type="default"):
        """
        指定した日付の開発日記を作成する
        
        Args:
            date (str, optional): YYYY-MM-DD形式の日付。Noneの場合は今日の日付
            template_type (str): テンプレートタイプ ("default", "detailed", "simple")
        
        Returns:
            str: 作成されたファイルのパス
        """
        if date is None:
            target_date = datetime.now()
        else:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        
        date_str = target_date.strftime("%Y-%m-%d")
        file_path = self.base_dir / f"{date_str}.md"
        
        # テンプレートを選択
        content = self._get_template(date_str, template_type)
        
        # ファイルが既に存在する場合の処理
        if file_path.exists():
            print(f"⚠️  日記ファイルが既に存在します: {file_path}")
            response = input("上書きしますか？ (y/N): ")
            if response.lower() != 'y':
                print("キャンセルしました。")
                return str(file_path)
        
        # ファイルを作成
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ 開発日記が作成されました: {file_path}")
        return str(file_path)
    
    def _get_template(self, date_str, template_type):
        """テンプレートを取得する"""
        day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        
        templates = {
            "default": self._default_template(date_str, day_of_week),
            "detailed": self._detailed_template(date_str, day_of_week),
            "simple": self._simple_template(date_str, day_of_week)
        }
        
        return templates.get(template_type, templates["default"])
    
    def _default_template(self, date_str, day_of_week):
        return f"""# 開発日記 - {date_str} ({day_of_week})

## 📈 今日の進捗
- [ ] **メインタスク**: 
- [ ] **サブタスク**: 
- [ ] **学習項目**: 

## 🔍 技術的な知見
### 新しく学んだこと
- 

### 解決した課題
- **問題**: 
- **解決方法**: 
- **参考資料**: 

### 使用した技術・ツール
- 

## 💡 気づき・アイデア
- 

## 📝 明日の予定
- [ ] 
- [ ] 
- [ ] 

## 🔗 参考リンク
- 

---
*作成日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    def _detailed_template(self, date_str, day_of_week):
        return f"""# 📊 詳細開発日記 - {date_str} ({day_of_week})

## ⏰ 作業時間
- **開始時刻**: 
- **終了時刻**: 
- **実作業時間**: 

## 🎯 目標と達成度
### 今日の目標
1. 
2. 
3. 

### 達成度 (%)
- 目標1: ___%
- 目標2: ___%
- 目標3: ___%

## 📈 詳細進捗
### 完了したタスク
- ✅ 
- ✅ 

### 進行中のタスク
- 🔄 
- 🔄 

### 未着手のタスク
- ⭕ 
- ⭕ 

## 🛠️ 技術的詳細
### 実装内容
```python
# 今日書いたコードの例
```

### 設計・アーキテクチャ
- 

### パフォーマンス・最適化
- 

## 🐛 問題と解決
### 発生した問題
1. **問題**: 
   - **原因**: 
   - **解決策**: 
   - **学び**: 

## 📚 学習内容
### 新技術・フレームワーク
- 

### ドキュメント・記事
- 

### コードレビュー・参考実装
- 

## 🔄 振り返り
### 良かった点
- 

### 改善点
- 

### 明日への改善アクション
- 

## 📋 明日の計画
### 優先タスク
1. 
2. 
3. 

### 学習予定
- 

---
*作成日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    def _simple_template(self, date_str, day_of_week):
        return f"""# {date_str} ({day_of_week})

## 今日やったこと
- 

## 学んだこと
- 

## 明日やること
- 

---
"""
    
    def list_entries(self, days=7):
        """過去の日記エントリーを一覧表示"""
        entries = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            file_path = self.base_dir / f"{date_str}.md"
            
            if file_path.exists():
                entries.append(f"✅ {date_str} - {file_path}")
            else:
                entries.append(f"❌ {date_str} - 未作成")
        
        return entries
    
    def generate_weekly_summary(self):
        """週次サマリーを生成"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        summary_content = f"""# 週次サマリー ({week_start.strftime("%Y-%m-%d")} - {today.strftime("%Y-%m-%d")})

## 今週の主な成果
- 

## 技術的な成長
- 

## 来週の目標
- 

## 参考リンク・資料
- 

"""
        
        summary_path = self.base_dir / f"weekly_summary_{week_start.strftime('%Y-%m-%d')}.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
        
        print(f"✅ 週次サマリーが作成されました: {summary_path}")
        return str(summary_path)

def main():
    """メイン関数 - コマンドライン引数を処理"""
    diary = DevelopmentDiary()
    
    if len(sys.argv) == 1:
        # 引数なしの場合は今日の日記を作成
        diary.create_diary_entry()
    elif sys.argv[1] == "list":
        # 過去の日記を一覧表示
        entries = diary.list_entries()
        print("\n📋 過去7日間の日記:")
        for entry in entries:
            print(f"  {entry}")
    elif sys.argv[1] == "weekly":
        # 週次サマリーを作成
        diary.generate_weekly_summary()
    elif sys.argv[1] == "detailed":
        # 詳細テンプレートで作成
        diary.create_diary_entry(template_type="detailed")
    elif sys.argv[1] == "simple":
        # シンプルテンプレートで作成
        diary.create_diary_entry(template_type="simple")
    else:
        # 特定の日付を指定
        try:
            diary.create_diary_entry(date=sys.argv[1])
        except ValueError:
            print("❌ 日付形式が正しくありません。YYYY-MM-DD形式で入力してください。")
            print("\n使用方法:")
            print("  python create_diary.py                    # 今日の日記を作成")
            print("  python create_diary.py 2023-10-15         # 特定の日付の日記を作成")
            print("  python create_diary.py detailed           # 詳細テンプレートで作成")
            print("  python create_diary.py simple             # シンプルテンプレートで作成")
            print("  python create_diary.py list               # 過去の日記を一覧表示")
            print("  python create_diary.py weekly             # 週次サマリーを作成")

if __name__ == "__main__":
    main()
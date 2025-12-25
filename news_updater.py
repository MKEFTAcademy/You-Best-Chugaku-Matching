#!/usr/bin/env python3
"""
script.js更新スクリプト
new_news.jsonからニュースを読み込み、script.jsに追加
"""
import json
import re
from datetime import datetime

# ========================================
# 設定
# ========================================
SCRIPT_JS_PATH = "script.js"
NEW_NEWS_JSON = "new_news.json"
MAX_NEWS_COUNT = 250  # 最大ニュース数（古いニュースは自動削除）

# ========================================
# ニュース読み込み
# ========================================
def load_new_news():
    """新しいニュースをJSONから読み込み"""
    try:
        with open(NEW_NEWS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  {NEW_NEWS_JSON} が見つかりません")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSONパースエラー: {e}")
        return []

def load_existing_news():
    """script.jsから既存のニュースを読み込み"""
    try:
        with open(SCRIPT_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # newsDataの配列部分を抽出
        match = re.search(r'const newsData = (\[.*?\]);', content, re.DOTALL)
        if match:
            news_array_str = match.group(1)
            # JavaScriptの配列をPythonで評価可能な形式に変換
            news_array_str = news_array_str.replace("'", '"')
            news_data = json.loads(news_array_str)
            return news_data
        else:
            print("⚠️  newsData が見つかりません")
            return []
            
    except FileNotFoundError:
        print(f"⚠️  {SCRIPT_JS_PATH} が見つかりません")
        return []
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []

# ========================================
# ニュース更新
# ========================================
def update_script_js(new_news):
    """script.jsを更新"""
    
    if not new_news:
        print("⚠️  新しいニュースがありません")
        return False
    
    # 既存のニュースを読み込み
    existing_news = load_existing_news()
    print(f"📰 既存ニュース: {len(existing_news)}件")
    
    # 重複チェック（URLベース）
    existing_urls = {news.get("url") for news in existing_news if news.get("url")}
    
    unique_new_news = []
    for news in new_news:
        if news.get("url") not in existing_urls:
            unique_new_news.append(news)
    
    print(f"📰 新規ニュース: {len(unique_new_news)}件")
    
    if not unique_new_news:
        print("✅ 新しいニュースはありません（重複）")
        return False
    
    # ニュースを統合（新しいニュースを先頭に追加）
    all_news = unique_new_news + existing_news
    
    # 最大数を超える場合は古いニュースを削除
    if len(all_news) > MAX_NEWS_COUNT:
        all_news = all_news[:MAX_NEWS_COUNT]
        print(f"⚠️  古いニュースを削除: {len(existing_news) + len(unique_new_news) - MAX_NEWS_COUNT}件")
    
    # script.jsを読み込み
    with open(SCRIPT_JS_PATH, "r", encoding="utf-8") as f:
        script_content = f.read()
    
    # newsData配列を置換
    news_data_str = json.dumps(all_news, ensure_ascii=False, indent=4)
    
    # JavaScriptの形式に変換（ダブルクォートをシングルクォートに）
    news_data_str = news_data_str.replace('"', "'")
    
    # 置換
    new_content = re.sub(
        r'const newsData = \[.*?\];',
        f'const newsData = {news_data_str};',
        script_content,
        flags=re.DOTALL
    )
    
    # 保存
    with open(SCRIPT_JS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✅ script.jsを更新しました")
    print(f"   - 新規追加: {len(unique_new_news)}件")
    print(f"   - 合計: {len(all_news)}件")
    
    return True

# ========================================
# 実行
# ========================================
if __name__ == "__main__":
    print("=" * 70)
    print("script.js 更新処理")
    print("=" * 70)
    
    # 新しいニュースを読み込み
    new_news = load_new_news()
    
    if not new_news:
        print("❌ 新しいニュースが見つかりません")
        exit(1)
    
    # script.jsを更新
    success = update_script_js(new_news)
    
    if success:
        print("\n✅ 更新完了")
    else:
        print("\n⚠️  更新不要")

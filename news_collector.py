#!/usr/bin/env python3
"""
ニュース収集・要約スクリプト
Google Custom Search APIで最新ニュースを検索し、Claude APIで要約を生成
"""
import os
import json
import requests
from datetime import datetime, timedelta
from anthropic import Anthropic

# ========================================
# 設定
# ========================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

# 検索キーワード
SEARCH_QUERIES = [
    "中学受験 入試 site:diamond.jp OR site:resemom.jp OR site:inter-edu.com",
    "中学校 説明会 site:resemom.jp OR site:inter-edu.com",
    "私立中学 偏差値 site:syutoken-mosi.co.jp OR site:inter-edu.com"
]

# ========================================
# Google Custom Search
# ========================================
def search_news(query, days_back=1):
    """Google Custom Searchでニュースを検索"""
    
    # 日付フィルター（過去N日間）
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query,
        "dateRestrict": f"d{days_back}",
        "num": 5,  # 1クエリあたり5件
        "sort": "date"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("displayLink", "")
                })
        
        return results
        
    except Exception as e:
        print(f"❌ 検索エラー: {e}")
        return []

# ========================================
# Claude API要約
# ========================================
def summarize_with_claude(title, snippet, source):
    """Claude APIでニュースを要約"""
    
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""以下の中学受験ニュースを、保護者向けに100文字以内で要約してください。
重要なポイントを簡潔にまとめてください。

タイトル: {title}
内容: {snippet}
情報源: {source}

要約（100文字以内）:"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        summary = message.content[0].text.strip()
        return summary
        
    except Exception as e:
        print(f"❌ 要約エラー: {e}")
        return snippet[:100] + "..."

# ========================================
# カテゴリ分類
# ========================================
def categorize_news(title, snippet):
    """ニュースをカテゴリに分類"""
    
    text = (title + " " + snippet).lower()
    
    if any(word in text for word in ["入試", "受験", "試験", "合格", "倍率", "難易度"]):
        return "entrance"
    elif any(word in text for word in ["学校", "説明会", "文化祭", "オープン", "見学"]):
        return "school"
    elif any(word in text for word in ["勉強", "学習", "対策", "教材", "塾"]):
        return "study"
    else:
        return "entrance"

# ========================================
# メイン処理
# ========================================
def collect_news():
    """ニュースを収集して整形"""
    
    print("=" * 70)
    print("ニュース収集開始")
    print("=" * 70)
    
    all_news = []
    seen_urls = set()
    
    # 各検索クエリでニュースを収集
    for query in SEARCH_QUERIES:
        print(f"\n🔍 検索中: {query[:50]}...")
        results = search_news(query, days_back=1)
        
        for result in results:
            # 重複チェック
            if result["link"] in seen_urls:
                continue
            seen_urls.add(result["link"])
            
            # 要約生成
            print(f"📝 要約生成中: {result['title'][:50]}...")
            summary = summarize_with_claude(
                result["title"],
                result["snippet"],
                result["source"]
            )
            
            # カテゴリ分類
            category = categorize_news(result["title"], result["snippet"])
            
            # ニュースオブジェクト作成
            news_item = {
                "id": len(all_news) + 300,  # 既存ニュースと重複しないID
                "title": result["title"],
                "summary": summary,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": category,
                "source": result["source"],
                "url": result["link"]
            }
            
            all_news.append(news_item)
            print(f"✅ 追加: {news_item['title'][:50]}...")
    
    print("\n" + "=" * 70)
    print(f"📊 収集結果: {len(all_news)}件の新しいニュース")
    print("=" * 70)
    
    return all_news

# ========================================
# 実行
# ========================================
if __name__ == "__main__":
    # 環境変数チェック
    if not ANTHROPIC_API_KEY:
        print("❌ エラー: ANTHROPIC_API_KEY が設定されていません")
        exit(1)
    
    if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        print("❌ エラー: Google Search API設定が不完全です")
        exit(1)
    
    # ニュース収集
    news = collect_news()
    
    # JSONファイルに保存
    with open("new_news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ new_news.json に保存しました（{len(news)}件）")

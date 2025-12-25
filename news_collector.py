#!/usr/bin/env python3
"""
中学受験ニュース収集スクリプト
Google Custom Search APIでニュースを検索し、Claude APIで要約
"""
import os
import json
import requests
from datetime import datetime, timedelta
from anthropic import Anthropic

# ========================================
# API設定
# ========================================
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')

# ========================================
# 検索設定
# ========================================
SEARCH_QUERIES = [
    "中学受験 入試",
    "中学入試 2026",
    "私立中学 募集",
    "中学受験 説明会"
]

# ========================================
# 関数定義
# ========================================
def search_news(query, num_results=3):
    """Google Custom Search APIでニュースを検索"""
    url = "https://www.googleapis.com/customsearch/v1"
    
    # 過去7日間の記事に限定
    date_restrict = "d7"
    
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_SEARCH_ENGINE_ID,
        'q': query,
        'num': num_results,
        'dateRestrict': date_restrict,
        'sort': 'date'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 検索エラー: {e}")
        return None

def summarize_with_claude(title, snippet, link):
    """Claude APIで記事を要約"""
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""以下のニュース記事を、中学受験を考えている保護者向けに100文字以内で簡潔に要約してください。
要約のみを出力し、前置きや説明は不要です。

タイトル: {title}
概要: {snippet}
URL: {link}

要約:"""
        
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
        print(f"❌ Claude API エラー: {e}")
        return snippet[:100] + "..."

def collect_news():
    """ニュースを収集して整形"""
    print("=" * 80)
    print("ニュース収集開始")
    print("=" * 80)
    
    all_articles = []
    seen_urls = set()
    
    for query in SEARCH_QUERIES:
        print(f"\n🔍 検索中: {query}")
        results = search_news(query)
        
        if not results or 'items' not in results:
            print(f"   ⚠️  結果なし")
            continue
        
        for item in results['items']:
            url = item.get('link', '')
            
            # 重複チェック
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            
            print(f"\n📰 要約作成中: {title[:50]}...")
            summary = summarize_with_claude(title, snippet, url)
            
            # 記事データを作成
            article = {
                'title': title,
                'summary': summary,
                'source': extract_source(url),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'url': url,
                'category': 'entrance'  # デフォルトカテゴリ
            }
            
            all_articles.append(article)
            print(f"   ✅ 完了")
    
    print(f"\n📊 収集完了: {len(all_articles)}件")
    print("=" * 80)
    
    return all_articles

def extract_source(url):
    """URLからソース名を抽出"""
    if 'resemom.jp' in url:
        return 'リセマム'
    elif 'inter-edu.com' in url:
        return 'インターエデュ'
    elif 'diamond.jp' in url:
        return 'ダイヤモンド・オンライン'
    elif 'president.jp' in url:
        return 'プレジデントオンライン'
    elif 'benesse.jp' in url:
        return 'ベネッセ教育情報サイト'
    elif 'asahi.com' in url:
        return '朝日新聞デジタル'
    elif 'yomiuri.co.jp' in url:
        return '読売新聞オンライン'
    elif 'mainichi.jp' in url:
        return '毎日新聞'
    elif 'nikkei.com' in url:
        return '日本経済新聞'
    elif 'kyoiku-press.com' in url:
        return '教育新聞'
    elif 'ict-enews.net' in url:
        return 'ICT教育ニュース'
    elif 'kyobun.co.jp' in url:
        return '教育新聞'
    elif 'kodomo-it.net' in url:
        return '子供とIT'
    elif 'edtechzine.jp' in url:
        return 'EdTechZine'
    elif 'mext.go.jp' in url:
        return '文部科学省'
    elif 'syutoken-mosi.co.jp' in url:
        return '首都圏模試センター'
    elif 'sapix.co.jp' in url:
        return 'SAPIX'
    elif 'nichinoken.co.jp' in url:
        return '日能研'
    elif 'yotsuyaotsuka.com' in url:
        return '四谷大塚'
    elif 'school21.jp' in url:
        return 'スクール21'
    elif 'tomas.co.jp' in url:
        return 'TOMAS'
    elif 'miraino.org' in url:
        return '未来の学校'
    elif 'study1.jp' in url:
        return 'スタディ1'
    else:
        return 'その他'

# ========================================
# メイン処理
# ========================================
if __name__ == "__main__":
    # API キーの確認
    if not all([ANTHROPIC_API_KEY, GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID]):
        print("❌ エラー: APIキーが設定されていません")
        exit(1)
    
    # ニュース収集
    articles = collect_news()
    
    # JSON出力
    output_file = 'news_articles.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ ニュースを {output_file} に保存しました")
    print(f"📝 収集記事数: {len(articles)}件")


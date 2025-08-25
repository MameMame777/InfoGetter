import requests
import xml.etree.ElementTree as ET
import json

def fetch_arxiv_recent_papers(category, max_results=10):
    """arXiv APIから指定カテゴリの直近の論文を取得"""
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    
    # XMLレスポンスを解析
    root = ET.fromstring(response.text)
    papers = []
    
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
        abstract = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        link = entry.find("{http://www.w3.org/2005/Atom}id").text.strip()
        papers.append({"title": title, "abstract": abstract, "link": link})
    
    return papers

def save_to_json(data, filename="arxiv_recent_papers.json"):
    """データをJSON形式で保存"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_previous_results(filename="arxiv_previous_papers.json"):
    """前回の結果を読み込む"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None  # 初回実行時はNoneを返す

def save_results(data, filename="arxiv_previous_papers.json"):
    """結果を保存"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def calculate_diff(new_results, previous_results):
    """新しい結果と前回の結果の差分を計算"""
    previous_links = {paper["link"] for paper in previous_results}
    diff = [paper for paper in new_results if paper["link"] not in previous_links]
    return diff

if __name__ == "__main__":
    category = "cs.AR"  # Hardware Architecture
    category = "cs.AI"  # Artificial Intelligence
    
    papers = fetch_arxiv_recent_papers(category, max_results=10)
    save_to_json(papers)
    print(f"Saved {len(papers)} papers to arxiv_recent_papers.json")

    # 新しい結果を取得（例: APIから取得した結果）
    new_results = [

    ]

    # 前回の結果を読み込む
    previous_results = load_previous_results()

    if previous_results is None:
        # 初回実行時は差分を生成せず、新しい結果を保存
        save_results(new_results)
        print("Initial execution: Saved all results as previous results.")
    else:
        # 差分を計算
        diff = calculate_diff(new_results, previous_results)

        # 差分を保存
        save_results(new_results)  # 新しい結果を保存
        with open("arxiv_diff_papers.json", "w", encoding="utf-8") as f:
            json.dump(diff, f, ensure_ascii=False, indent=4)

        print(f"Saved {len(diff)} new papers to arxiv_diff_papers.json")
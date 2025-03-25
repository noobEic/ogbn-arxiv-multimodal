import os
import requests
import feedparser
from urllib.parse import urlencode
from dotenv import load_dotenv
import time

load_dotenv() 

ARXIV_API_URL = "http://export.arxiv.org/api/query?"

def search_arxiv(title, max_results=3):
    query = {
        "search_query": f'{title}',
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(ARXIV_API_URL + urlencode(query))
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        if len(feed.entries) == 0:
            return None
            
        # 返回最相关的结果
        return {
            "id": feed.entries[0].id.split("/abs/")[-1],
            "title": feed.entries[0].title,
            "published": feed.entries[0].published
        }
        
    except Exception as e:
        print(f"搜索失败: {str(e)}")
        return None

def download_tex(arxiv_id, output_dir="downloads"):
    """下载TeX源代码"""
    tex_url = f"https://arxiv.org/src/{arxiv_id}"
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        response = requests.get(tex_url)
        response.raise_for_status()
        
                
        filename = os.path.join(output_dir, f"{arxiv_id}.tar.gz")
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
        
            
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return None

def download_by_title(title, output_dir,delay=20):


    """主函数"""
    # 搜索论文
    paper = search_arxiv(title)
    if not paper:
        print("未找到匹配论文")
        return None
    print(f"找到论文: {paper['title']} (ID: {paper['id']})")
    
    # 遵守API速率限制
    time.sleep(delay)  
    
    # 下载源代码
    path = download_tex(paper['id'],output_dir)
    if path:
        print(f"已下载到: {path}")
        return path
    return None

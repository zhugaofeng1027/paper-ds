import argparse
import requests
from bs4 import BeautifulSoup
import os
from typing import List, Optional


# 预置的 CSS 选择器模板
SELECTOR_PRESETS = {
    "acl": "p.d-sm-flex strong a",           # ACL Anthology
    "arxiv": "p.list-title a",                # arXiv 搜索结果
    "semantic": "a.cl-paper-title",           # Semantic Scholar
    "default": "a",                            # 通用：所有链接
    "cvpr": "dt.ptitle > a",                 # cvpr式
    "nips": "li a"                          # nips式子
}


def scrape_papers(
    url: str,
    keywords: List[str],
    output_file: str,
    selector: str = "acl",
    match_any: bool = True,
    case_sensitive: bool = False,
) -> List[str]:
    """
    通用论文爬虫函数
    
    Args:
        url: 目标网页 URL
        keywords: 关键词列表
        output_file: 输出文件路径
        selector: CSS 选择器（可用预设名或自定义选择器）
        match_any: True=匹配任一关键词, False=需匹配所有关键词
        case_sensitive: 是否区分大小写
    
    Returns:
        匹配到的论文标题列表
    """
    # 解析选择器
    css_selector = SELECTOR_PRESETS.get(selector, selector)
    
    print(f"正在抓取: {url}")
    print(f"关键词: {keywords}")
    print(f"CSS 选择器: {css_selector}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.select(css_selector)
        
        print(f"找到 {len(elements)} 个元素")
        
        matched_papers = []
        for element in elements:
            title = element.get_text(strip=True)
            if not title:
                continue
                
            # 关键词匹配
            check_title = title if case_sensitive else title.lower()
            check_keywords = keywords if case_sensitive else [k.lower() for k in keywords]
            
            if match_any:
                matched = any(kw in check_title for kw in check_keywords)
            else:
                matched = all(kw in check_title for kw in check_keywords)
            
            if matched:
                matched_papers.append(title)
        
        # 去重并保持顺序
        matched_papers = list(dict.fromkeys(matched_papers))
        
        # 写入文件
        output_path = os.path.abspath(output_file)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if matched_papers:
                f.write('\n'.join(matched_papers))
                print(f"\n✓ 找到 {len(matched_papers)} 篇匹配论文")
                print(f"✓ 结果已保存至: {output_path}")
            else:
                f.write("未找到匹配的论文")
                print("\n✗ 未找到匹配的论文")
        
        return matched_papers
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="通用学术论文爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 爬取 ACL 2023，搜索 agent 相关论文
  python spider_acl.py -u "https://aclanthology.org/events/acl-2023/" -k agent
  
  # 多关键词搜索（OR 逻辑）
  python spider_acl.py -u URL -k agent llm reasoning
  
  # 多关键词搜索（AND 逻辑）
  python spider_acl.py -u URL -k agent llm --match-all
  
  # 使用自定义 CSS 选择器
  python spider_acl.py -u URL -k agent -s "div.title a"
  
预置选择器:
  acl      - ACL Anthology (默认)
  arxiv    - arXiv 搜索结果
  semantic - Semantic Scholar
  default  - 通用链接选择器
        """
    )
    
    parser.add_argument("-u", "--url", required=True, help="目标网页 URL")
    parser.add_argument("-k", "--keywords", nargs="+", required=True, help="搜索关键词（空格分隔多个）")
    parser.add_argument("-o", "--output", default="matched_papers.txt", help="输出文件路径 (默认: matched_papers.txt)")
    parser.add_argument("-s", "--selector", default="acl", help="CSS 选择器或预设名 (默认: acl)")
    parser.add_argument("--match-all", action="store_true", help="需匹配所有关键词 (默认: 匹配任一)")
    parser.add_argument("--case-sensitive", action="store_true", help="区分大小写")
    
    args = parser.parse_args()
    
    scrape_papers(
        url=args.url,
        keywords=args.keywords,
        output_file=args.output,
        selector=args.selector,
        match_any=not args.match_all,
        case_sensitive=args.case_sensitive,
    )


if __name__ == "__main__":
    # pip install requests beautifulsoup4
    main()
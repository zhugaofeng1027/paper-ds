import requests
from bs4 import BeautifulSoup
import os
import time

def scrape_neurips_papers():
    """
    Scrapes NeurIPS papers page for titles containing "Agent"
    and saves results to a text file.
    """
    # URL provided by user
    # Nips
    # url = "https://neurips.cc/virtual/2025/loc/san-diego/papers.html?search=Agent"
    # url = "https://neurips.cc/virtual/2024/loc/san-diego/papers.html?search=Agent"
    # url = "https://neurips.cc/virtual/2023/loc/san-diego/papers.html?search=Agent"

    # ICML
    # url = "https://icml.cc/virtual/2025/papers.html?search=Agent"
    # url = "https://icml.cc/virtual/2024/papers.html?search=Agent"
    # url = "https://icml.cc/virtual/2023/papers.html?search=Agent"

    # ICLR
    # url = "https://iclr.cc/virtual/2024/papers.html?filter=titles&search=Agent"
    # url = "https://iclr.cc/virtual/2023/papers.html?filter=titles&search=Agent"

    # ECCV
    url = "https://eccv.ecva.net/virtual/2024/papers.html?search=Agent"
    output_filename = "agent_papers_eccv2024.txt"
    output_filepath = os.path.join(os.getcwd(), output_filename)
    
    print(f"Fetching papers from {url}...")
    
    try:
        # Add headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        
        # Add a small delay to be polite to the server
        time.sleep(2)
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Based on user feedback, the titles are in <a> tags within <li> tags.
        paper_links = soup.select('li a')
        
        agent_papers = []
        for link in paper_links:
            title = link.get_text(strip=True)
            # The search URL should already filter, but we double-check.
            if 'agent' in title.lower():
                agent_papers.append(title)

        # Filter out non-paper links if any (e.g., navigation links)
        # A simple heuristic: real paper titles are usually longer.
        agent_papers = [title for title in agent_papers if len(title) > 20]

        with open(output_filepath, 'w', encoding='utf-8') as f:
            if agent_papers:
                # Remove duplicates that might be caught by the selector
                agent_papers = sorted(list(set(agent_papers)))
                f.write('\n'.join(agent_papers))
                print(f"\nSuccessfully found {len(agent_papers)} papers with 'Agent' in the title.")
                print(f"Results have been saved to: {output_filepath}")
            else:
                f.write("No papers with 'Agent' in title found. The content might be loaded dynamically via JavaScript, which this script cannot handle.")
                print("\nNo matching papers found. This could be because:")
                print("1. The papers for NeurIPS 2025 are not yet published.")
                print("2. The page content is loaded dynamically (via JavaScript), which requires more advanced tools like Selenium to scrape.")
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Before running, please ensure you have installed the required libraries:
    # pip install requests beautifulsoup4
    scrape_neurips_papers()
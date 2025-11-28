import requests
from bs4 import BeautifulSoup
import os

def scrape_cvpr():
    """
    Scrapes the CVPR 2024 open access page to find papers with "Agent" in the title
    and saves them to a file.
    """
    # URL of the CVPR 2024 proceedings
    # Note: CVPR 2025 is a future event, so we are using CVPR 2024 instead.
    # CVPR
    # url = "https://openaccess.thecvf.com/CVPR2023?day=all"

    # ICCV
    url = "https://openaccess.thecvf.com/ICCV2023?day=all"
    output_filename = "agent_papers_iccv2023.txt"
    output_filepath = os.path.join(os.getcwd(), output_filename)

    print(f"Fetching papers from {url}...")

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Titles are in <a> tags within <dt> tags with class 'ptitle'
        paper_titles = soup.select('dt.ptitle > a')

        agent_papers = []
        for title_element in paper_titles:
            title = title_element.get_text(strip=True)
            if 'agent' in title.lower():
                agent_papers.append(title)

        # Write the found titles to the output file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            if agent_papers:
                f.write('\n'.join(agent_papers))
                print(f"\nSuccessfully found {len(agent_papers)} papers with 'Agent' in the title.")
                print(f"Results have been saved to: {output_filepath}")
            else:
                f.write("No papers with 'Agent' in the title were found.")
                print("\nNo papers with 'Agent' in the title were found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Before running, please ensure you have installed the required libraries:
    # pip install requests beautifulsoup4
    scrape_cvpr()
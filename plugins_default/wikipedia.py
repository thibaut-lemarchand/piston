import requests
from bs4 import BeautifulSoup

# Define the website name and URL as constants
WEBSITE_NAME = "Wikipedia"
WEBSITE_URL = "https://en.wikipedia.org/wiki/Main_Page"


def scrape(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all links on the page
        all_links = soup.find_all("a")
        links_with_descriptions = []

        for link in all_links:
            href = link.get("href")
            description = link.text.strip()
            if href and not href.startswith("#"):
                links_with_descriptions.append((href, description))

        # Remove duplicates while preserving order
        unique_links_with_descriptions = list(dict.fromkeys(links_with_descriptions))

        return {
            "link_count": len(unique_links_with_descriptions),
            "links_with_descriptions": unique_links_with_descriptions,
        }
    except Exception as e:
        print(f"Error scraping Wikipedia: {e}")
        return None

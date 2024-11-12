import re
import requests
from bs4 import BeautifulSoup

# Define the website name and URL as constants
WEBSITE_NAME = "OCDE"
WEBSITE_URL = (
    "https://careers.smartrecruiters.com/OECD/oecd---fr?search=data%20donn%C3%A9es"
)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def extract_job_offer_number(url):
    pattern = r"/OECD/(\d+)-"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def extract_offers_info(offer_block):
    offers = []
    for offer in offer_block.find_all(
        "li", class_="opening-job job column wide-7of16 medium-1of2"
    ):
        job_name = offer.find("h4", class_="job-title").text.strip()
        url = offer.find("a", class_="details")["href"].strip()
        location = offer.find("p", class_="job-desc").text.strip()
        offer_id = extract_job_offer_number(url)

        offers.append((offer_id, "\n".join([job_name, location, url]) + "\n"))
    return offers


def scrape(url):
    try:
        response = requests.request("GET", url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        offers = []
        for ul_element in soup.find_all(
            "ul", class_="opening-jobs grid--gutter padding--none js-group-list"
        ):
            offers.extend(extract_offers_info(ul_element))

        return {"link_count": len(offers), "links_with_descriptions": offers}
    except Exception as e:
        return str(e)

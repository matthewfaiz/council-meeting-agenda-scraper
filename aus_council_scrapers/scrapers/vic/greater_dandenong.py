from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper
from bs4 import BeautifulSoup
import re
from datetime import datetime

@register_scraper
class GreaterDandenongScraper(BaseScraper):
    def __init__(self):
        council_name = "greater_dandenong"
        state = "VIC"
        base_url = "https://www.greaterdandenong.vic.gov.au/"
        super().__init__(council_name, state, base_url)
        self.default_location = "Dandenong Civic Centre, 225 Lonsdale Street, Dandenong"
        self.default_time = "19.00"
    
    def scraper(self) -> ScraperReturn | None:
        initial_webpage_url = "https://www.greaterdandenong.vic.gov.au/council-meetings"

        # Find url of next meeting
        raw_html = self.fetcher.fetch_with_requests(initial_webpage_url)
        init_soup = BeautifulSoup(raw_html, "html.parser")
        meeting_a = init_soup.find("div", class_="field__item-label-hidden").find("a")
        meeting_url = meeting_a["href"]

        # Parse html of next meeting
        meeting_html = self.fetcher.fetch_with_requests(meeting_url)
        meeting_soup = BeautifulSoup(meeting_html, "html.parser")

        # Extract variables
        name = meeting_soup.find("h1").text
        date_str = re.search(self.date_regex, name).group()
        download_a = meeting_soup.find("div", class_="file--mime-application-pdf").find("a")
        download_url = download_a["href"]

        
        return ScraperReturn(
            name = name,
            date = date_str,
            time = None,
            webpage_url = meeting_url,
            download_url = download_url
        )

if __name__ == "__main__":
    scraper = GreaterDandenongScraper()
    scraper.scraper()
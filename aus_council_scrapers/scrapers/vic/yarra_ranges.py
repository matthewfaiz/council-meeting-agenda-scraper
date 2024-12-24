from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper
from bs4 import BeautifulSoup
import re
from datetime import datetime

@register_scraper
class YarraRangesScraper(BaseScraper):
    def __init__(self):
        council_name = "yarra_ranges"
        state = "VIC"
        base_url = "https://yarraranges.moderngov.com.au/"
        super().__init__(council_name, state, base_url)
        self.date_pattern = re.compile(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday).+\d{1,2}[dhnst]{2}.+(January|February|March|April|May|June|July|August|September|October|November|December).+\d{4}")
        self.time_pattern = re.compile(r"\d{1,2}\.\d{2}\s[APap]{1}[Mm]{1}")
    
    def scraper(self) -> ScraperReturn | None:
        initial_webpage_url = "https://www.yarraranges.vic.gov.au/Council/Council-meetings/Council-Meeting-Minutes-Agendas"

        # Find url of next meeting
        raw_html = self.fetcher.fetch_with_requests(initial_webpage_url)
        init_soup = BeautifulSoup(raw_html, "html.parser")
        meetings = init_soup.find("ul", class_="mgNonBulletTableList") # might change code to use the text in the tag's sibling instead later
        meeting_obj = meetings.find(lambda x: x.name == "li" and 'Agenda' in x.text)
        meeting_a = meeting_obj.find("a")
        meeting_url = self.base_url + meeting_a["href"]

        # Parse html of next meeting
        meeting_html = self.fetcher.fetch_with_requests(meeting_url)
        meeting_soup = BeautifulSoup(meeting_html, "html.parser")

        # Extract variables
        name = meeting_soup.find("a", title="Link to Council Meeting").text # think about adding some sort of a "name pattern" to eliminate date & time from name
        print(name)
        date_str = self.date_pattern.search(name).group()
        print(date_str)
        time_str = self.time_pattern.search(name).group()
        print(time_str)
        download_a = meeting_soup.find(lambda y: y.name == "a" and 'Agenda frontsheet' in y.text)
        download_url = self.base_url + download_a["href"]
        print(download_url)
        
        return ScraperReturn(
            name = name,
            date = date_str,
            time = time_str,
            webpage_url = meeting_url, # check this again later
            download_url = download_url
        )

if __name__ == "__main__":
    scraper = YarraRangesScraper()
    scraper.scraper()
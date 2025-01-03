from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper
from bs4 import BeautifulSoup
import re

@register_scraper
class HumeScraper(BaseScraper):
    def __init__(self):
        council_name = "hume"
        state = "VIC"
        base_url = "https://www.hume.vic.gov.au/"
        super().__init__(council_name, state, base_url)
        self.date_pattern = r"\b(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})\b"
        self.time_pattern = r"\b(\d{1,2}:\d{2})\s(AM|PM)\b"
    
    def scraper(self) -> ScraperReturn | None:
        webpage_url = "https://www.hume.vic.gov.au/Your-Council/Council-Meetings/Agendas-Minutes-and-Meeting-Recordings"
        response = self.fetcher.fetch_with_requests(webpage_url)
        soup = BeautifulSoup(response, "html.parser")
        next_meeting_link = soup.find(
            "a", class_="accordion-trigger minutes-trigger ajax-trigger"
        )["href"]
        print(next_meeting_link)

        meeting_response = self.fetcher.fetch_with_requests(next_meeting_link)
        soup = BeautifulSoup(meeting_response, "html.parser")
        minutes_date = soup.find("span", class_="minutes-date")
        meeting_type = soup.find("span", class_="meeting-type")
        if minutes_date and meeting_type:  # Ensure both elements are found
            date = minutes_date.text.strip()
            name = meeting_type.text.strip()
        
        time_div = soup.find("div", class_="meeting-time")
        if time_div:
            time = time_div.text.strip()
            time = re.search(r"\d{1,2}:\d{2}\s(?:AM|PM)", time).group(0)
        else:
            self.logger.error("Meeting time not found.")
            time = None
        
        # Extract agenda PDF link
        agenda_div = soup.find("div", class_="meeting-attachments")
        agenda_link = agenda_div.find("a", class_="document ext-pdf")
        if agenda_link and "href" in agenda_link.attrs:
            download_url = agenda_link["href"]
            if not download_url.startswith("http"):
                download_url = (
                    "https://www.hume.vic.gov.au" + download_url
                )
            else:
                self.logger.error("Agenda link not found.")
                download_url = None
        
        scraper_return = ScraperReturn(name, date, time, self.base_url, download_url)
        print(scraper_return)
        return scraper_return


        

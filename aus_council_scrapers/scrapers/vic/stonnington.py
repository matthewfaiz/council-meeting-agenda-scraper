from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper
from bs4 import BeautifulSoup
import re


@register_scraper
class StonningtonScraper(BaseScraper):
    def __init__(self):
        council = "stonnington"
        state = "VIC"
        base_url = "https://www.stonnington.vic.gov.au/"
        super().__init__(council, state, base_url)
        self.webpage_url = "https://www.stonnington.vic.gov.au/About/About-Council/Council-meetings/Minutes-and-agendas"
        self.name = 'Council Meeting'
        self.time_pattern = re.compile(r"\d+:\d+\s?[apmAPM]+")

    def scraper(self) -> ScraperReturn | None:
        # Initialise driver

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        # Assign initial values to variables that will be returned 

        date = None
        meeting_time = None
        download_url = None

        # Retrieve webpage

        driver.get(self.webpage_url)
        driver.refresh()

        # Open accordions 

        elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'accordion-trigger')]")
        for element in elements:
            driver.execute_script("arguments[0].click();", element)

        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".accordion-list-item-container .initialised")
            )
        )

        output = driver.page_source
        driver.quit()

        soup = BeautifulSoup(output, "html.parser")

        meetings = soup.find_all("div", class_="accordion-list-item-container")

        # Extract variables from first meeting on the page

        for meeting in meetings:
            document_link = meeting.find("a", class_="document")["href"]
            if not document_link:
                continue

            date = meeting.find("span", class_="minutes-date").text
            time = meeting.find("div", class_="meeting-time").text

            if time:
                time_match = self.time_pattern.search(time)
                meeting_time = time_match.group()
                print(meeting_time)
            
            download_url = self.base_url + document_link
            print(download_url)
            break

        return ScraperReturn(
            name = self.name,
            date = date,
            time = meeting_time,
            webpage_url = self.webpage_url,
            download_url = download_url
        )

if __name__ == "__main__":
    scraper = StonningtonScraper()
    scraper.scraper()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import re

from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper


@register_scraper
class BanyuleScraper(BaseScraper):
    def __init__(self):
        council = "banyule"
        state = "VIC"
        base_url = "https://www.banyule.vic.gov.au"
        self.webpage_url = "https://www.banyule.vic.gov.au/About-us/Councillors-and-Council-meetings/Council-meetings/Council-meeting-agendas-and-minutes"
        super().__init__(council, state, base_url)
        self.time_pattern = re.compile(r"\d+:\d+\s?[apmAPM]+")

    def scraper(self) -> ScraperReturn | None:

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(self.webpage_url)

        # Reload the page, as the first time we visit javascript does not get loaded
        # for some reason
        driver.refresh()

        # Open all the accordions
        driver.execute_script(
            "Array.from(document.getElementsByClassName('accordion-trigger')).forEach(e => e.click())"
        )

        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".accordion-list-item-container .initialised")
            )
        )

        # Give a little time for all accordions to load, just in case. may not be necessary
        driver.implicitly_wait(2)

        # Get the HTML
        output = driver.page_source

        soup = self.html_soup(output)
     
        while not soup:
            button = driver.find_element(By.LINK_TEXT, "Next")
            if button:
                driver.execute_script("arguments[0].click()", button)
                driver.refresh()
                driver.execute_script(
                    "Array.from(document.getElementsByClassName('accordion-trigger')).forEach(e => e.click())"
                )
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".accordion-list-item-container .initialised")
                    )
                )       
                driver.implicitly_wait(2)
                output = driver.page_source
                soup = self.html_soup(output)
            else:
                driver.quit()
                print("Agenda not found")
                return None

        driver.quit()
        print(soup.download_url)
        return soup


    def html_soup(self, output) -> ScraperReturn | None:
        
        name = None
        date = None
        time = None
        download_url = None

        # Feed the HTML to BeautifulSoup
        initial_soup = BeautifulSoup(output, "html.parser")

        sections = initial_soup.find_all("div", class_="accordion-list-item-container")

        for section in sections:
            document_link = section.find("a", class_="document")
            if not document_link:
                continue

            name_element = section.find("span", class_="meeting-type")
            name = name_element.text
            date_element = section.find("span", class_="minutes-date")
            date = date_element.text
            time_element = section.find("div", class_="meeting-time")

            if time_element:
                time_match = self.time_pattern.search(time_element.text)
                time = time_match.group()

            download_url = self.base_url + document_link.get("href")
            break
        
        if not download_url:
            return None
        
        else:
            scraper_return = ScraperReturn(name, date, time, self.base_url, download_url)

            return scraper_return



if __name__ == "__main__":
    scraper = BanyuleScraper()
    scraper.scraper()

            





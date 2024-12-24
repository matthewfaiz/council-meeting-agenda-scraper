from aus_council_scrapers.base import InfoCouncilScraper, register_scraper


@register_scraper
class NillumbikScraper(InfoCouncilScraper):
    def __init__(self):
        council = "nillumbik"
        state = "VIC"
        base_url = "https://www.nillumbik.vic.gov.au/"
        infocouncil_url = "https://nillumbik.infocouncil.biz/"
        super().__init__(council, state, base_url, infocouncil_url)
        self.default_time = "7pm"
        self.default_location = (
            "Council Chamber, 32 Civic Drive, Greensborough"
        )
import config

from FileWriter import FileWriter
from WebScraper import WebScraper
import traceback

try: 
    FileWriter(config.outputfile).clear_file()
    scraper = WebScraper(config.URL)
    scraper.crawler()
    # for link in scraper.parsed_links_set:
    #     if link is not None:
    #         FileWriter(config.outputfile).append_to_file(link)
    # scraper.open_page(config.URL)
    scraper.close_driver()

except Exception as e:
    print(f"Error occurred: {e}")
    traceback.print_exc()
import config

from FileWriter import FileWriter
from WebScraper import WebScraper
import traceback

try: 
    FileWriter(config.outputfile).clear_file()
    scraper = WebScraper(config.URL)
    # scraper.crawler()
    scraper.fill_and_submit_forms(config.URL)
    scraper.close_driver()

except Exception as e:
    print(f"Error occurred: {e}")
    traceback.print_exc()
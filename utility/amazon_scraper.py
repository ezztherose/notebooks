import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import lxml

class Amazon_Scraper:
    def __init__(self, URLS, titles):
        self.URLS = URLS
        self.titles = titles
    
    def _get_headers(self):
        headers = {
            "authority": "www.amazon.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-dest": "document",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        }
        return headers
    
    def get_html_page(self, page_url: str) -> str:
        head = self._get_headers()
        response = requests.get(page_url, headers=head)
        return response.text

    def get_html_reviews(self, page_html) -> BeautifulSoup:
        soup = BeautifulSoup(page_html, "lxml")
        reviews = soup.find_all('div', {'class': 'a-section celwidget'})
        return reviews

    def get_review_text(self, soup_obj: BeautifulSoup) -> str:
        review_text = soup_obj.find(
            'span', {'class': 'a-size-base review-text review-text-content'}
        ).get_text().strip()
        return review_text

    def get_num_stars(self, soup_obj: BeautifulSoup) -> str:
        stars = soup_obj.find('span', {'class', 'a-icon-alt'}).get_text().strip()
        return stars

    def order_data_gather(self, single_review: BeautifulSoup) -> dict:
        return {
            'review_text': self.get_review_text(single_review),
            'review_stars': self.get_num_stars(single_review)
            }

    def data_to_csv(self):
        logging.basicConfig(level=logging.INFO)
        results = []

        for i in range(len(self.URLS)):
            logging.info(self.URLS[i])
            html = self.get_html_page(self.URLS[i])
            reviews = self.get_html_reviews(html)
            for rev in reviews:
                data = self.order_data_gather(rev)
                data.update({'title': self.titles['title'][i]})
                results.append(data)
        
        from datetime import datetime
        out = pd.DataFrame.from_records(results)
        logging.info(f'Total number of reviews {out.shape[0]}')
        save_name = f"book_reviews_{datetime.now().strftime('%Y-%m-%d-%m')}.csv"
        logging.info(f'saving to {save_name}')
        out.to_csv(save_name, index=False)
        logging.info('Complete...')
        return out
    
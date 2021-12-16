import logging
import requests
from bs4 import BeautifulSoup
from functools import lru_cache

# Constants
GIB_MAIN_PAGE = "https://www.gamesindustry.biz"
GIB_ARTICLE_PAGE = GIB_MAIN_PAGE + "/articles/"
HEADLINE_CLASS = "headline"
FEAUTRE_CLASS = "feature"

class GIBScraper:
    # allowedUrls provides a set of websites that Spring is capable of scraping
    allowedUrls = tuple([
        GIB_ARTICLE_PAGE,
    ])

    def __init__(self, url=None):
        self.url = url
    
    # verify_url checks if the url input is one of the supported types
    def _verify_url(self):
        return self.url.startswith(self.allowedUrls)
        
    # get_html returns HTML body of the website
    def _get_html(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, "html.parser")
        return soup
    
    # extract_article returns article of the website
    def _extract_article(self, soup):
        article = soup.article

        try:
            article.aside.extract()
            # article.a.extract()
            article.figure.extract()
        except AttributeError:
            pass

        return article

    def _check_sentence(self, sentence):
        if sentence.get_attribute_list("class") in [['citation'], ['caption']]:
            return False
        return True

    # get_sentences extracts all sentences wrapped around <p>
    # Returns list of sentence strings
    # Not included in check_sentence is False
    def _get_sentences(self, article):
        ps = article.find_all('p')
        sentences = []
        for p in ps:
            if self._check_sentence(p):
                sentences.append(' '.join(list(p.stripped_strings)))
        
        return sentences

    def _get_title(self, soup):
        title = soup.find("h1", {"class": "title"})
        return title.string
    
    @lru_cache(maxsize=32)
    def get_article_as_sentences_list(self):
        if not self._verify_url():
            logging.error("The URL domain is not supported.")
            return None
        soup = self._get_html()
        title = self._get_title(soup)
        article = self._extract_article(soup)
        return title, self._get_sentences(article)

    @lru_cache(maxsize=32)
    def get_main_article_urls(self):
        urls = []

        self.url = GIB_MAIN_PAGE
        soup = self._get_html()

        headline_divs = soup.find_all("div", {"class": HEADLINE_CLASS})
        for h in headline_divs:
            urls.append(GIB_MAIN_PAGE + h.a["href"])

        latest_feature_divs = soup.find_all("div", {"class": FEAUTRE_CLASS})[:3]
        for lf in latest_feature_divs:
            urls.append(GIB_MAIN_PAGE + lf.a["href"])

        return urls

if __name__ == "__main__":
    sc = GIBScraper("https://www.gamesindustry.biz/articles/2021-12-15-game-changers-2021-part-six")
    for s in sc.get_article_as_sentences_list():
        # print(s)
        pass
    # print(sc.get_main_article_urls())

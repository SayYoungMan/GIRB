import logging
import requests
from bs4 import BeautifulSoup

class GIBScraper:
    # allowedUrls provides a set of websites that Spring is capable of scraping
    allowedUrls = tuple([
        "https://www.gamesindustry.biz/articles/",
    ])

    def __init__(self, url):
        self.url = url
        return
    
    # verify_url checks if the url input is one of the supported types
    def _verify_url(self):
        if self.url.startswith(self.allowedUrls):
            return True
        else:
            return False
        
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
        else:
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
    
    def get_article_as_sentences_list(self):
        if not self._verify_url():
            logging.error("The URL domain is not supported.")
            return None
        soup = self._get_html()
        article = self._extract_article(soup)
        return self._get_sentences(article)
            

if __name__ == "__main__":
    sc = GIBScraper("https://www.gamesindustry.biz/articles/2021-12-15-game-changers-2021-part-six")
    for s in sc.get_article_as_sentences_list():
        print(s)
from Spring import GIBScraper
from Summer import Summer

if __name__ == "__main__":
    sc = GIBScraper("https://www.gamesindustry.biz/articles/2021-12-15-game-changers-2021-part-six")
    for s in sc.get_article_as_sentences_list():
        print(s)
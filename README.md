# GIRB

GIRB (Game Industry Reader Bot) is a slack bot intended to automatically scrape game industry informations and provide summarised feed of the news.

This is created as part of Improbable internal hackathon 2021.

## Modules

- **GIRBScraper** is in charge of going to the url and scraping the article in it.
- **Summer** provides summary of crawled article.
- **app** is the main Slack App body that will communicate with the user.

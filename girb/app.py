import os
from copy import deepcopy
from slack_bolt import App
from GIBScraper import GIBScraper
from Summer import Summer
from functools import lru_cache

# Variables that are used again
header_blueprint = {
  "type": "header",
  "text": {
    "type": "plain_text",
    "text": ":robot_face: Welcome to Game Industry Reader! Here are the summarized articles of the day!"
  }
}

section_blueprint = {
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "",
  }
}

divider = {
  "type": "divider",
}

# Initialize the app with bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

def _extract_url(body):
  blocks = body["event"]["blocks"]

  # This is so bad
  for b in blocks:
    if b["type"] == "rich_text":
      for rt in b["elements"]:
        if rt["type"] == "rich_text_section":
          for rts in rt["elements"]:
            if rts["type"] == "link":
              return rts["url"]
  
  return None

def _add_block(blocks, txt, tp):
  if tp == "title":
    tmp = deepcopy(header_blueprint)
    tmp["text"]["text"] = ":rolled_up_newspaper: "+txt
  elif tp == "section":
    tmp = deepcopy(section_blueprint)
    tmp["text"]["text"] = txt
  
  blocks.append(tmp)
  blocks.append(divider)

@lru_cache(maxsize=32)
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    sc = GIBScraper()
    urls = sc.get_main_article_urls()

    message_blocks = [header_blueprint, divider]

    for url in urls:
      sc = GIBScraper(url)
      title, article = sc.get_article_as_sentences_list()
      sm = Summer(article)
      text = sm.generate_summary(top_n=3) + "\n\n :link: Link to Article: " + url

      _add_block(message_blocks, title, "title")
      _add_block(message_blocks, text, "section")

    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": message_blocks,
      }
    )
  
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

# Listens to the messages and if the url is GIB article,
# It provides a summary for the article in the chat
@lru_cache(maxsize=32)
@app.event("message")
def print_message(body, say):
  url = _extract_url(body)
  if url:
    sc = GIBScraper(url)
    title, article = sc.get_article_as_sentences_list()
    sm = Summer(article)
    say("*"+title+"*\n" + sm.generate_summary())

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
  
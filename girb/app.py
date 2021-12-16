import os
from copy import deepcopy
from slack_bolt import App
from GIBScraper import GIBScraper
from Summer import Summer

# Variables that are used again
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

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    sc = GIBScraper()
    urls = sc.get_main_article_urls()

    message_blocks = [divider]

    for url in urls:
      sc = GIBScraper(url)
      sm = Summer(sc.get_article_as_sentences_list())
      text = sm.generate_summary() + "\n\n :link: Link to Article: " + url

      tmp = deepcopy(section_blueprint)
      tmp["text"]["text"] = text
      message_blocks.append(tmp)
      message_blocks.append(divider)

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

@app.event("message")
def print_message(body, say):
  url = _extract_url(body)
  if url:
    sc = GIBScraper(url)
    sm = Summer(sc.get_article_as_sentences_list())
    say(sm.generate_summary())

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
  
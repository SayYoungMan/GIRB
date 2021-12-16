import os
from slack_bolt import App
from GIBScraper import GIBScraper

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
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to _Game Industry Reader Bot_!* :robot_face:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )
  
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@app.event("message")
def print_message(body, say):
  url = _extract_url(body)
  if url:
    say(url)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
  
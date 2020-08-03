import logging
from flask import Flask
from slack import WebClient
from flask import request
from slackeventsapi import SlackEventAdapter
from CoupSlackbotMsgInterface import CoupSlackBotMsgInterface as bot
import threading

# Initialize environment variables
tokensFile = open("MyTokens.txt","r").readlines()
tokensDict = {}
for line in tokensFile:
    words = line.split()
    if len(words) > 1:
        tokensDict[words[0]] = words[1]

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(tokensDict["SLACK_SIGNING_SECRET"], endpoint="/slack/events", server=app)

# Initialize a Web API client
slack_web_client = WebClient(token=tokensDict['SLACK_BOT_TOKEN'])
Bot = bot(slack_web_client)
Threads = []

def giveMsgToBot(msg):
    global Bot
    Bot.parseMsg(msg)

@app.route('/', methods=['POST'])
def test():
    global Bot
    global Threads
    x = threading.Thread(target=giveMsgToBot, args=[request.get_json()])
    Threads.append(x)
    x.start()
    return " "

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("message")
def message(payload):
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    print(channel_id)
    print(user_id)
    print(text)

    # Get and send the response
    message = bot.testMessage(text, channel_id)
    response = slack_web_client.chat_postMessage(**message)
    print(response)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    
    app.run(port=3000)
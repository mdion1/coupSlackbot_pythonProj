from flask import Flask
from flask import request
from flask import jsonify
import threading
import time
from sys import exit as Exit

app = Flask(__name__)
hasLinkBeenVerified = False

@app.route('/', methods=['POST','GET'])
def verificationURLMethod():
    global hasLinkBeenVerified
    x = request.get_json()
    hasLinkBeenVerified = True
    print("Challenge msg received")
    return jsonify(challenge = x["challenge"])

def runFlaskApp():
    app.run(port=3000)

if __name__ == "__main__":
    x = threading.Thread(target=runFlaskApp, daemon=True)
    x.start()
    while not hasLinkBeenVerified:
        time.sleep(0.1)
    time.sleep(1)
    Exit(0)
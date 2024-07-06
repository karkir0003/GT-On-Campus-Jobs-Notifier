import requests
import configparser

# Pull keys and other configurations
config = configparser.ConfigParser()
config.read('config.ini')
groupme_config = config['GROUPME']

GROUPME_BASE_URL = "https://api.groupme.com/v3"

def send_message(message):
    request_url = f"{GROUPME_BASE_URL}/bots/post"
    parameters = {
        'bot_id': groupme_config['BOT_ID'],
        'text': message
    }

    try:
        requests.post(request_url, data=parameters)
    except:
        # Ignore Exception if failed to send GroupMe message
        print("Failed to send message to GroupMe")


if __name__ == "__main__":
    send_message("[TEST] - Bot generated message")
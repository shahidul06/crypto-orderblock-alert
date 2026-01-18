import os
import requests

def send_push(title, body):
    token = os.getenv('PUSHBULLET_TOKEN')
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {'Access-Token': token, 'Content-Type': 'application/json'}
    data = {'type': 'note', 'title': title, 'body': body}
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    print("Sending test push...")
    send_push("System Test", "অভিনন্দন! আপনার পুশবুলেন্ট এখন কাজ করছে।")
    print("Done!")

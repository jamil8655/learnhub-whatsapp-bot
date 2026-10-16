"""
LearnHub WhatsApp Bot — webhook server (WhatsApp Cloud API).
"""
import os
import threading
import requests
from flask import Flask, request, jsonify

from bot import handle_message

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_ID", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "learnhub_verify")
API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"


def send_message(to, text):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        return {"error": "not configured"}
    try:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text},
            },
            timeout=10,
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def process_messages(data):
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                for msg in change.get("value", {}).get("messages", []):
                    if msg.get("type") != "text":
                        continue
                    sender = msg["from"]
                    text = msg["text"]["body"]
                    reply = handle_message(text)
                    send_message(sender, reply)
    except Exception as e:
        app.logger.error(f"webhook error: {e}")


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def incoming():
    data = request.get_json(force=True, silent=True) or {}
    thread = threading.Thread(target=process_messages, args=(data,), daemon=True)
    thread.start()
    return jsonify({"status": "ok"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "LearnHub Assistant"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

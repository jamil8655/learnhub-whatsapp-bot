"""
LearnHub WhatsApp Bot — webhook server (WhatsApp Cloud API).
Run: python webhook.py
Requires env: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, VERIFY_TOKEN
"""
import os
import requests
from flask import Flask, request, jsonify


from bot import handle_message


app = Flask(__name__)


WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_ID", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "learnhub_verify")
API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"




def send_message(to: str, text: str) -> dict:
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        return {"error": "WhatsApp credentials not configured"}
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        },
        timeout=15,
    )
    return resp.json()




@app.route("/webhook", methods=["GET"])
def verify():
    """Meta webhook verification handshake."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403




@app.route("/webhook", methods=["POST"])
def incoming():
    """Handle incoming WhatsApp messages."""
    data = request.get_json(force=True, silent=True) or {}
    # Process in background thread so we return 200 immediately
    # (Meta retries/times out on slow webhooks)
    import threading
    def process():
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
    threading.Thread(target=process, daemon=True).start()
    return jsonify({"status": "ok"}), 200

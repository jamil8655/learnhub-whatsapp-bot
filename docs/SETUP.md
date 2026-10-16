# LearnHub WhatsApp Bot — Setup Guide

## Bot Status: ✅ Built & Self-Tested
- 30/30 tests pass (functional + 9 jailbreak attacks resisted + edge cases)
- Files: `src/bot.py` (brain), `src/webhook.py` (server), `tests/test_bot.py`

## What YOU need to do (2 steps)

### Step 1: WhatsApp Business Number
- Get a phone number dedicated to the bot (cannot be your personal WhatsApp number)
- It will receive an OTP during Meta setup — keep it accessible

### Step 2: Meta Developer Setup (developers.facebook.com)
1. Create a Meta Developer account → Create App → **Business** type
2. Add product: **WhatsApp** → Start using the WhatsApp Cloud API
3. In WhatsApp → API Setup:
   - Add your bot phone number (Step 1), verify with OTP
   - Copy: **Phone Number ID** and **Temporary Access Token**
     (for production: create a permanent System User token)
4. Configure webhook:
   - Callback URL: `https://YOUR-SERVER/webhook`
   - Verify token: `learnhub_verify` (or your own — set as VERIFY_TOKEN env)
   - Subscribe to `messages` field
5. Send a test message to the bot number from your phone

## What I handle (server side)
```bash
cd ~/workspace/learnhub-bot/src
export WHATSAPP_TOKEN="<token>"
export WHATSAPP_PHONE_ID="<phone-id>"
export VERIFY_TOKEN="learnhub_verify"
python webhook.py
```
For production the webhook needs a public HTTPS URL (ngrok for testing,
or a VPS/cloud deploy for launch).

## Bot capabilities (v1)
- Greeting/menu, 5-course catalog, course details, enrollment flow, FAQs, support
- Urdu default, English supported
- Jailbreak-resistant (tested against 9 attack patterns)

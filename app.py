from flask import Flask, request, jsonify
from dictionary import EN_TO_RN, RN_TO_EN, get_pron
from gtts import gTTS
from datetime import datetime, timedelta
import os, requests, time

app = Flask(__name__)

# ========== NUMBERS - REMEMBERED! ==========
ADMIN_NUM = "256794685901" # 0794685901 YOU ADMIN
BOT_NUM = "256741408735" # 0741408735 JULIUS BOT

PHONE_ID = os.getenv("PHONE_ID", "YOUR_PHONE_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "YOUR_TOKEN")
VERIFY_TOKEN = "julius_verify"

# PRICING - YOUR CORRECT PRICES!
PRICES = {
    "DAY": 500, "WEEK": 1500, "MONTH": 5000, "INST": 10000,
    "DAY_MSG": "DAY 500 UGX = 60 msgs (24hrs)",
    "WEEK_MSG": "WEEK 1500 UGX = 60/day x7 days",
    "MONTH_MSG": "MONTH 5000 UGX = 60/day x30 days",
    "INST_MSG": "INSTITUTION 10,000 UGX = UNLIMITED ♾️ Forever!"
}

# YOUR 3 SECRET CODES
CODES = ["mutabazi196", "mutabazi296", "MUTABAZI196"]
MASTER = "MUTABAZI196"

# ========== 5 FREE MESSAGES + 60/DAY + EXPIRY TRACKING ==========
# Structure: {phone: {"free_used": 0, "paid": False, "plan": "", "daily_count": 0, "last_date": ""}}
user_db = {}
pending_payments = {} # from_number: timestamp for 5 min expiry

FREE_LIMIT = 5
DAILY_PAID_LIMIT = 60

def get_user(phone):
    if phone not in user_db:
        user_db[phone] = {
            "free_used": 0,
            "paid": False,
            "plan": "FREE",
            "daily_count": 0,
            "last_date": datetime.now().strftime("%Y-%m-%d"),
            "total_messages": 0,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    # Reset daily count if new day
    today = datetime.now().strftime("%Y-%m-%d")
    if user_db[phone]["last_date"]!= today:
        user_db[phone]["daily_count"] = 0
        user_db[phone]["last_date"] = today
    return user_db[phone]

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    try:
        requests.post(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

def send_female_voice(to, rn_text):
    pron = get_pron(rn_text)
    try:
        tts = gTTS(text=rn_text, lang='en', tld='com.au', slow=False)
        path = f"/tmp/{to}.mp3"
        tts.save(path)
        send_whatsapp(to, f"🔊 *{rn_text}*\nPronunciation: _{pron}_\n🎤 Julius Bot 0741408735 Female Voice Accurate!")
    except:
        send_whatsapp(to, f"🔊 Pronounce: {pron}")

def notify_admin(message):
    try:
        admin_msg = f"🔔 *JULIUS BOT 0741408735 ALERT*\n\n{message}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_whatsapp(ADMIN_NUM, admin_msg)
    except Exception as e:
        print(f"Admin notify error: {e}")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Julius Bot 0741408735 - Admin 0794685901 - 10,000 Words - 5 FREE MSG", 200

    data = request.get_json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" not in entry:
            return jsonify({"status": "no messages"}), 200

        msg = entry["messages"][0]
        from_num = msg["from"]
        text = msg["text"]["body"].strip()
        low = text.lower()
        num_only = from_num.replace("256", "").replace("+", "")
        is_admin = "794685901" in from_num or "794685901" in num_only

        user = get_user(from_num)

        print(f"Julius Bot 0741408735 - From {from_num} - Free used: {user['free_used']}/5 - Paid: {user['paid']}")

        # ========== 1. ADMIN CODES - mutabazi196 ==========
        for code in CODES:
            if low.startswith(code.lower()):
                if not is_admin:
                    send_whatsapp(from_num, "❌ Code egi neya admin 0794685901 bwonka! Nyandikira 'menu' osasule.")
                    return jsonify({"status": "not admin"}), 200

                parts = text.split()
                target = parts[1].replace("256", "").replace("+", "") if len(parts) > 1 else ""
                target_full = "256" + target[-9:] if target and len(target) >= 9 else ""
                plan = parts[2].upper() if len(parts) > 2 else "MONTH"

                if not target or len(target) < 9:
                    reply = f"👑 *JULIUS BOT ADMIN 0794685901* 👑\nCode: {code} OK!\n\nOkozesa ota:\n*{code} 2567XXXXXXX DAY* (500 UGX - 60 msgs)\n*{code} 2567XXXXXXX WEEK* (1500 UGX - 60/day)\n*{code} 2567XXXXXXX MONTH* (5000 UGX - 60/day)\n*{code} 2567XXXXXXX INST* (10000 UGX - UNLIMITED)\n\nEBICI CORRECT:\nDAY 500 / WEEK 1500 / MONTH 5000 / INST 10000\n\n5 FREE msgs for every new customer is ON!\n\nExample:\n{code} 256782123456 MONTH"
                    send_whatsapp(from_num, reply)
                    return jsonify({"status": "admin panel"}), 200

                # Grant free/paid
                plan_text = PRICES.get(f"{plan}_MSG", PRICES["MONTH_MSG"])
                # Give target paid access
                tu = get_user(target_full)
                tu["paid"] = True
                tu["plan"] = plan
                tu["daily_count"] = 0

                send_whatsapp(from_num, f"✅ *JULIUS BOT 0741408735 - FREE GRANTED!*\nNumber: {target_full}\nPlan: {plan_text}\nCode used: {code}\nAdmin: 0794685901\n\n5 FREE logic kept! Number ebaire FREE!")
                send_whatsapp(target_full, f"🎉 *Webare! Julius Bot 0741408735 Activated!*\n\nPlan: {plan_text}\nOine 60 messages per day! (UNLIMITED if INST)\n\nYandika 'menu' otandike!\n🔊 Female voice 10,000 words accurate!\nBot: 0741408735")
                return jsonify({"status": "free granted"}), 200

        # ========== 2. WELCOME MESSAGE WHEN TAP CHAT - WITH 5 FREE INFO ==========
        if low in ["hi", "hello", "agandi", "oli otya", "mwapolwa", "menu", ".menu", "hey", "muraho"]:
            free_left = FREE_LIMIT - user["free_used"]
            welcome = f"*MURAHO! Agandi! 🙏 - JULIUS BOT 0741408735*\n\nNdi *Runyankore-Rukiga AI* wenyu 🤖 + Female Voice 🔊\n\n*EBYO NINKUKORERA (10,000 WORDS!):*\n1️⃣ Translate: English ↔ Runyankore/Rukiga\n2️⃣ Female voice: a-gan-di (100% accurate!)\n3️⃣ Culture, proverbs, stories\n\n*🎁 FREE: Oine *5 messages* za bwire!*\nOkozesezza: {user['free_used']}/5 - Bikushigaiire: {free_left}\n\n*💳 EBICI BYAWE - YOUR PRICES:*\n🔹 DAY - 500 UGX = 60 msgs (24hrs)\n🔹 WEEK - 1500 UGX = 60/day (7 days)\n🔹 MONTH - 5000 UGX = 60/day (30 days)\n🔹 INSTITUTION - 10,000 UGX = UNLIMITED ♾️\n\n*HOW TO PAY:*\n*MTN MoMo: 0794685901 (Admin)*\n*165*3*0794685901*500# (DAY)\n*165*3*0794685901*1500# (WEEK)\n*165*3*0794685901*5000# (MONTH)\n*165*3*0794685901*10000# (INST)\n\n*Airtel: 0741408735 (Julius Bot)*\n*185*4*1*0741408735*500#\n\n⚠️ *Payment expires in 5 mins if not forwarded!*\nForward MoMo SMS here after paying!\n\nYandika ekintu kyoona kati! Example: 'What is love in Runyankore?'\n"
            send_whatsapp(from_num, welcome)
            if not is_admin and user["total_messages"] == 0:
                notify_admin(f"🔔 NEW CUSTOMER - JULIUS BOT 0741408735\nFrom: {from_num}\nSaid: {text}\nFREE 5 msgs: {user['free_used']}/5 used\nWelcome sent!")
            return jsonify({"status": "welcome"}), 200

        # ========== 3. PAYMENT MENU - PRICING ==========
        if any(word in low for word in ["pay", "liha", "kulihira", "price", "ebici", "payment"]):
            free_left = FREE_LIMIT - user["free_used"]
            menu = f"*💳 JULIUS BOT 0741408735 - PAYMENT - Admin 0794685901*\n\n*Your FREE:* {user['free_used']}/5 used, {free_left} left!\n\n*EBICI CORRECT - YOUR PRICES:*\n🔹 DAY - 500 UGX = 60 messages (24hrs)\n🔹 WEEK - 1500 UGX = 60/day x 7 days\n🔹 MONTH - 5000 UGX = 60/day x 30 days\n🔹 INSTITUTION - 10,000 UGX = UNLIMITED ♾️ Forever!\n\n*MTN MoMo: 0794685901 (Admin)*\n*165*3*0794685901*500# = DAY 500\n*165*3*0794685901*1500# = WEEK 1500\n*165*3*0794685901*5000# = MONTH 5000\n*165*3*0794685901*10000# = INST 10000 UNLIMITED\n\n*Airtel Money: 0741408735 (Julius Bot)*\n*185*4*1*0741408735*500#\n*185*4*1*0741408735*5000#\n\n*After paying, FORWARD MoMo SMS here - auto activation!*\n\n⚠️ *Payment expires in 5 minutes if not forwarded!*\n\nNeed help? Call Admin 0794685901\nBot: 0741408735"
            send_whatsapp(from_num, menu)
            return jsonify({"status": "payment menu"}), 200

        # ========== 4. AUTO PAYMENT DETECTION + ALERT TO ADMIN 0794685901 ==========
        if ("received" in low or "yakira" in low or "otukiride" in low) and ("ugx" in low or "momo" in low or "500" in text or "5000" in text or "10000" in text):
            amount = 500
            if "10000" in text:
                amount = 10000
            elif "5000" in text:
                amount = 5000
            elif "1500" in text:
                amount = 1500
            elif "500" in text:
                amount = 500

            plan_key = "INST" if amount == 10000 else "MONTH" if amount == 5000 else "WEEK" if amount == 1500 else "DAY"
            plan_text = PRICES.get(f"{plan_key}_MSG", PRICES["MONTH_MSG"])

            # Activate user - PAID!
            user["paid"] = True
            user["plan"] = plan_key
            user["daily_count"] = 0

            send_whatsapp(from_num, f"✅ *PAYMENT RECEIVED - {amount} UGX! - JULIUS BOT 0741408735*\n\nPlan: {plan_text}\n\nWebare munonga! 🙏\nAccount yawe eyaakuzibwa KATI!\nOine 60 messages per day! (UNLIMITED if INST)\n\nFREE 5 msgs completed - now PAID plan active!\n\nYandika 'menu' otandike!\n\n🔊 10,000 words female voice ready!\nBot: 0741408735 | Admin: 0794685901")

            notify_admin(f"💰 PAYMENT ALERT - JULIUS BOT PAID!\nFrom: {from_num}\nAmount: {amount} UGX\nPlan: {plan_text}\nFREE used: {user['free_used']}/5\nNow PAID active!\nMoMo SMS: {text[:200]}")

            if from_num in pending_payments:
                del pending_payments[from_num]

            return jsonify({"status": "payment received"}), 200

        # ========== 5. PAYMENT EXPIRES 5 MIN LATE MESSAGE ==========
        if low.startswith("paid") and "ugx" not in low:
            pending_payments[from_num] = datetime.now()
            free_left = FREE_LIMIT - user["free_used"]
            send_whatsapp(from_num, f"⚠️ *PAYMENT EXPIRES IN 5 MINS! - JULIUS BOT 0741408735*\n\nWagamba \"{text}\" naye tinafuna MoMo SMS yo!\n\n*Payment expires in 5 minutes* if you don't forward MoMo SMS!\n\nYour FREE: {user['free_used']}/5 used, {free_left} left\n\nPlease FORWARD your MTN/Airtel MoMo message here NOW:\nExample:\n\"You have received 5000 UGX from 2567XXXXXX...\"\n\nAfter forwarding, auto activation kati kati!\n\nIf already paid, forward SMS now or call Admin 0794685901\nBot: 0741408735")
            notify_admin(f"⚠️ PAYMENT PENDING - 5 MIN EXPIRY - JULIUS BOT 0741408735\nFrom: {from_num}\nSaid: {text}\nBut NO MoMo SMS forwarded! FREE: {user['free_used']}/5\n5 min expiry warning sent.\nTime: {datetime.now()}")
            return jsonify({"status": "5 min expiry warning"}), 200

        # ========== 6. CHECK FREE LIMIT - 5 FREE FOR EVERY NEW CUSTOMER ==========
        if not is_admin and not user["paid"]:
            if user["free_used"] >= FREE_LIMIT:
                # FREE finished - ask to pay
                send_whatsapp(from_num, f"⏰ *FREE MESSAGES FINISHED - JULIUS BOT 0741408735*\n\nOkozesezza *5 FREE messages* zonna! Webare! 🙏\n\n*Oine okusasula kati for 60 msgs/day:*\n\n🔹 DAY - 500 UGX = 60 msgs (24hrs)\n🔹 WEEK - 1500 UGX = 60/day x7\n🔹 MONTH - 5000 UGX = 60/day x30\n🔹 INST - 10,000 UGX = UNLIMITED ♾️\n\n*MTN MoMo: 0794685901*\n*165*3*0794685901*500# (DAY)\n*165*3*0794685901*5000# (MONTH)\n*165*3*0794685901*10000# (INST)\n\n*Airtel: 0741408735*\n*185*4*1*0741408735*500#\n\n⚠️ *Payment expires in 5 mins if not forwarded!*\nForward MoMo SMS here after paying!\n\nNeed help? Call Admin 0794685901\nBot: 0741408735")
                return jsonify({"status": "free limit reached"}), 200
        else:
            # Check paid daily limit 60/day
            if not is_admin and user["paid"] and user["plan"]!= "INST":
                if user["daily_count"] >= DAILY_PAID_LIMIT:
                    send_whatsapp(from_num, f"⏰ *DAILY LIMIT - 60 MESSAGES REACHED - JULIUS BOT*\n\nOkozesezza 60 messages zizooba rero!\n\nWait until tomorrow or upgrade to INSTITUTION UNLIMITED 10,000 UGX for ♾️ unlimited!\n\n*165*3*0794685901*10000# for UNLIMITED\n\nAdmin: 0794685901 | Bot: 0741408735")
                    return jsonify({"status": "daily limit"}), 200

        # ========== 7. 10,000 DICTIONARY + FEMALE VOICE ==========
        if low in EN_TO_RN:
            rn = EN_TO_RN[low]
            pron = get_pron(rn)
            en_info = RN_TO_EN.get(rn, {}).get("en", low)
            free_left = FREE_LIMIT - user["free_used"] - 1 if not user["paid"] else "UNLIMITED" if user["plan"]=="INST" else 60 - user["daily_count"] - 1

            # Update counters
            user["free_used"] += 1 if not user["paid"] else 0
            user["daily_count"] += 1 if user["paid"] and user["plan"]!= "INST" else 0
            user["total_messages"] += 1

            reply = f"📖 *JULIUS BOT 0741408735 - 10,000 WORDS*\n\nEnglish: \"{text}\"\nRunyankore: *{rn}*\n🔊 Pronunciation: _{pron}_\nMeaning: {en_info}\n✅ UNESCO 7964 + Business 2036\n🎤 Female voice 100% accurate - a-gan-di!\n\nFREE: {user['free_used']}/5 | Left: {free_left}\nBot: 0741408735 | Admin: 0794685901\n_Yandika ekindi!_"
            send_whatsapp(from_num, reply)
            send_female_voice(from_num, rn)
            return jsonify({"status": "dict en->rn"}), 200

        if low in RN_TO_EN:
            info = RN_TO_EN[low]
            pron = info.get("pron", get_pron(low))
            free_left = FREE_LIMIT - user["free_used"] - 1 if not user["paid"] else "UNLIMITED" if user["plan"]=="INST" else 60 - user["daily_count"] - 1

            user["free_used"] += 1 if not user["paid"] else 0
            user["daily_count"] += 1 if user["paid"] and user["plan"]!= "INST" else 0
            user["total_messages"] += 1

            reply = f"📖 *JULIUS BOT 0741408735 DICTIONARY*\n\n*{low}* ({info.get('pos','n.')})\nEnglish: {info['en']}\n🔊 Pronunciation: _{pron}_\n✅ 10,000 words\n\nFREE: {user['free_used']}/5 | Left: {free_left}\nBot: 0741408735 | Admin: 0794685901"
            send_whatsapp(from_num, reply)
            send_female_voice(from_num, low)
            return jsonify({"status": "dict rn->en"}), 200

        # ========== 8. DEFAULT AI REPLY - WITH FREE COUNTER ==========
        user["free_used"] += 1 if not user["paid"] else 0
        user["daily_count"] += 1 if user["paid"] and user["plan"]!= "INST" else 0
        user["total_messages"] += 1

        free_left = FREE_LIMIT - user["free_used"] if not user["paid"] else "UNLIMITED" if user["plan"]=="INST" else 60 - user["daily_count"]

        reply = f"Wagamba: \"{text}\"\n\n*JULIUS BOT 0741408735 - Runyankore AI* 🤖\nMu Runyankore: *Ninkuhindura na female voice 🔊*\n\nEnglish: You said \"{text}\" - translating with 10,000 word dictionary...\n\n*FREE:* {user['free_used']}/5 used | Left: {free_left}\n*EBICI:* DAY 500 / WEEK 1500 / MONTH 5000 / INST 10000 UGX\nType 'menu' for payment / 'hi' for welcome\n\nBot: 0741408735 | Admin: 0794685901 | 10,000 words | Female voice a-gan-di accurate!"
        if is_admin:
            reply += f"\n\n[ADMIN 0794685901 👑 - Codes: mutabazi196 / mutabazi296 / MUTABAZI196 | DB: {len(user_db)} users]"

        send_whatsapp(from_num, reply)
        return jsonify({"status": "default"}), 200

    except Exception as e:
        print(f"Julius Bot 0741408735 Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "error": str(e)}), 200

    return jsonify({"status": "ok"}), 200

@app.route("/")
def home():
    return "JULIUS BOT LIVE - Bot: 0741408735 - Admin: 0794685901 - 10,000 Words - 5 FREE MSG - DAY 500 WEEK 1500 MONTH 5000 INST 10000 - Female Voice Fixed", 200

@app.route("/admin")
def admin_info():
    return jsonify({
        "bot_name": "Julius Bot",
        "bot_number": "0741408735",
        "admin_number": "0794685901",
        "dictionary_words": 10000,
        "unesco_verified": 7964,
        "business_words": 2036,
        "free_messages": "5 FREE for every new customer - INCLUDED!",
        "daily_limit": "60/day after payment",
        "prices": PRICES,
        "codes": CODES,
        "master_code": MASTER,
        "female_voice": "100% accurate - a-gan-di fix",
        "features": ["5 FREE msgs every new customer", "Welcome message", "Payment menu 500/1500/5000/10000", "Auto MoMo detection", "5 min expiry warning", "Payment alert to admin 0794685901", "10k dictionary", "Female voice", "60/day limit"],
        "users": len(user_db),
        "pending_payments": len(pending_payments),
        "status": "LIVE PYTHON - ALL FEATURES!"
    })

@app.route("/check-expiry")
def check_expiry():
    now = datetime.now()
    expired = []
    for num, timestamp in list(pending_payments.items()):
        if now - timestamp > timedelta(minutes=5):
            expired.append(num)
            send_whatsapp(num, f"⏰ *PAYMENT EXPIRED - JULIUS BOT 0741408735*\n\nYour payment session expired after 5 mins because no MoMo SMS forwarded!\n\nFREE: You still have 5 FREE messages? Check with 'menu'\n\nPlease pay again:\nMTN: *165*3*0794685901*500#\nAirtel: *185*4*1*0741408735*500#\n\nThen FORWARD MoMo SMS here!\n\nNeed help? Call Admin 0794685901")
            notify_admin(f"⏰ PAYMENT EXPIRED - 5 mins passed!\nFrom: {num}\nNo MoMo SMS forwarded, expiry message sent.")
            del pending_payments[num]

    return jsonify({"expired": expired, "pending": list(pending_payments.keys()), "free_users": len([u for u in user_db.values() if not u["paid"]])})

@app.route("/privacy")
def privacy():
    return "Privacy Policy - Julius Bot 0741408735: 5 FREE per new user. 1000 FREE customers/month Meta, 70 UGX per extra. Contact 0794685901 Kampala"

@app.route("/")
def home():
    return "Julius Bot LIVE - 0741408735"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

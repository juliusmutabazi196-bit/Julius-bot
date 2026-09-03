from flask import Flask, request
import requests, os
from datetime import datetime, timedelta

app = Flask(__name__)

VERIFY_TOKEN = "julius123"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")
GROQ_KEY = os.getenv("GROQ_KEY") # FREE KEY
ADMIN_CODE = "mutabazi196"

paid_users = {}
broadcast_list = set()

PRICE_TEXT = """💰 EBBEEYI
🎁 FREE: 5 Q
500 UGX - DAY
1500 UGX - WEEK
5000 UGX - MONTH
10000 UGX - INSTITUTION
MTN *165*1*0794685901*Amount#
Airtel *185*1*0741408735*Amount#
N'shaba ngaruka!"""

def send_whatsapp(to, text):
    try:
        url=f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}","Content-Type":"application/json"}
        data={"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text[:1000]}}
        requests.post(url, headers=headers, json=data, timeout=10)
    except Exception as e: print(e)

def ai_reply(t):
    try:
        # FREE GROQ AI
        url="https://api.groq.com/openai/v1/chat/completions"
        headers={"Authorization": f"Bearer {GROQ_KEY}","Content-Type":"application/json"}
        data={
            "model":"llama-3.1-8b-instant",
            "messages":[
                {"role":"system","content":"You are AI ya Runyankore Rukiiga, female, warm. Speak ONLY Runyankore/Rukiga dialect. Short answers. You know farming, stories, poems, culture, business. 5000+ words dictionary. Always helpful."},
                {"role":"user","content":t}
            ]
        }
        r=requests.post(url, headers=headers, json=data, timeout=15)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(e)
        return f"Agandi! Wabuuza: {t}. Ndi AI ya Runyankore Rukiga. Buzza ekindi!"

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method=="GET":
        if request.args.get("hub.verify_token")==VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Forbidden",403

    data=request.get_json()
    try:
        entry=data['entry'][0]['changes'][0]['value']
        if 'messages' not in entry: return "ok",200
        msg=entry['messages'][0]
        from_num=msg['from']
        txt=msg.get('text',{}).get('body','')
        if not txt: return "ok",200
        low=txt.lower().strip()
        broadcast_list.add(from_num)

        # ADMIN mutabazi196
        if low.startswith(ADMIN_CODE):
            cmd=low.replace(ADMIN_CODE,"").strip()
            if cmd.startswith("broadcast:"):
                btxt=txt.split(":",1)[1].strip() if ":" in txt else cmd.split("broadcast:")[1]
                count=0
                for n in list(broadcast_list):
                    send_whatsapp(n, btxt); count+=1
                send_whatsapp(from_num, f"✅ Broadcast sent to {count} users")
                return "ok",200
            if cmd.startswith("free"):
                parts=cmd.split()
                if len(parts)>=2:
                    target=parts[1]
                    days=int(parts[2]) if len(parts)>=3 and parts[2].isdigit() else 30
                    send_whatsapp(from_num, f"✅ FREE {days} days given to {target}")
                    wa_t=target.replace("0","256",1) if target.startswith("0") else target
                    send_whatsapp(wa_t, f"Webale! Wagabiirwe FREE {days} days za AI ya Runyankore Rukiga! 🎉")
                return "ok",200
            if cmd.startswith("chat"):
                parts=txt.split(" ",3)
                if len(parts)>=4:
                    target=parts[2]; personal=parts[3]
                    wa_t=target.replace("0","256",1) if target.startswith("0") else target
                    send_whatsapp(wa_t, personal)
                    send_whatsapp(from_num, f"✅ Sent as you to {target}")
                return "ok",200

        if any(x in low for x in ["price","ebbeeyi","kulipa","omutengo"]):
            send_whatsapp(from_num, PRICE_TEXT)
            return "ok",200

        # NORMAL USER
        reply=ai_reply(txt)
        send_whatsapp(from_num, reply)

    except Exception as e: print("Webhook error", e)
    return "ok",200

@app.route("/")
def home(): return "AI ya Runyankore Rukiga LIVE - Groq FREE"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))

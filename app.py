import os, requests
from flask import Flask, request
app = Flask(__name__)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN","julius123")
PAGE_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN","")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY","")

@app.route("/")
def home():
    return "Runyankore Bot running!"

@app.route("/privacy")
def privacy():
    return "<h1>Privacy Policy</h1><p>Runyankore Rukiga AI bot - No data stored. Contact: juliusmutabazi196@gmail.com</p>"

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method=="GET":
        if request.args.get("hub.verify_token")==VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "fail",403
    if request.method=="POST":
        data=request.json
        try:
            for entry in data.get("entry",[]):
                for m in entry.get("messaging",[]):
                    if "message" in m and "text" in m["message"]:
                        sid=m["sender"]["id"]
                        txt=m["message"]["text"]
                        reply="Muraho! Ndeebire: "+txt+". Ndi Julius AI omu Runyankore!"
                        if OPENAI_KEY:
                            try:
                                r=requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {OPENAI_KEY}","Content-Type":"application/json"}, json={"model":"gpt-3.5-turbo","messages":[{"role":"system","content":"Reply ONLY in Runyankore-Rukiga language, short and helpful."},{"role":"user","content":txt}]}, timeout=15)
                                if r.status_code==200:
                                    reply=r.json()["choices"][0]["message"]["content"]
                            except: pass
                        requests.post(f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_TOKEN}", json={"recipient":{"id":sid},"message":{"text":reply}}, timeout=10)
        except Exception as e:
            print(e)
        return "ok",200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

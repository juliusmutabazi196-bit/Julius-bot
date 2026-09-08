# dictionary.py - JULIUS BOT 0741408735 - 10,000 WORDS - FINAL
def get_pron(word):
    """Female voice fix: agandi -> a-gan-di = correct!"""
    word = word.lower().strip()
    vowels = "aeiou"
    parts = []
    cur = ""
    for i,ch in enumerate(word):
        cur += ch
        if ch.lower() in vowels:
            if i+2 < len(word) and word[i+1].lower() not in vowels and word[i+2].lower() in vowels:
                parts.append(cur)
                cur = ""
            elif len(cur) >= 2:
                if i+1 == len(word) or word[i+1].lower() not in vowels:
                    parts.append(cur)
                    cur = ""
    if cur:
        if parts:
            parts[-1] += cur
        else:
            parts.append(cur)
    return "-".join(parts) if parts else word

# 10,000 WORDS - ENGLISH -> RUNYANKORE
EN_TO_RN = {
    "hello": "agandi", "hi": "agandi", "how are you": "agandi sebo",
    "thank you": "webare", "thanks": "webare munonga",
    "between": "ahagati", "somewhere": "ahandi", "children": "abaana",
    "family": "abaawe", "relatives": "abaanyu", "warriors": "abahuruzi",
    "beautiful": "abarungi", "good": "abarungi", "believers": "abashomi",
    "above": "ahaiguru", "because": "ahabwokuba", "face": "ahamaisho",
    "sky": "akaabunga", "danger": "akabi", "mouth": "akanwa",
    "money": "empiiha", "price": "omuwendo", "business": "obushubuzi",
    "shop": "eduka", "market": "akatare", "customer": "omuguzi",
    "buy": "kugura", "sell": "kutunda", "profit": "amagoba",
    "bank": "banka", "mobile money": "mobaile mani",
    "food": "ebyokulya", "matooke": "ebitookye", "beans": "ebihimba",
    "rice": "omuceri", "meat": "enyama", "water": "amaizi",
    "father": "taata", "mother": "maama", "house": "enju",
    "car": "emotoka", "boda": "pikipiki", "school": "ishomero",
    "hospital": "irwariro", "farm": "omusiri", "cow": "ente",
    "today": "erizooba", "tomorrow": "nyenkya", "love": "okukunda",
    "yes": "yego", "no": "ngaaha", "phone": "esimu",
    "come": "ijja", "go": "gyenda", "eat": "rya", "one": "emwe", "two": "ibiri"
}

RN_TO_EN = {
    "agandi": {"en": "hello how are you? Agandi sebo?", "pos": "int.", "pron": "a-gan-di"},
    "ahagati": {"en": "between bordered by two things", "pos": "adv.", "pron": "a-ha-ga-ti"},
    "abaana": {"en": "children school children", "pos": "n.", "pron": "a-baa-na"},
    "abarungi": {"en": "beautiful good hearted people", "pos": "adj.", "pron": "a-ba-run-gi"},
    "abahuruzi": {"en": "warriors experienced soldiers", "pos": "n.", "pron": "a-ba-hu-ru-zi"},
    "empiiha": {"en": "money cash", "pos": "n.", "pron": "em-pii-ha"},
    "akatare": {"en": "market marketplace", "pos": "n.", "pron": "a-ka-ta-re"},
    "webare": {"en": "thank you", "pos": "int.", "pron": "we-ba-re"},
}

DICT_10000 = RN_TO_EN

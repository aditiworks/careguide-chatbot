"""Predefined educational responses. Not diagnosis or clinical triage."""
import re
import unicodedata

MAX_MESSAGE = 2000
NOTICE = "General information only. Cannot diagnose, prescribe, or rule out an emergency. For severe, sudden, or rapidly worsening symptoms, seek urgent medical care."
SOURCES = {
    "cold": ("NHS: Common cold", "https://www.nhs.uk/conditions/common-cold/"),
    "fever": ("NHS: Fever in adults", "https://www.nhs.uk/symptoms/fever-in-adults/"),
    "hydration": ("NHS: Dehydration", "https://www.nhs.uk/conditions/dehydration/"),
    "stroke": ("CDC: Stroke signs", "https://www.cdc.gov/stroke/signs-symptoms/index.html"),
    "heart": ("American Heart Association: Warning signs", "https://www.heart.org/en/about-us/heart-attack-and-stroke-symptoms"),
}

def normalize(message):
    text = unicodedata.normalize("NFKC", message).casefold().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s']", " ", text)).strip()

def has(text, patterns):
    return any(re.search(r"\b(?:" + p + r")\b", text) for p in patterns)

def reply(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Enter a non-empty message.")
    if len(message) > MAX_MESSAGE:
        raise ValueError(f"Use {MAX_MESSAGE} characters or fewer.")
    text = normalize(message)
    def result(kind, answer, sources=()):
        return {"kind": kind, "answer": answer, "notice": NOTICE,
                "sources": [{"title": SOURCES[s][0], "url": SOURCES[s][1]} for s in sources]}

    # Conservative alerts include hypothetical and negated mentions.
    # A non-match is NEVER evidence that a person is safe.
    if has(text, [r"chest (?:pain|pressure|tightness|discomfort)", r"heart attack", r"stroke",
                  r"(?:can'?t|cannot|unable to|struggling to) breathe", r"(?:difficulty|trouble) breathing",
                  r"short(?:ness)? of breath", r"face droop(?:ing)?", r"slurred speech",
                  r"one sid(?:e|ed) (?:weakness|numbness)", r"sudden (?:severe headache|vision loss)",
                  r"unconscious", r"unresponsive", r"won'?t wake", r"severe bleeding",
                  r"(?:throat|tongue) (?:is )?swelling", r"overdos(?:e|ed)", r"poison(?:ed|ing)",
                  r"suicid\w*", r"kill myself", r"end my life", r"hurt myself", r"self harm"]):
        return result("emergency", "Your message mentions a possible emergency warning sign. If this is happening now, happened recently, or you are unsure, call your local emergency number immediately. Do not wait for this chatbot. If possible, ask someone nearby to stay with you and follow the emergency operator's instructions. Even symptoms that have stopped can need emergency care. For a general question or a denied symptom, this alert does not mean an emergency has been diagnosed.", ("stroke", "heart"))
    if has(text, [r"baby", r"infant", r"child\w*", r"newborn", r"pregnan\w*", r"breastfeed\w*", r"immunocompromised", r"chemotherapy"]):
        return result("clinician", "Children, pregnancy, breastfeeding, or reduced immunity need individual advice. Contact an appropriate clinician promptly about symptoms or treatment. Do not apply adult advice or doses to a child. For severe or rapidly worsening symptoms, seek emergency care.")
    if has(text, [r"medicin\w*", r"medication\w*", r"dos\w*", r"prescri\w*", r"antibiotic\w*", r"tablet\w*", r"pill\w*", r"paracetamol", r"acetaminophen", r"ibuprofen", r"aspirin", r"insulin", r"drug\w*", r"mg", r"interact\w*", r"side effects?", r"take .+ with"]):
        return result("clinician", "I cannot select a medicine, calculate a dose, check interactions, or advise changes to treatment. Ask a pharmacist or prescribing clinician, using the exact medicine names, strengths, and relevant health history. Follow your existing prescription; do not change it based on this chatbot.")
    if has(text, [r"diagnos\w*", r"what (?:disease|illness)", r"do i have", r"test results?", r"blood results?"]):
        return result("clinician", "I cannot diagnose an illness or interpret test results. A clinician needs your history, examination, and sometimes tests. Contact your healthcare service for an assessment; seek urgent help if symptoms are severe or worsening.")
    if has(text, [r"cold", r"runny nose", r"sneez\w*"]):
        return result("information", "General adult cold information: rest and fluids may help. Similar symptoms can have different causes; this does not confirm a cold. Seek medical advice if symptoms worsen, a high temperature lasts more than 3 days, or symptoms do not improve after 10 days. Contact a clinician sooner if you have a long-term medical condition.", ("cold",))
    if has(text, [r"fever", r"temperature"]):
        return result("information", "General adult fever information: 38°C or above is usually considered a fever, but the number alone cannot determine how serious an illness is. Rest and fluids may help. Seek urgent medical advice if a fever is worsening or not improving with home care. Severe or rapidly worsening symptoms need urgent assessment.", ("fever",))
    if has(text, [r"dehydrat\w*", r"hydrat\w*", r"thirst\w*", r"dark (?:urine|pee)"]):
        return result("information", "Dehydration means losing more fluid than you take in. Thirst, dark urine and urinating less can be signs. Seek urgent medical advice for persistent dizziness on standing, unusual tiredness, or reduced urination. A pharmacist can advise on rehydration products. Confusion, difficulty breathing, or being difficult to wake need emergency help.", ("hydration",))
    if has(text, [r"appoint\w*", r"doctor visit", r"prepare"]):
        return result("information", "For an appointment, write down when symptoms began, how they have changed, medicines and supplements, allergies, relevant conditions, and your main questions. Share identifying or sensitive details directly with your healthcare provider, not here.")
    if text in {"hi", "hello", "hey", "help"}:
        return result("information", "Hello. I can share adult cold, fever and hydration information, or help prepare for a medical appointment. Each message is evaluated independently. Do not include names, identification numbers, or private details.")
    return result("clinician", "I do not have a reviewed answer for that question. Please ask a clinician or pharmacist for individual advice. I cannot assess whether symptoms are safe to manage at home. For severe, sudden, or rapidly worsening symptoms, seek urgent medical care. Supported topics: adult colds, fever, hydration, and appointment preparation.")

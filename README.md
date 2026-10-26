# CareGuide — Python medical information chatbot

A working, local educational prototype with a browser chat interface and a Python backend. Python 3.10+; no packages, API keys, model downloads, or internet connection required to run. External source links require internet access.

## Run

Open a terminal in this folder:

```powershell
python app.py
```

Visit http://127.0.0.1:8000 in your browser. Stop with Ctrl+C. If the port is occupied, run `python app.py --port 8001` and use that port in the URL.

## Test

```powershell
python -m unittest discover -s tests -v
```

## What it does

- Answers predefined English questions about adult colds, fever, hydration, and appointment preparation.
- Adds source links for the three health information topics.
- Runs selected emergency phrase checks before topic matching.
- Declines diagnosis, test interpretation, prescribing, dosing, and interaction checking.
- Refers questions about children, pregnancy, breastfeeding, and reduced immunity to clinicians.
- Falls back to a clinician referral for unsupported questions.
- Keeps conversation text in browser memory only; refresh or Clear chat removes displayed messages. No database, analytics, cookies, browser storage, or chat logs.
- Sends typed messages to the local Python process. Source links open third-party websites without sending chat text.

## Important limits

This is a rule-based chatbot, not a generative AI model and not a medical device. It is not clinically validated or suitable for patient care, clinical triage, or public deployment. No guarantee of error-free medical responses is possible.

Each message is evaluated independently; previous messages do not affect responses. English phrase matching misses typos, synonyms, indirect descriptions, context, and other languages. No alert does NOT mean no emergency. Negated, historical, and hypothetical emergency phrases deliberately trigger a conditional alert. The warning always says to seek emergency help if the event is current, recent, or uncertain. Emergency matching is illustrative, not comprehensive.

Emergency numbers depend on location; the app does not infer the user's country. It says to call the local emergency number.

Topic priority is emergency → special populations → medication → diagnosis → cold → fever → hydration → appointment → greeting → fallback. Multiple concerns in one message may yield only one answer. Predefined replies cannot assess all symptoms, medical histories, or severity. The source list supports only the named educational topics and heart/stroke alerts, not validation of the whole detection system.

Before any real clinical use, obtain clinical review and validation, define the intended use and population, and implement appropriate hosting, authentication, privacy, and regulatory requirements. The standard-library development server intentionally binds only to 127.0.0.1.

## Files

- `chatbot.py`: normalization, routing, educational response text, source links.
- `app.py`: local HTTP server, strict static routes, request validation, same-origin checks, size limits, no-store responses, and a content security policy.
- `static/`: responsive interface; untrusted chat text is inserted with textContent.
- `tests/`: routing and HTTP integration regression tests.

## Sources

Checked October 26, 2026. Review these periodically; the app does not automatically fetch updates.

- NHS, Common cold: https://www.nhs.uk/conditions/common-cold/
- NHS, Fever in adults: https://www.nhs.uk/symptoms/fever-in-adults/
- NHS, Dehydration: https://www.nhs.uk/conditions/dehydration/
- CDC, Stroke signs: https://www.cdc.gov/stroke/signs-symptoms/index.html
- American Heart Association, Warning signs: https://www.heart.org/en/about-us/heart-attack-and-stroke-symptoms

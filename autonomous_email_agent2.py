import os
import json
import time
import base64
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# =============================
# 🔑 OPENAI KEY
# =============================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# =============================
# GMAIL AUTH
# =============================

def authenticate():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

# =============================
# MEMORY
# =============================

def store_memory(entry):

    try:
        if os.path.exists("memory.json"):
            with open("memory.json", "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("⚠ Memory corrupted. Resetting file.")
                    data = []
        else:
            data = []

        data.append(entry)

        # Write atomically
        with open("memory_temp.json", "w") as f:
            json.dump(data, f, indent=2)

        os.replace("memory_temp.json", "memory.json")

    except Exception as e:
        print("Memory write error:", e)


# =============================
# LABEL MANAGEMENT
# =============================

def get_or_create_label(service, name):
    labels = service.users().labels().list(userId='me').execute()
    for label in labels['labels']:
        if label['name'] == name:
            return label['id']

    label = service.users().labels().create(
        userId='me',
        body={
            'name': name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
    ).execute()

    return label['id']

def apply_label(service, message_id, label_name):
    label_id = get_or_create_label(service, label_name)

    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': [label_id]}
    ).execute()

# =============================
# AI CLASSIFICATION
# =============================

def classify_email(email_text):

    prompt = f"""
You are an AI email classifier.

Classify the email into one of:
- urgent
- follow_up
- informational
- marketing
- ignore

Return JSON only:
{{
    "classification": "",
    "reasoning": "",
    "reply": ""
}}

Email:
{email_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

# =============================
# SELF CRITIQUE (SILENT)
# =============================

def critique(email_text, decision):

    prompt = f"""
Evaluate this classification.

Email:
{email_text}

Decision:
{decision}

Respond only:
good
or
incorrect
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()

# =============================
# REPLY
# =============================

def send_reply(service, to_email, reply_text):

    message = f"To: {to_email}\r\n"
    message += "Subject: Re: Automated Response\r\n\r\n"
    message += reply_text

    raw = base64.urlsafe_b64encode(message.encode()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

# =============================
# AGENT LOOP
# =============================

def run():

    print("🚀 Stable AI Email Agent Running...")
    service = authenticate()

    while True:

        results = service.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            maxResults=5
        ).execute()

        messages = results.get('messages', [])

        for msg in messages:

            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = ""
            sender = ""

            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                if header['name'] == 'From':
                    sender = header['value']

            parts = message['payload'].get('parts')
            body = ""

            if parts:
                body = base64.urlsafe_b64decode(
                    parts[0]['body']['data']
                ).decode('utf-8', errors="ignore")

            full_email = f"Subject: {subject}\nFrom: {sender}\n\n{body}"

            print(f"\n📩 {subject}")

            decision = classify_email(full_email)

            verdict = critique(full_email, decision)

            print("🧠 Classification:", decision["classification"])
            print("🔎 Critique:", verdict)

            # APPLY LABELS
            if decision["classification"] == "urgent":
                apply_label(service, msg['id'], "AI-Urgent")
                send_reply(service, sender, decision["reply"])

            elif decision["classification"] == "follow_up":
                apply_label(service, msg['id'], "AI-FollowUp")

            elif decision["classification"] == "informational":
                apply_label(service, msg['id'], "AI-Info")

            elif decision["classification"] == "marketing":
                apply_label(service, msg['id'], "AI-Marketing")
                # archive marketing
                service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={'removeLabelIds': ['INBOX']}
                ).execute()

            # mark as read
            service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            store_memory({
                "timestamp": datetime.now().isoformat(),
                "subject": subject,
                "classification": decision["classification"],
                "critique": verdict
            })

        time.sleep(15)

if __name__ == "__main__":
    run()

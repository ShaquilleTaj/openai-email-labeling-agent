🤖 Autonomous AI Gmail Agent Workshop

This project demonstrates how to build a real autonomous AI agent that:

Connects to Gmail
Detects new emails
Classifies them using an LLM
Applies Gmail labels automatically
Archives marketing emails
Replies to urgent emails
Stores memory of past decisions
Self-critiques its own decisions
This is not just a chatbot — this is a working AI automation system.
🧠 Architecture Overview
Email Arrives
↓
Gmail API (polling every 15 seconds)
↓
OpenAI LLM Classification
↓
Structured JSON Output
↓
Decision Engine
↓
Gmail Label + Action
↓
Memory Storage

📦 Requirements
Python 3.10+ (recommended)

Gmail account
OpenAI API key
Google Cloud project
🔧 Step 1 — Clone or Download Project

Place the following files in one folder:
stable_autonomous_email_agent.py
README.md
You will later add:
credentials.json
.env
token.json (auto-generated)
memory.json (auto-generated)
🔑 Step 2 — Get OpenAI API Key

Go to:
https://platform.openai.com/api-keys

Create a new secret key
Copy it
🔐 Step 3 — Set Up Environment Variables (Recommended)
Option A — Using .env File
Install dependency
pip install python-dotenv

Create a file named:
.env


Add this line:

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

Update the script (if needed)

At the top of your script:

from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

📧 Step 4 — Set Up Gmail API
1️⃣ Create Google Cloud Project

Go to:

https://console.cloud.google.com/

Create a new project.

2️⃣ Enable Gmail API

APIs & Services → Library → Search for “Gmail API” → Enable

3️⃣ Create OAuth Credentials

Go to:

APIs & Services → Credentials → Create Credentials → OAuth Client ID

Choose:
Desktop Application
Download the file.
Rename it:
credentials.json


Place it in the same folder as the script.

📦 Step 5 — Install Dependencies
pip install openai google-auth google-auth-oauthlib google-api-python-client python-dotenv

🚀 Step 6 — Run the Agent
python stable_autonomous_email_agent.py


First run:
Browser will open
Log into Gmail

Approve permissions
token.json will be created automatically
After that:

The agent will:
Check for unread emails every 15 seconds

Classify them
Apply Gmail labels
Archive marketing
Reply to urgent emails
Store decisions in memory.json
🏷️ What Labels Are Created?
The agent automatically creates these Gmail labels:
AI-Urgent
AI-FollowUp
AI-Info
AI-Marketing
Marketing emails are archived automatically.
🧠 Classification Categories

Emails are classified into:
urgent
follow_up
informational
marketing
ignore

🗂️ Memory
All decisions are stored in:
memory.json

Each entry includes:
Timestamp
Subject
Classification
Critique result
⚙️ How It Works

The system uses:
LLM reasoning layer
Deterministic control logic
Gmail API execution
Structured JSON enforcement
Self-critique evaluation
This is a hybrid neural + symbolic automation system.
🔄 Processing Mode
The system operates on:
Unread emails only.
To process everything in Inbox instead, change:
labelIds=['UNREAD']
To:
labelIds=['INBOX']
🛑 Stopping the Agent
Press:
CTRL + C

🧩 Troubleshooting
Invalid Structure Errors
Ensure the OpenAI call includes:
response_format={"type": "json_object"}
Memory JSON Error
If you see:
JSONDecodeError
Delete:
memory.json
And restart.
Python Version Warning
If using Python 3.9, you may see warnings.

Recommended:
Upgrade to Python 3.10+.

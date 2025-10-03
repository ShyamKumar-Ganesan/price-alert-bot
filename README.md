# Automated Price Alert Bot
A Python bot that tracks product prices on Amazon, Flipkart, and Myntra and sends WhatsApp alerts when prices drop.

Features:

--Tracks prices across multiple sites

--Sends WhatsApp notifications via Twilio

--Runs automatically using GitHub Actions

--Handles dynamic site changes

Installation & Setup:

git clone <repo-link>

cd price-alert-bot

pip install -r requirements.txt

Configure Secrets

(Repo)Settings --> Secrets and Variables --> Actions --> New repository Secret

--TWILIO_ACCOUNT_SID

--TWILIO_AUTH_TOKEN

--TWILIO_FROM

--TWILIO_TO

GitHub Actions Setup:

The workflow is already configured to run every hour, but can also be triggered manually.

(Repo)Actions --> Workflow Name --> Select run workflow

Note : This is for personal/hobby use.

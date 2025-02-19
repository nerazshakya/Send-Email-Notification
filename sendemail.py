import smtplib
import os
import datetime
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Get local time
local_timezone = datetime.datetime.now().astimezone().tzinfo
current_time = datetime.datetime.now(local_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')

def get_commit_message():
    try:
        return subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return "No commit message available"

def send_email():
    try:
        # Load input parameters from environment variables
        title = os.getenv("INPUT_TITLE", "Workflow Notification")
        status = os.getenv("INPUT_STATUS", "Unknown")
        commit = os.getenv("GITHUB_SHA", "Unknown")[:7]  # Short commit hash
        actor = os.getenv("GITHUB_ACTOR", "Unknown User")
        event = os.getenv("GITHUB_EVENT_NAME", "Unknown Event")
        repo = os.getenv("GITHUB_REPOSITORY", "Unknown Repo")
        branch = os.getenv("GITHUB_REF_NAME", "Unknown Branch")
        commit_message = get_commit_message()
        run_id = os.getenv("GITHUB_RUN_ID", "Unknown Run ID")
        github_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
        environ = os.getenv("INPUT_ENVIRON", "N/A")
        stage = os.getenv("INPUT_STAGE", "N/A")
        app = os.getenv("INPUT_APP", "N/A")

        repo_url = f"{github_url}/{repo}/tree/{branch}"
        commit_url = f"{github_url}/{repo}/commit/{commit}"
        build_url = f"{github_url}/{repo}/actions/runs/{run_id}"

        # Adaptive Card JSON directly in Python
        adaptive_card_json = f"""
        {{
            "type": "message",
            "attachments": [{{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {{
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.6",
                    "body": [
                        {{
                            "type": "Container",
                            "items": [
                                {{
                                    "type": "TextBlock",
                                    "size": "medium",
                                    "weight": "bolder",
                                    "text": "{title}",
                                    "spacing": "none"
                                }},
                                {{
                                    "type": "TextBlock",
                                    "size": "small",
                                    "weight": "bolder",
                                    "text": "RUN ID #{run_id} (Commit {commit})",
                                    "spacing": "none"
                                }},
                                {{
                                    "type": "TextBlock",
                                    "size": "small",
                                    "weight": "bolder",
                                    "text": "By @{actor} on {current_time}",
                                    "spacing": "none"
                                }},
                                {{
                                    "type": "FactSet",
                                    "separator": true,
                                    "spacing": "Padding",
                                    "facts": [
                                        {{"title": "Environment", "value": "{environ.upper()}"}},
                                        {{"title": "Application", "value": "{app.upper()}"}},
                                        {{"title": "Stage", "value": "{stage.upper()}"}},
                                        {{"title": "Event Type", "value": "{event.upper()}"}},
                                        {{"title": "Branch", "value": "{branch}"}},
                                        {{"title": "Status", "value": "{status.upper()}"}},
                                        {{"title": "Commit Message", "value": "{commit_message}"}}
                                    ]
                                }}
                            ]
                        }},
                        {{
                            "type": "Container",
                            "items": [
                                {{
                                    "type": "ActionSet",
                                    "actions": [
                                        {{"type": "Action.OpenUrl", "title": "Repository", "style": "positive", "url": "{repo_url}"}},
                                        {{"type": "Action.OpenUrl", "title": "Workflow Status", "style": "positive", "url": "{build_url}"}},
                                        {{"type": "Action.OpenUrl", "title": "Review Diffs", "style": "positive", "url": "{commit_url}"}}
                                    ]
                                }}
                            ]
                        }}
                    ]
                }}
            }}]
        }}
        """

        # Email configuration
        SMTP_SERVER = os.getenv("SMTP_SERVER")
        SMTP_PORT = int(os.getenv("SMTP_PORT", 25))
        SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        FROM_EMAIL = os.getenv("FROM_EMAIL")
        TO_EMAIL = os.getenv("TO_EMAIL")

        email_html = f"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>
            <h3>Workflow Status Notification</h3>
            <p>Your CI/CD pipeline has completed successfully!</p>
            <p><b>Note:</b> This email contains an Adaptive Card. Please view it in Outlook.</p>
            <p><b>Title:</b> {title}</p>
            <p><b>Status:</b> {status}</p>
            <p><b>Commit:</b> {commit} - {commit_message}</p>
            <p><a href="{repo_url}">Repository</a> | <a href="{build_url}">Workflow Status</a> | <a href="{commit_url}">Review Diffs</a></p>
        </body>
        </html>
        """

        # Create email message
        msg = MIMEMultipart("alternative")
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = f"Workflow Status Notification: {status}"

        # Attach HTML content
        msg.attach(MIMEText(email_html, "html"))

        # Attach Adaptive Card as a separate MIME part for Outlook
        adaptive_card_part = MIMEText(adaptive_card_json, "json")
        adaptive_card_part.add_header("Content-Disposition", "attachment", filename="adaptive_card.json")
        msg.attach(adaptive_card_part)

        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())

        print("✅ Email with Adaptive Card sent successfully!")
    
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        exit(1)

if __name__ == "__main__":
    send_email()

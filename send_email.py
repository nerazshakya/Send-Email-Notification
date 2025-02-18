import smtplib
import pytz
import datetime
import subprocess
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
local_timezone = datetime.datetime.now().astimezone().tzinfo

# Format time for display
current_time = datetime.datetime.now(local_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
def send_email():
    try:
        # Load input parameters from environment variables
        title = os.getenv("TITLE", "Workflow Notification")
        #run_id = os.getenv("RUN_ID", "1234")
        #commit = os.getenv("COMMIT", "abcdef123456")
        #actor = os.getenv("ACTOR", "github-user")
        #current_time = os.getenv("CURRENT_TIME", "2025-02-18 12:00:00")
        environ = os.getenv("ENVIRON", "production")
        app = os.getenv("APP", "MyApp")
        stage = os.getenv("STAGE", "build")
        event = os.getenv("EVENT", "push")
        branch = os.getenv("BRANCH", "main")
        status = os.getenv("STATUS", "success")
        commit_message = os.getenv("COMMIT_MESSAGE", "Initial commit")
        github_url = os.getenv('GITHUB_SERVER_URL','https://github.com')
        commit = os.getenv('GITHUB_SHA', 'Unknown')[:7]  # Short commit hash
        actor = os.getenv('GITHUB_ACTOR', 'Unknown User')
        event = os.getenv('GITHUB_EVENT_NAME', 'Unknown Event')
        repo = os.getenv('GITHUB_REPOSITORY', 'Unknown Repo')
        branch = os.getenv('GITHUB_REF_NAME', 'Unknown Branch')
        #commit_message = os.getenv('GITHUB_COMMIT_MESSAGE', 'No commit message found')
        commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()
        run_id = os.getenv('GITHUB_RUN_ID', '')

        
        repo_url = f"{github_url}/{repo}/tree/{branch}"
        commit_url = f"{github_url}/{repo}/commit/{commit}"
        build_url = f"{github_url}/{repo}/actions/runs/{run_id}"



# Get the absolute path of the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "adaptive_card.json")

            # Load Adaptive Card template
        with open(file_path, "r") as file:
            adaptive_card_template = file.read()

        # Load Adaptive Card template from the repo
        #with open("adaptive_card.json", "r") as file:
        #    adaptive_card_template = file.read()

        # Replace placeholders with dynamic values
        adaptive_card_json = (
            adaptive_card_template
            .replace("{TITLE}", title)
            .replace("{RUN_ID}", run_id)
            .replace("{COMMIT}", commit)
            .replace("{ACTOR}", actor)
            .replace("{CURRENT_TIME}", current_time)
            .replace("{ENVIRON}", environ)
            .replace("{APP}", app)
            .replace("{STAGE}", stage)
            .replace("{EVENT}", event)
            .replace("{BRANCH}", branch)
            .replace("{STATUS}", status)
            .replace("{COMMIT_MESSAGE}", commit_message)
            .replace("{REPO_URL}", repo_url)
            .replace("{BUILD_URL}", build_url)
            .replace("{COMMIT_URL}", commit_url)
        )

        # Email configuration
        SMTP_SERVER = os.getenv("SMTP_SERVER")
        SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
        SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        FROM_EMAIL = os.getenv("FROM_EMAIL")
        TO_EMAIL = os.getenv("TO_EMAIL")

        adaptive_card_script = f"""
        <script type="application/adaptivecard+json">
        {adaptive_card_json}
        </script>
        """

        email_html = f"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            {adaptive_card_script}
        </head>
        <body>
            <h3>Workflow Status Notification</h3>
            <p>Your CI/CD pipeline has completed successfully!</p>
            <p><b>Note:</b> This email contains an Adaptive Card. Please view it in Outlook.</p>
        </body>
        </html>
        """

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = "Workflow Status Notification"
        msg.attach(MIMEText(email_html, "html"))

        # Send email via SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        server.quit()

        print("✅ Email with Adaptive Card sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        exit(1)

if __name__ == "__main__":
    send_email()

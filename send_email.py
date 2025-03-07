import smtplib
import os
import datetime
import pytz
import subprocess
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from jinja2 import Template

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

        repo_url = urllib.parse.quote(f"{github_url}/{repo}/tree/{branch}", safe=':/?=')
        commit_url = urllib.parse.quote(f"{github_url}/{repo}/commit/{commit}", safe=':/?=')
        build_url = urllib.parse.quote(f"{github_url}/{repo}/actions/runs/{run_id}", safe=':/?=')
        #f"{github_url}/{repo}/tree/{branch}"
        #commit_url = f"{github_url}/{repo}/commit/{commit}"
        #build_url = f"{github_url}/{repo}/actions/runs/{run_id}"
        
        email_variables = {
            "current_time": current_time,
            "title": title,
            "status": status,
            "commit": commit,
            "actor": actor,
            "event": event,
            "repo": repo,
            "branch": branch,
            "environ": environ,
            "stage": stage,
            "app": app,
            "commit_message": commit_message,
            "run_id": run_id,
            "repo_url": repo_url,
            "commit_url": commit_url,
            "build_url": build_url
        }


        # Email configuration
        SMTP_SERVER = os.getenv("SMTP_SERVER")
        SMTP_PORT = int(os.getenv("SMTP_PORT", 25))
        SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        FROM_EMAIL = os.getenv("FROM_EMAIL")
        TO_EMAIL = os.getenv("TO_EMAIL")
        CC_EMAIL = os.getenv("CC_EMAIL")
        BCC_EMAIL = os.getenv("BCC_EMAIL")
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        html_file_path = os.path.join(script_dir, "templates", "email_template.html")
        css_file_path = os.path.join(script_dir, "templates", "style.css")
        
        
        with open(html_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        with open(css_file_path, "r", encoding="utf-8") as file:
            css_styles = file.read()

            
                # Render the HTML with Jinja2
        template = Template(html_content)
        rendered_html = template.render(email_variables)

        # Embed CSS into HTML inside <style> tags
        #html_content = html_content.replace("<!-- INLINE_CSS -->", f"<style>{css_styles}</style>")
        final_html = rendered_html
        
        # Handle multiple emails in TO_EMAIL (comma or semicolon separated)
        to_emails = [email.strip() for email in (TO_EMAIL or '').replace(';', ',').split(',')] if TO_EMAIL else []
        cc_emails = [email.strip() for email in (CC_EMAIL or '').replace(';', ',').split(',')] if CC_EMAIL else []
        bcc_emails = [email.strip() for email in (BCC_EMAIL or '').replace(';', ',').split(',')] if BCC_EMAIL else []


        #to_emails_str = ", ".join(to_emails)
            # Create email message
        msg = MIMEMultipart("alternative")
        msg["From"] = FROM_EMAIL
        msg["To"] = ", ".join(to_emails)
        msg["CC"] = ", ".join(cc_emails)
        msg["BCC"] = ", ".join(bcc_emails)
        msg["Subject"] = f"GitHub workflow status: {status}"

            # Attach HTML content
        msg.attach(MIMEText(final_html, "html")) 
        
        all_recipients = to_emails + cc_emails + bcc_emails  



        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, all_recipients, msg.as_string())
            server.quit()

        print("✅ Email with Adaptive Card sent successfully!")
    
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        exit(1)

if __name__ == "__main__":
    send_email()

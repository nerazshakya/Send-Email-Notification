import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

class AdaptiveCardEmailSender:
    def __init__(self):
        # Initialize email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 25))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.to_email = os.getenv("TO_EMAIL")
        
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def load_adaptive_card_template(self):
        """
        Loads the adaptive card template from the JSON file.
        The file should be in the same directory as the script.
        """
        try:
            # Construct the full path to the adaptive_card.json file
            template_path = os.path.join(self.script_dir, "adaptive_card.json")
            
            # Read and return the template content
            with open(template_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            print("❌ Error: adaptive_card.json template file not found")
            raise
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in adaptive_card.json template")
            raise

    def replace_template_placeholders(self, template, workflow_data):
        """
        Replaces all placeholders in the template with actual workflow data.
        """
        replacements = {
            "{TITLE}": workflow_data.get("title", "Workflow Notification"),
            "{STATUS}": workflow_data.get("status", "Unknown"),
            "{ENVIRON}": workflow_data.get("environ", ""),
            "{APP}": workflow_data.get("app", ""),
            "{STAGE}": workflow_data.get("stage", ""),
            "{COMMIT}": workflow_data.get("commit", ""),
            "{ACTOR}": workflow_data.get("actor", ""),
            "{BRANCH}": workflow_data.get("branch", ""),
            "{CURRENT_TIME}": workflow_data.get("current_time", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "{COMMIT_MESSAGE}": workflow_data.get("commit_message", "No commit message available"),
            "{REPO_URL}": workflow_data.get("repo_url", "#"),
            "{BUILD_URL}": workflow_data.get("build_url", "#"),
            "{COMMIT_URL}": workflow_data.get("commit_url", "#"),
            "{RUN_ID}": workflow_data.get("run_id", "")
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))
        return result

    def create_email_content(self, adaptive_card_json):
        """
        Creates the HTML email content with the embedded adaptive card.
        """
        return f"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <script type="application/adaptivecard+json">
            {adaptive_card_json}
            </script>
        </head>
        <body>
            <h3>Workflow Status Notification</h3>
            <p>Your CI/CD pipeline has completed. Please check the status below.</p>
            <p><b>Note:</b> This email contains an Adaptive Card. Please view it in Outlook.</p>
        </body>
        </html>
        """

    def send_email(self, workflow_data):
        """
        Sends an email with the adaptive card containing workflow information.
        """
        try:
            # Load and process the adaptive card template
            template = self.load_adaptive_card_template()
            adaptive_card_json = self.replace_template_placeholders(template, workflow_data)
            
            # Validate the resulting JSON
            try:
                json.loads(adaptive_card_json)
            except json.JSONDecodeError:
                print("❌ Error: Template replacement resulted in invalid JSON")
                raise

            # Create email content
            email_html = self.create_email_content(adaptive_card_json)

            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = self.to_email
            msg["Subject"] = workflow_data.get("title", "Workflow Status Notification")
            msg.attach(MIMEText(email_html, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, self.to_email, msg.as_string())
            
            print("✅ Email with Adaptive Card sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Collect workflow data from environment variables
    workflow_data = {
        "title": os.getenv("INPUT_TITLE", "Workflow Notification"),
        "status": os.getenv("INPUT_STATUS", "Unknown"),
        "environ": os.getenv("INPUT_ENVIRON", ""),
        "app": os.getenv("INPUT_APP", ""),
        "stage": os.getenv("INPUT_STAGE", ""),
        "commit": os.getenv("GITHUB_SHA", "")[:7],
        "actor": os.getenv("GITHUB_ACTOR", ""),
        "branch": os.getenv("GITHUB_REF_NAME", ""),
        "current_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "commit_message": os.getenv("COMMIT_MESSAGE", "No commit message available"),
        "repo_url": os.getenv("REPO_URL", "#"),
        "build_url": os.getenv("BUILD_URL", "#"),
        "commit_url": os.getenv("COMMIT_URL", "#"),
        "run_id": os.getenv("GITHUB_RUN_ID", "")
    }
    
    # Send the email
    sender = AdaptiveCardEmailSender()
    sender.send_email(workflow_data)

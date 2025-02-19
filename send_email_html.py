import smtplib
import os
import datetime
import pytz
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


        

        # Email configuration
        SMTP_SERVER = os.getenv("SMTP_SERVER")
        SMTP_PORT = int(os.getenv("SMTP_PORT", 25))
        SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        FROM_EMAIL = os.getenv("FROM_EMAIL")
        TO_EMAIL = os.getenv("TO_EMAIL")

        adaptive_card_json = f"""
        <script type="application/adaptivecard+json">
        {{
                    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
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
            </script>
        """
            # Create email message
        msg = MIMEMultipart("alternative")
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = f"Workflow Status Notification: {status}"

        # Attach HTML content
    
        html_content = f"""<!doctype html>
    <html lang="en">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Simple Transactional Email</title>
    <style media="all" type="text/css">
    
    body {
        font-family: Helvetica, sans-serif;
        -webkit-font-smoothing: antialiased;
        font-size: 16px;
        line-height: 1.3;
        -ms-text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%;
    }
    
    table {
        border-collapse: separate;
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
        width: 100%;
    }
    
    table td {
        font-family: Helvetica, sans-serif;
        font-size: 16px;
        vertical-align: top;
    }

    
    body {
        background-color: #f4f5f6;
        margin: 0;
        padding: 0;
    }
    
    .body {
        background-color: #f4f5f6;
        width: 100%;
    }
    
    .container {
        margin: 0 auto !important;
        max-width: 600px;
        padding: 0;
        padding-top: 24px;
        width: 600px;
    }
    
    .content {
        box-sizing: border-box;
        display: block;
        margin: 0 auto;
        max-width: 600px;
        padding: 0;
    }

    .main {
        background: #ffffff;
        border: 1px solid #eaebed;
        border-radius: 16px;
        width: 100%;
    }
    
    .wrapper {
        box-sizing: border-box;
        padding: 24px;
    }
    
    .footer {
        clear: both;
        padding-top: 24px;
        text-align: center;
        width: 100%;
    }
    
    .footer td,
    .footer p,
    .footer span,
    .footer a {
        color: #9a9ea6;
        font-size: 16px;
        text-align: center;
    }
    
    p {
        font-family: Helvetica, sans-serif;
        font-size: 16px;
        font-weight: normal;
        margin: 0;
        margin-bottom: 16px;
    }
    
    a {
        color: #0867ec;
        text-decoration: underline;
    }
    
    .btn {
        box-sizing: border-box;
        min-width: 100% !important;
        width: 100%;
    }
    
    .btn > tbody > tr > td {
        padding-bottom: 16px;
    }
    
    .btn table {
        width: auto;
    }
    
    .btn table td {
        background-color: #ffffff;
        border-radius: 4px;
        text-align: center;
    }
    
    .btn a {
        background-color: #ffffff;
        border: solid 2px #0867ec;
        border-radius: 4px;
        box-sizing: border-box;
        color: #0867ec;
        cursor: pointer;
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        margin: 0;
        padding: 12px 24px;
        text-decoration: none;
        text-transform: capitalize;
    }
    
    .btn-primary table td {
        background-color: #0867ec;
    }
    
    .btn-primary a {
        background-color: #0867ec;
        border-color: #0867ec;
        color: #ffffff;
    }
    
    @media all {
    .btn-primary table td:hover {
        background-color: #04953e !important;
    }
    .btn-primary a:hover {
        background-color: #04953e !important;
        border-color: #04953e !important;
    }
    }
        
    .last {
        margin-bottom: 0;
    }
    
    .first {
        margin-top: 0;
    }
    
    .align-center {
        text-align: center;
    }
    
    .align-right {
        text-align: right;
    }
    
    .align-left {
        text-align: left;
    }
    
    .text-link {
        color: #0867ec !important;
        text-decoration: underline !important;
    }
    
    .clear {
        clear: both;
    }
    
    .mt0 {
        margin-top: 0;
    }
    
    .mb0 {
        margin-bottom: 0;
    }
    
    .preheader {
        color: transparent;
        display: none;
        height: 0;
        max-height: 0;
        max-width: 0;
        opacity: 0;
        overflow: hidden;
        mso-hide: all;
        visibility: hidden;
        width: 0;
    }
    
    .powered-by a {
        text-decoration: none;
    }
    
    @media only screen and (max-width: 640px) {
        .main p,
        .main td,
        .main span {
        font-size: 16px !important;
        }
        .wrapper {
        padding: 8px !important;
        }
        .content {
        padding: 0 !important;
        }
    .container {
        padding: 0 !important;
        padding-top: 8px !important;
        width: 100% !important;
        }
        .main {
        border-left-width: 0 !important;
        border-radius: 0 !important;
        border-right-width: 0 !important;
        }
    .btn table {
        max-width: 100% !important;
        width: 100% !important;
        }
    .btn a {
        font-size: 16px !important;
        max-width: 100% !important;
        width: 100% !important;
        }

    td {
        padding: 0 10px 0 0;
        }
    }
    
    @media all {
    .ExternalClass {
        width: 100%;
        }
    .ExternalClass,
    .ExternalClass p,
    .ExternalClass span,
    .ExternalClass font,
    .ExternalClass td,
    .ExternalClass div {
        line-height: 100%;
        }
    .apple-link a {
        color: inherit !important;
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
        text-decoration: none !important;
        }
    #MessageViewBody a {
        color: inherit;
        text-decoration: none;
        font-size: inherit;
        font-family: inherit;
        font-weight: inherit;
        line-height: inherit;
        }
    }
    </style>
    </head>
    <body>
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
    <tr>
        <!--<td>&nbsp;</td> -->
        <td class="container">
        <div class="content">

            <!-- START CENTERED WHITE CONTAINER -->
            <span class="preheader">Preview</span>
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="main">

            <!-- START MAIN CONTENT AREA -->
            <tr>
                <td class="wrapper">
                <p><b>GitHub Notifications</b></p>
                <p>"Daimler-Truck-Financial-Service {title} ".</p>
                <p>"RUN ID #{run_id} (Commit {commit})".</p>
                <p>"By @{actor} on {current_time}".</p>
                <p>
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="">
                <tbody>
                    <tr>
                        <td align="left">
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tbody>
                            <tr >
                                <td>Environment:</td>
                                <td>{environ.upper()}</td>
                            </tr>
                            <tr>
                                <td>Application:</td>
                                <td>{app.upper()}</td>
                            </tr>
                            <tr>
                                <td>Stage:</td>
                                <td>{stage.upper()}</td>
                            </tr>
                            <tr>
                                <td>Event Type:</td>
                                <td>{event.upper()}</td>
                            </tr>
                            <tr>
                                <td>Branch:</td>
                                <td>{branch}</td>
                            </tr>
                            <tr>
                                <td>Status:</td>
                                <td>{status.upper()}</td>
                            </tr>
                            <tr >
                                <td style="white-space:nowrap">Commit Message:</td>
                                <td>{commit_message}</td>
                            </tr>
                            </tbody>
                        </table>
                        </td>
                    </tbody>
                </table>
                </p>
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                    <tbody>
                    <tr>
                        <td align="left">
                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tbody>
                            <tr>
                                <td> <a href="http://htmlemail.io" target="_blank">Repository</a> </td>
                            </tr>
                            </tbody>
                        </table>
                        </td>
                        <td align="center">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tbody>
                                <tr>
                                <td> <a href="http://htmlemail.io" target="_blank">Workflow Status</a> </td>
                                </tr>
                            </tbody>
                            </table>
                        </td>
                        <td align="right">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                            <tbody>
                                <tr>
                                <td> <a href="http://htmlemail.io" target="_blank">Reveiw Diffs</a> </td>
                                </tr>
                            </tbody>
                            </table>
                        </td>
                    </tr>
                    </tbody>
                </table>
                </td>
            </tr>
            </table>

        <!--<td>&nbsp;</td> -->
    </tr>
    </table>
    </body>
    </html>"""    
            
        msg.attach(MIMEText(html_content, "html"))      



        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
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

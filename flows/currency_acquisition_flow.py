import os
import smtplib
import json
from email.message import EmailMessage
from prefect import flow, get_run_logger
from prefect.blocks.system import Secret
from utils.exchange_rate_fetcher import fetch_last_month_rates


def send_email_with_attachment(file_path, recipient_email, logger):
    """
    Send the generated file via email.
    Requires a Prefect Secret block named 'email-config' containing a JSON string:
    {
        "smtp_host": "smtp.office365.com",
        "smtp_port": 587,
        "sender_email": "your_email@example.com",
        "sender_password": "your_password"
    }
    """
    try:
        # Load configuration from Secret block
        try:
            secret_block = Secret.load("email-config")
            config = json.loads(secret_block.get())
        except ValueError:
            logger.warning("Secret block 'email-config' not found.")
            logger.warning("To enable email delivery, create a Secret block named 'email-config' with your SMTP details in JSON format.")
            return
        except json.JSONDecodeError:
            logger.error("Secret block 'email-config' must contain valid JSON.")
            return

        smtp_host = config.get("smtp_host")
        smtp_port = config.get("smtp_port", 587)
        sender_email = config.get("sender_email")
        sender_password = config.get("sender_password")

        if not all([smtp_host, sender_email, sender_password]):
            logger.error("Missing required email configuration (smtp_host, sender_email, sender_password).")
            return

        # Create the email
        msg = EmailMessage()
        msg['Subject'] = f"Data Acquisition: {os.path.basename(file_path)}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content("Please find the attached currency exchange rate data.")

        # Attach the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(file_path)
        
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Send the email
        logger.info(f"Connecting to SMTP server {smtp_host}:{smtp_port}...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        logger.info(f"Successfully sent email to {recipient_email}")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")


@flow(name="currency_acquisition_flow")
def currency_acquisition_flow():
    """
    Fetch last month's FX rates (idempotent).
    Scheduled monthly via Prefect Cloud.
    """
    logger = get_run_logger()
    logger.info("Running monthly FX acquisition task...")

    fx_path = fetch_last_month_rates()

    logger.info(f"FX acquisition complete: {fx_path}")
    
    # Attempt to send email
    # Hardcoded recipient as requested
    recipient = "yli@intracen.org"
    send_email_with_attachment(fx_path, recipient, logger)
    
    return fx_path


if __name__ == "__main__":
    currency_acquisition_flow()

import os

import requests
import resend

REVIEWER_EMAIL = os.environ.get("AR_REVIEWER_EMAIL", "andrew.mendoza@dict.gov.ph")
REPORT_OWNER_EMAIL = os.environ.get("AR_OWNER_EMAIL", "matthewjericho.silva@dict.gov.ph")
SENDER = os.environ.get("AR_SENDER_EMAIL", "noreply@dict.gov.ph")
REVIEWER_NAME = os.environ.get("AR_REVIEWER_NAME", "Sir Andrew")
REPORT_OWNER_NAME = os.environ.get("AR_OWNER_NAME", "Matthew Jericho Silva")


def send_telegram_confirmation(period: str, resend_response: dict | None) -> None:
    bot_token = os.environ.get("AR_TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("AR_TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return

    resend_id = resend_response.get("id") if isinstance(resend_response, dict) else None
    message = (
        "Accomplishment Report draft sent to your email for review.\n\n"
        f"Period: {period}\n"
        f"Sent to: {REPORT_OWNER_EMAIL}\n"
        f"Next step: Review the PDF and Excel. If good, forward the PDF to {REVIEWER_EMAIL} ({REVIEWER_NAME}) for cosigning."
    )
    if resend_id:
        message += f"\nResend ID: {resend_id}"

    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
            timeout=30,
        ).raise_for_status()
    except Exception as error:
        print(f"telegram_confirmation_failed error={error}", flush=True)


def send_report_email(api_key: str, pdf_bytes: bytes, period: str, docx_bytes: bytes | None = None) -> None:
    resend.api_key = api_key

    base_filename = f"AR - Silva, Matthew Jericho - {period}"
    attachments = [{"filename": f"{base_filename}.pdf", "content": list(pdf_bytes)}]
    if docx_bytes is not None:
        attachments.append({"filename": f"{base_filename}.docx", "content": list(docx_bytes)})

    response = resend.Emails.send({
        "from": SENDER,
        "to": [REPORT_OWNER_EMAIL],
        "subject": f"AR Draft Ready for Review - {period}",
        "text": (
            f"Hi {REPORT_OWNER_NAME},\n\n"
            f"Your Accomplishment Report draft for {period} is ready.\n\n"
            "Attached:\n"
            f"- {base_filename}.pdf — the generated report\n"
            + (f"- {base_filename}.docx — editable Word document if you need to make changes (opens in Google Docs)\n" if docx_bytes else "")
            + f"\nOnce you're happy with it, forward the PDF to {REVIEWER_NAME} ({REVIEWER_EMAIL}) for review and cosigning.\n\n"
            "This was generated automatically."
        ),
        "attachments": attachments,
    })
    send_telegram_confirmation(period, response)

import smtplib

from celery import Celery
from email.message import EmailMessage

from config import MAIL_USERNAME, RESET_PASSWORD_REDIRECT_URL, SECRET, RESET_PASSWORD_EXPIRY_MINUTES, MAIL_SERVER, \
    MAIL_PASSWORD, MAIL_PORT, REDIS_HOST, REDIS_PORT

celery = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{int(REDIS_PORT)}/0",
    backend=f"redis://{REDIS_HOST}:{int(REDIS_PORT)}/0"
)


def get_email_objects(user_email, token):
    email = EmailMessage()
    email['Subject'] = f'Verify email'
    email['From'] = MAIL_USERNAME
    email['To'] = user_email

    forget_url_link = f"{RESET_PASSWORD_REDIRECT_URL}/{SECRET}"

    email.set_content(
        f"""
            <html>
            <body>
                <p>
                    Hello, 😊<br><br>
                    You have requested to reset your password for <b>JetBrains</b>.<br>
                    Please click on the following link within {RESET_PASSWORD_EXPIRY_MINUTES} minutes to reset your password:<br>
                    <a href="{forget_url_link}">{forget_url_link}</a><br><br>
                    Your token {token} <br>
                    If you did not request this reset, please ignore this email. 🙅‍♂️<br><br>
                    Regards, <br>
                    JetBrains Team 🚀
                </p>
            </body>
            </html>
        """,
        subtype='html',
    )
    return email


@celery.task
def send_mail_for_forget_password(email: str, token: str):
    email = get_email_objects(email, token)
    with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(email)

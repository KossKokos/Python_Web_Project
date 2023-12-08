from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import service_auth
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Alghorithmic",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str) -> None:
    """
    The send_email function sends an email to the user with a link to confirm their email address.

        The function takes in three arguments:
            email: the user's email address, which is used as a unique identifier for them.
            username: the username of the user who is registering for an account. 
            host: this is where we are hosting our application, which will be used as part of our URL when sending out emails.
    
    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the email template
    :param host: str: Pass the hostname of the server to be used in the link for email verification
    :return: None
    """
    try:
        token_verification = await service_auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: EmailStr, username: str, host: str) -> None:
    """
    The send_reset_password_email function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The user's username.
            host (str): The hostname of the server where this function is being called from, e.g., &quot;localhost&quot; or &quot;127.0.0.&quot; 
    
    :param email: EmailStr: Specify the email address of the user who is requesting a password reset
    :param username: str: Pass the username to the template, so it can be displayed in the email
    :param host: str: Pass the hostname of the server to the email template
    :return: None
    """
    try:
        token_verification = await service_auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset password ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
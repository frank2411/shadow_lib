import smtplib
import ssl
from email.message import EmailMessage
from typing import Any, List

from flask import current_app, render_template

#  https://docs.python.org/3.7/library/email.examples.html


class Notify:  # pragma: no cover
    def __init__(self, *args: List, **kwargs: Any) -> None:
        self.email_template = kwargs["email_template"]
        self.subject = kwargs["subject"]
        self.receiver = kwargs["receiver"]
        self.data = kwargs["data"]
        self.sender = kwargs.get(
            "sender", current_app.config.get("EMAIL_SENDER_ADDRESS")
        )
        self.kwargs = kwargs

        self.is_testing = current_app.config.get("TESTING")

        # Sender server configs
        self.email_host = current_app.config.get("EMAIL_HOST")
        self.email_host_port = current_app.config.get("EMAIL_PORT")
        self.email_use_tls = current_app.config.get("EMAIL_USE_TLS")
        self.email_host_user = current_app.config.get("EMAIL_HOST_USER")
        self.email_host_password = current_app.config.get("EMAIL_HOST_PASSWORD")
        self.is_localhost = True if self.email_host == "localhost" else False

        self.message = EmailMessage()
        self.set_context()
        self.set_text()
        self.set_html()

    def set_context(self) -> None:
        self.context = self.data

    def set_html(self) -> None:
        template_name = f"emails/{self.email_template}.html"
        self.html = render_template(template_name, **self.context)

        self.message.add_alternative(self.html, subtype="html")

    def set_text(self) -> None:
        template_name = f"emails/{self.email_template}.txt"
        self.text = render_template(template_name, **self.context)

        self.message.set_content(self.text)

    def send(self) -> Any:

        self.message["Subject"] = self.subject
        self.message["From"] = self.sender
        self.message["To"] = self.receiver

        if self.is_testing:
            current_app.notify_message = self.message
            return

        mailserver = smtplib.SMTP(self.email_host, self.email_host_port)

        if self.email_use_tls and not self.is_localhost:
            ssl_context = ssl.create_default_context()
            if mailserver.starttls(context=ssl_context)[0] != 220:
                return False  # cancel if connection is not encrypted

        if not self.is_localhost:
            mailserver.login(self.email_host_user, self.email_host_password)
        mailserver.send_message(self.message)
        mailserver.quit()

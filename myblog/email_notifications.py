import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from myblog.models import User
from abc import ABC, abstractmethod
from flask import current_app


class EmailSender(ABC):
    TYPE = None

    def __init__(self):
        self.context = ssl.create_default_context()
        self.message = MIMEMultipart("alternative")
        with current_app.app_context():
            self.smtp_server = current_app.config["MAIL_SERVER"]
            self.port = current_app.config["MAIL_PORT"]
            self.sender_email = current_app.config["MAIL_USERNAME"]
            self.password = current_app.config["MAIL_PASSWORD"]
        self.message["From"] = self.sender_email

    def send_mail(self):
        with smtplib.SMTP_SSL(
            self.smtp_server, self.port, context=self.context
        ) as server:
            current_app.logger.info("Logging to email server")
            server.login(self.sender_email, self.password)
            current_app.logger.info(
                f"Sending {self.TYPE} email notification to {self.message['To']}"
            )
            server.sendmail(
                self.sender_email, self.message["To"], self.message.as_string()
            )

    def add_plain_message(self, text: str):
        self.message.attach(MIMEText(text, "plain"))

    def add_html_message(self, html: str):
        self.message.attach(MIMEText(html, "html"))

    def add_subject(self, subj: str):
        self.message["Subject"] = subj

    def add_receiver_email(self, receiver_email: str):
        self.message["To"] = receiver_email

    @classmethod
    @abstractmethod
    def build_message(self, *args, **kwargs):
        pass


class OpCommentNotificationEmailSender(EmailSender):
    TYPE = "OP"

    @classmethod
    def build_message(
        cls, post_url: str, comment_id: str, receiver: User, commenter: User
    ):
        obj = cls()
        obj.add_receiver_email(receiver.email)
        obj.add_subject("Comment notification")
        post_url = post_url + f"#comment_{comment_id}"
        text = f"""\
        Hi {receiver.username},
        User {commenter.username} commented on this post: {post_url}.
        You're receiving this email because you're the original poster on the post thread.
        """
        obj.add_plain_message(text)
        html = f"""\
        <html>
        <body>
            <p>Hi {receiver.username},<br>
            User {commenter.username} commented on <a href="{post_url}">this post</a>.<br>
            You're receiving this email because you're the original poster on the post thread.
            </p>
        </body>
        </html>
        """
        obj.add_html_message(html)
        return obj


class TagNotificationEmailSender(EmailSender):
    TYPE = "TAGGED"

    @classmethod
    def build_message(cls, post_url: str, comment_id: str, tagged: User, tagger: User):
        obj = cls()
        obj.add_receiver_email(tagged.email)
        obj.add_subject("Mention notification")
        post_url = post_url + f"#comment_{comment_id}"
        text = f"""\
        Hi {tagged.username},
        User {tagger.username} mentioned you when commenting on this post: {post_url}.
        """
        obj.add_plain_message(text)
        html = f"""\
        <html>
        <body>
            <p>Hi {tagged.username},<br>
            User {tagger.username} mentioned you when commenting <a href="{post_url}">this post</a>.
            </p>
        </body>
        </html>
        """
        obj.add_html_message(html)
        return obj

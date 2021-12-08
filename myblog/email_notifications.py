import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from myblog.models import User
from abc import ABC, abstractmethod


class EmailSender(ABC):
    smtp_server = "smtp.gmail.com"
    port = 465
    sender_email = "blblog.notification@gmail.com"

    def __init__(self):
        self.context = ssl.create_default_context()
        self.password = "Vaffanculostronzo94"
        self.message = MIMEMultipart("alternative")
        self.message["From"] = EmailSender.sender_email

    def send_mail(self):
        with smtplib.SMTP_SSL(EmailSender.smtp_server,
                              EmailSender.port,
                              context=self.context) as server:
            server.login(EmailSender.sender_email, self.password)
            server.sendmail(EmailSender.sender_email,
                            self.message["To"],
                            self.message.as_string())

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

    @classmethod
    def build_message(cls, post_url: str, comment_id: str,
                      receiver: User, commenter: User):
        obj = cls()
        obj.add_receiver_email(receiver.email)
        obj.add_subject("Comment notification")
        post_url = post_url + f'#comment_{comment_id}'
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

    @classmethod
    def build_message(cls, post_url: str, comment_id: str,
                      tagged: User, tagger: User):
        obj = cls()
        obj.add_receiver_email(tagged.email)
        obj.add_subject("Mention notification")
        post_url = post_url + f'#comment_{comment_id}'
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

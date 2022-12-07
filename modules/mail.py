import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from abc import ABCMeta, abstractmethod

from modules import utils


class IBuilder(metaclass=ABCMeta):
    "The Builder Interface"

    @staticmethod
    @abstractmethod
    def subject(subject):
        "Build subject"

    @staticmethod
    @abstractmethod
    def content(content):
        "Build content"

    @staticmethod
    @abstractmethod
    def receivers(receivers):
        "Build receivers"

    @staticmethod
    @abstractmethod
    def build():
        "Return the final product"


class MailBuilder(IBuilder):
    def __init__(self):
        self._mail_components = Mail()

    def subject(self, subject):
        self._mail_components._subject = subject
        return self

    def content(self, content):
        self._mail_components._content = content
        return self

    def receivers(self, receivers):
        self._mail_components._receivier_list = receivers
        return self

    def build(self):
        return self._mail_components


class Mail():

    def __init__(self):
        self._notifier_mail_addres = utils.get_config_entry(
            'notifier_mail_addres')
        self._notifier_mail_password = utils.get_config_entry(
            'notifier_mail_password')

        self._subject = ''
        self._content = ''
        self._receivier_list = []

    def send(self):
        message = MIMEMultipart()
        message['From'] = self._notifier_mail_addres
        message['To'] = ','.join(self._receivier_list)

        message['Subject'] = self._subject

        message.attach(MIMEText(self._content, 'plain'))

        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security

        session.login(self._notifier_mail_addres, self._notifier_mail_password)
        session.send_message(
            message, self._notifier_mail_addres, self._receivier_list)
        session.quit()

        print('Mail has been sent')
from __future__ import print_function
import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors, discovery

import telebot
import telebotdata

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

bot = telebot.TeleBot(telebotkey.token)
SCOPES = ['https://mail.google.com/']

if __name__ == '__main__':
    main()


def main():
    service = auth()


def getEmailById(service, id):
    return Email(service.users().messages().get(
        userId='me', id=id).execute())


def sendEmail(service, message):
    try:
        message = (service.users().messages().send(
            userId='me', body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def createEmail(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body


def setEmailAsRead(service, threadId):
    service.users().threads().modify(userId='me', id=threadId,
                                     body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute()


def sendEmailByTelegram(service, email, chat_id):
    bot.send_message(
        chat_id=chat_id, text="{}\n{}\n{}".format(email.titulo, email.hora, email.de))


def getUnreadEmails(service):
    return service.users().messages().list(userId='me', q="is:unread").execute()


def auth():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


class Email:
    def __init__(self, data):
        self.id = data['id']
        self.threadId = data['threadId']
        self.de = 'undefined'
        self.hora = ''
        self.titulo = data['snippet']
        for header in data['payload']['headers']:
            if(header['name'] == 'Date'):
                self.hora = header['value']
            elif(header['name'] == 'Reply-To'):
                self.de = header['value']

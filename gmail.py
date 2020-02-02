from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import telebot
import telebotkey

bot = telebot.TeleBot(telebotkey.token)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']
service = ''


def main():
    global service
    service = auth()
    # Call the Gmail API
    naolidos = getUnreadEmails()
    if('messages' in naolidos):
        data = [sendEmailByTelegram(getEmailById(message['id']))
                for message in naolidos['messages']]
    setAsRead()


def getEmailById(id):
    return Email(service.users().messages().get(
        userId='me', id=id).execute())


def setEmailAsRead(threadId):
    service.users().threads().modify(userId='me', id=threadId,
                                     body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute()


def sendEmailByTelegram(email):
    bot.send_message(
        chat_id=411321208, text="{}\n{}\n{}".format(email.titulo, email.hora, email.de))


def getUnreadEmails():
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


if __name__ == '__main__':
    main()
# [END gmail_quickstart]

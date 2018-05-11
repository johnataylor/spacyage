# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import http.server
import http.client

import json
import asyncio

from botbuilder.schema import (Activity, ActivityTypes, ChannelAccount)
from botframework.connector import ConnectorClient
from botframework.connector.auth import (MicrosoftAppCredentials,
                                         JwtTokenValidation, SimpleCredentialProvider)

import spacy

nlp = spacy.load('en')

def gather_additional_obj(noun, result):
    for child in noun.children:
        if child.dep_ == 'conj' and child.pos_ != 'VERB':
            result.append(child)
            gather_additional_obj(child, result)

def find_obj_for_verb(verb):
    for child in verb.children:
        if child.dep_ == 'dobj':
            result = [child]
            gather_additional_obj(child, result)
            return result
    return None

def form_put(noun):
    conn = http.client.HTTPConnection("0.0.0.0", 8080)
    conn.request("PUT", "/form/" + noun, None)
    response = conn.getresponse()
    return response.status == 201



def form_del(noun):
    conn = http.client.HTTPConnection("0.0.0.0", 8080)
    conn.request("DELETE", "/form/" + noun, None)
    response = conn.getresponse()
    return response.status == 200

def form_get():
    conn = http.client.HTTPConnection("0.0.0.0", 8080)
    conn.request("GET", "/form", None)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    return data


def process_verb(verb, reply):

    if verb.text == 'add':
        objs = find_obj_for_verb(verb)
        added = []
        for obj in objs:
            if form_put(obj.text):
                added.append(obj.text)
        if len(added) == 0:
            reply('Nothing new to add.')
        else:
            replyText = 'added '
            for text in added:
                replyText += text
                replyText += ' '
            reply(replyText)

    elif verb.text == 'remove':
        objs = find_obj_for_verb(verb)
        removed = []
        for obj in objs:
            if form_del(obj.text):
                removed.append(obj.text)
        if len(removed) == 0:
            reply('Nothing to remove.')
        else:
            replyText = 'removed '
            for text in removed:
                replyText += text
                replyText += ' '
            reply(replyText)

    elif verb.text == 'list':
        replyText = form_get()
        reply(replyText)

    else:
        reply("Sorry I don't know how to '{}'".format(verb.text))

def process_command(token, reply):
    text = token.text
    if text == 'list':
        replyText = form_get()
        reply(replyText)
    else:
        reply("I understand this '{}' to be a command but I don't know what to do with it.".format(text))

def process_utterance(text, reply, retry = False):
    doc = nlp(text)
    verbs = [token for token in doc if token.pos_ == 'VERB']
    if len(verbs) > 0:
        for verb in verbs:
            process_verb(verb, reply)
        state['previous'] = text
    elif len(doc) == 1:
        process_command(doc[0], reply)
    else:
        if retry == False:
            process_utterance(state['previous'] + ' ' + text, reply, True)
        else:
            reply("Sorry I don't understand this: '{}'".format(doc.text))

APP_ID = ''
APP_PASSWORD = ''

state = {}
# ----------------------------------------------
# Incoming address from the Bot Connector service 
#  If you are testing in a docker container, 
#  set this to your docker bridge. (ie, 172.17.0.1)
# Otherwise, set to Bot framework.
# ----------------------------------------------
class BotConnectorSvc:
    incoming_address = "192.168.0.1"

class BotRequestHandler(http.server.BaseHTTPRequestHandler):
        

    @staticmethod
    def __create_reply_activity(request_activity, text):
        return Activity(
            type=ActivityTypes.message,
            channel_id=request_activity.channel_id,
            conversation=request_activity.conversation,
            recipient=request_activity.from_property,
            from_property=request_activity.recipient,
            text=text,
            service_url=request_activity.service_url)
    
    
    def __handle_conversation_update_activity(self, activity):
        self.send_response(202)
        self.end_headers()
        if activity.members_added[0].id != activity.recipient.id:
            credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
            reply = BotRequestHandler.__create_reply_activity(activity, 'Hello and welcome to The SpaCy Age!')
            connector = ConnectorClient(credentials, base_url=reply.service_url.replace('localhost', BotConnectorSvc.incoming_address ))
            connector.conversations.send_to_conversation(reply.conversation.id, reply)

    def __handle_message_activity(self, activity):
        self.send_response(200)
        self.end_headers()

        def replyFunction (replyText):
            credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
            connector = ConnectorClient(credentials, base_url=activity.service_url.replace('localhost', BotConnectorSvc.incoming_address))
            reply = BotRequestHandler.__create_reply_activity(activity, replyText)
            connector.conversations.send_to_conversation(reply.conversation.id, reply)

        process_utterance(activity.text, replyFunction)

    
    def __handle_authentication(self, activity):
        # Capture Bot Connector Service address 
        BotConnectorSvc.incoming_address = self.client_address[0]
        credential_provider = SimpleCredentialProvider(APP_ID, APP_PASSWORD)
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(JwtTokenValidation.assert_valid_activity(
                activity, self.headers.get("Authorization"), credential_provider))
            return True
        except Exception as ex:
            self.send_response(401, ex)
            self.end_headers()
            return False
        finally:
            loop.close()

    def __unhandled_activity(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(str(body, 'utf-8'))
        activity = Activity.deserialize(data)

        if not self.__handle_authentication(activity):
            return

        if activity.type == ActivityTypes.conversation_update.value:
            self.__handle_conversation_update_activity(activity)
        elif activity.type == ActivityTypes.message.value:
            self.__handle_message_activity(activity)
        else:
            self.__unhandled_activity()


try:
    # Listen on all available nics
    SERVER = http.server.HTTPServer(('0.0.0.0', 9000), BotRequestHandler)
    print('Started http server')
    SERVER.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    SERVER.socket.close()

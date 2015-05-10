__author__ = 'reverendken'

from slackapi import SlackBotUser, post_message
import json
import random

class BOB(SlackBotUser):
    def __init__(self, api, name, emoji, slap_responses_filename):
        self._name = name
        self._slap_responses = json.load(open(slap_responses_filename, 'rt'))
        self._emoji = emoji
        self._api = api

    @property
    def id(self):
        return self._name

    @property
    def name(self):
        return self._name

    @property
    def emoji(self):
        return self._emoji

    def slap(self, conference, from_whom, trout):
        parms = {'who': '<@%s>' % from_whom.name,
                 'what': trout,
                 'me': self.name}
        message = random.choice(self._slap_responses) % parms
        post_message(conference, message, self)

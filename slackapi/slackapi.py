__author__ = 'reverendken'

import urllib.parse
import os
import json

import requests
from ws4py.client.threadedclient import WebSocketClient

import slackapi.messages


API_BASE = "https://slack.com/api/"
SLACK_TOKEN = None


def func_once(func):
    """A decorator that runs a function only once."""
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated


@func_once
def _slack_token():
    return open(os.path.expanduser("~/.slack/token")).read().strip()


class SlackChannel(object):
    def __init__(self, channel_info):
        self._info = channel_info

    @property
    def id(self):
        return self._info['id']

    @property
    def name(self):
        return self._info['name']


class SlackUser(object):
    def __init__(self, user_info):
        self._info = user_info

    @property
    def id(self):
        return self._info['id']

    @property
    def name(self):
        return self._info['name']


class SlackBotUser(SlackUser):
    @property
    def emoji(self):
        raise NotImplementedError("Implement in derived class")

    def slap(self, trout):
        raise NotImplementedError("Implement in derived class")

class SlackConnection(WebSocketClient):
    def __init__(self, slack_info):
        super(SlackConnection, self).__init__(slack_info['url'])
        self._callbacks = {}
        self._slack_info = slack_info

    @property
    def channels(self):
        return list(SlackChannel(i) for i in self._slack_info['channels'])

    @property
    def users(self):
        return list(SlackUser(i) for i in self._slack_info['users'])

    @property
    def channels_by_id(self):
        return dict((c.id, c) for c in self.channels)

    @property
    def users_by_id(self):
        return dict((u.id, u) for u in self.users)

    def get_user_by_id(self, user_id):
        return self.users_by_id[user_id]

    def get_channel_by_id(self, channel_id):
        return self.channels_by_id[channel_id]

    def opened(self):
        pass

    def closed(self, code, reason=None):
        pass

    def received_message(self, message):
        j = json.loads(str(message))
        msg = slackapi.messages.SlackMessage.get_message(self, j)
        if msg:
            f = self._callbacks.get(msg.type())
            if f:
                f(msg)

    def add_callback(self, message_type, f):
        self._callbacks[message_type] = f


def start_realtime():
    url = urllib.parse.urljoin(API_BASE, "rtm.start")
    res = requests.get(url, {'token': _slack_token()}).json()

    return SlackConnection(res)


def post_message(conference, message, user):
    url = urllib.parse.urljoin(API_BASE, "chat.postMessage")
    parms = {'token': _slack_token(),
             'channel': conference.id,
             'text': message,
             'username': user.name,
             'as_user': False,
             'icon_emoji': user.emoji}
    res = requests.post(url, parms)
    return res.status_code == 200
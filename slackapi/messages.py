__author__ = 'reverendken'


import logging


class SlackMessage(object):
    def __init__(self, api, message):
        self._message = message
        self._api = api

    @classmethod
    def is_this_type(cls, message):
        return message['type'] == cls.MESSAGE_TYPE

    @classmethod
    def get_message(cls, api, message):
        for t in cls.MESSAGE_TYPES:
            if t.is_this_type(message):
                logging.debug('Creating %s from: %s', t.__name__, message)
                return t(api, message)

    @classmethod
    def type(cls):
        return cls.MESSAGE_TYPE


class HelloMessage(SlackMessage):
    MESSAGE_TYPE = 'hello'

    def __init__(self, *args, **kwargs):
        logging.info("Hello to you, too!")
        super(HelloMessage, self).__init__(*args, **kwargs)


class MessageReceivedMessage(SlackMessage):
    MESSAGE_TYPE = 'message'

    @classmethod
    def is_this_type(cls, message):
        return message['type'] == cls.MESSAGE_TYPE and not any(i in message for i in ('deleted_ts', 'subtype'))

    @property
    def message(self):
        return self._message['text']

    @property
    def user(self):
        return self._api.get_user_by_id(self._message['user'])

    @property
    def channel(self):
        return self._api.get_channel_by_id(self._message['channel'])

SlackMessage.MESSAGE_TYPES = (HelloMessage, MessageReceivedMessage)
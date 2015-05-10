__author__ = 'reverendken'

import logging
import re

import slackapi
from botusers import BOB


SLAP_RX = re.compile(r"slaps ([A-Za-z0-9\.]+) with a ([A-Za-z0-9\.\s]+)$")

SLACK_BOTS = {}

def message_received(msg):
    logging.debug("Message from %s: %s" % (msg.user.name, msg.message))
    slap_info = SLAP_RX.search(msg.message)
    if slap_info:
        whom, what = slap_info.groups()
        bot_user = SLACK_BOTS.get(whom)
        if bot_user:
            logging.info("Slapping %s from %s", msg.user.name, bot_user.name)
            bot_user.slap(msg.channel, msg.user, what)


def create_bots(api):
    SLACK_BOTS['B.O.B.'] = BOB(api, 'B.O.B.', ':computer:', 'bobslap.json')

def main():
    ws = slackapi.start_realtime()

    create_bots(ws)

    ws.add_callback('message', message_received)
    ws.connect()
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
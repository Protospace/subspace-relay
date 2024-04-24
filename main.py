import os, logging
DEBUG = os.environ.get('DEBUG')
logging.basicConfig(
        format='[%(asctime)s] %(levelname)s %(module)s/%(funcName)s - %(message)s',
        level=logging.DEBUG if DEBUG else logging.INFO)

import time

import meshtastic
import meshtastic.serial_interface

import uptime_kuma_api

import secrets

mesh = None
kuma = None

def init():
    global mesh, kuma

    mesh = meshtastic.serial_interface.SerialInterface()

    kuma = uptime_kuma_api.UptimeKumaApi(secrets.UPTIME_KUMA_URL)
    kuma.login(secrets.UPTIME_KUMA_USER, secrets.UPTIME_KUMA_PASS)

def send_to_tanner(msg):
    mesh.sendText(msg, secrets.TANNER_NODE_ID)

def check_monitors():
    all_monitors = kuma.get_monitors()

    logging.info('Checking %s monitors...', len(all_monitors))

    down_monitors = []

    for monitor in all_monitors:
        beats = kuma.get_monitor_beats(monitor['id'], 1)

        last_five_beats = beats[-5:]

        statuses = [int(beat['status']) for beat in last_five_beats]

        logging.info('Monitor %s, ID: %s, beats: %s', monitor['name'], monitor['id'], statuses)

        if all(x == 0 for x in statuses):
            logging.info('Monitor is down!')
            down_monitors.append(monitor['id'])

    uptime_msg = 'SUBSPACE:' + str(down_monitors).replace(' ','')
    logging.info('Sending message: %s', uptime_msg)
    send_to_tanner(uptime_msg)


if __name__ == '__main__':
    init()

    try:
        while True:
            check_monitors()

            logging.info('Sleeping...')
            time.sleep(300)
    finally:
        mesh.close()


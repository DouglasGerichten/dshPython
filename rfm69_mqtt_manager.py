#!/usr/bin/env python

"""
This is a simple mqtt client that manages the rfm69 network.
It does things like poll the sensors at a specified interval
and check when a device goes down.
"""

import paho.mqtt.client as mqtt
import time
import signal, sys


from config_file import get_conf

# conf file file default path
conf_file_path = 'dshPython.conf'

# callback functions

def on_connect(client, userdata, flags, rc):
    print('connected with result: ' + str(rc))

    # resubscribe whenever connecting or reconnecting
    client.subscribe("RFM69/+/log")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# helper functions

def scan(client, network_id):
    topic = 'RFM69/' + str(network_id) + '/requests'
    client.publish(topic, 'SCAN', 1)

def sweep(client, network_id):
    topic = 'RFM69/' + str(network_id) + '/requests'
    client.publish(topic, 'SWEEP', 1)


# signal handler for ctrl-c

def signal_handler(signal, frame):
    print("Ending Program.....")
    sys.exit(0)

def main():

    signal.signal(signal.SIGINT, signal_handler)

    # get consts from the config file
    conf_file = open(conf_file_path, 'r') # TODO check for errors opening file and ask the user for the location
    config = get_conf(conf_file)

    #reads config file and returns relevant variables
    #TODO default values in case these are ommited from the config
    server_ip = config['server ip']
    server_port = config['server port']
    client_id = config['client id']
    keep_alive = config['keep alive'] # max number of seconds without sending a message to the broker

    sweep_interval_s = config['interval']

    client = mqtt.Client(client_id)
    
    # set the callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # start the connection
    client.connect(server_ip, server_port, keep_alive)

    # start the thread for processing incoming data
    client.loop_start()

    # main loop
    while True:
        scan(client, 0)
        sweep(client, 0)
        time.sleep(sweep_interval_s)
    # stop the thread
    client.loop_stop()

if __name__ == '__main__':
    main()

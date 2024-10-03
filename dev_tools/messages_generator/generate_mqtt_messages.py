#!/usr/bin/env python3

import random
import sched
import time

from paho.mqtt import client as mqtt_client

"""
openwrt/AP3000-Caldera/cpu-0/percent-system: 1727934089.686:0.133645172068159
openwrt/AP3000-Caldera/cpu-1/percent-idle: 1727934089.687:99.8325519089082
openwrt/AP3000-Caldera/cpu-1/percent-steal: 1727934089.687:0
openwrt/AP3000-Caldera/cpu-1/percent-softirq: 1727934089.686:0.0669792364367046
openwrt/AP3000-Caldera/cpu-1/percent-interrupt: 1727934089.686:0.0334896182183523
openwrt/AP3000-Caldera/cpu-1/percent-nice: 1727934089.686:0
openwrt/AP3000-Caldera/cpu-1/percent-wait: 1727934089.686:0
openwrt/AP3000-Caldera/cpu-1/percent-system: 1727934089.686:0.0669792364367046
openwrt/AP3000-Caldera/cpu-1/percent-user: 1727934089.686:0
openwrt/AP3000-Caldera/cpu-0/percent-idle: 1727934089.686:99.6992983628466
openwrt/AP3000-Caldera/cpu-0/percent-steal: 1727934089.686:0
openwrt/AP3000-Caldera/cpu-0/percent-softirq: 1727934089.686:0.133645172068159
openwrt/AP3000-Caldera/cpu-0/percent-interrupt: 1727934089.686:0.0334112930170398
openwrt/AP3000-Caldera/cpu-0/percent-nice: 1727934089.686:0
openwrt/AP3000-Caldera/cpu-0/percent-wait: 1727934089.686:0
openwrt/AP3000-Caldera/cpu-0/percent-user: 1727934089.686:0
"""

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASS = ""
MQTT_CLIENT_ID = f'messages-generator-{random.randint(0, 1000)}'
MQTT_TOPIC = "openwrt/Testing-Router"
MQTT_FIRST_RECONNECT_DELAY = 1
MQTT_RECONNECT_RATE = 2
MQTT_MAX_RECONNECT_COUNT = 12
MQTT_MAX_RECONNECT_DELAY = 60

OPENWRT_SIMULATED_PROCESSORS = 2

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")

    def on_disconnect(client, userdata, flags, rc, properties):
        print(f"Disconnected with result code: {rc}")
        reconnect_count, reconnect_delay = 0, MQTT_FIRST_RECONNECT_DELAY
        while reconnect_count < MQTT_MAX_RECONNECT_COUNT:
            print(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                print("Reconnected successfully!")
                return
            except Exception as err:
                print(f"{err}. Reconnect failed. Retrying...")

            reconnect_delay *= MQTT_RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MQTT_MAX_RECONNECT_DELAY)
            reconnect_count += 1
        print(f"Reconnect failed after {reconnect_count} attempts. Exiting...")
    
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id=MQTT_CLIENT_ID, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    if MQTT_USER != "" and MQTT_PASS != "":
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_HOST, MQTT_PORT)
    return client

def publish_processor(client, scheduler):
    """This function send some openwrt example data to the MQTT topic"""
    values = [
        "percent-system",
        "percent-idle",
        "percent-steal",
        "percent-softirq",
        "percent-interrupt",
        "percent-nice",
        "percent-wait",
        "percent-user"
    ]
    for i in range(OPENWRT_SIMULATED_PROCESSORS):
        publish_topic_prefix = f"{MQTT_TOPIC}/cpu-{i}/"
        for value in values:
            epoch = time.time()
            percent = random.uniform(0.0, 100.0)
            publish_topic = publish_topic_prefix + value

            result = client.publish(publish_topic, f"{epoch}:{percent}")
            if result[0] == 0:
                print(f"Sent `{epoch}:{percent}` to topic `{publish_topic}`")
            else:
                print(f"Failed to send `{epoch}:{percent}` to topic `{publish_topic}`")

    scheduler.enter(30, 1, publish_processor, (client, scheduler))

def run():
    client = connect_mqtt()
    client.loop_start()

    my_scheduler = sched.scheduler(time.time, time.sleep)
    my_scheduler.enter(5, 1, publish_processor, (client, my_scheduler))
    my_scheduler.run()

    client.loop_stop()


if __name__ == '__main__':
    run()
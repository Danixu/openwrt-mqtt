#!/usr/bin/env python3

import random
import sched
import time

from paho.mqtt import client as mqtt_client

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASS = ""
MQTT_CLIENT_ID = f'messages-generator-{random.randint(0, 1000)}'
MQTT_TOPIC = "openwrt"
MQTT_FIRST_RECONNECT_DELAY = 1
MQTT_RECONNECT_RATE = 2
MQTT_MAX_RECONNECT_COUNT = 12
MQTT_MAX_RECONNECT_DELAY = 60

OPENWRT_ROUTERS_NAME = [
    "OpenWRT-Garage",
    "OpenWRT-Outside"
]
OPENWRT_CONFS = {
    "max_conntrack": 15360,
    "simulated_cpu": 2
}
MESSAGES_DELAY = 30

MESSAGES_GROUPS = {
    "conntrack": True,
    "contextswitch": True,
    "dhcpleases": False,
    "interfaces": False,
    "ipstatistics": False,
    "memory": False,
    "processes": False,
    "processor": True,
    "sensors": False,
    "systemload": False,
    "tcpconnections": False,
    "thermal": False,
    "uptime": False,
    "wireless": False
}

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

def publish_conntrack(client, topic, scheduler):
    publish_topic_prefix = f"{topic}/conntrack"
    epoch = time.time()
    current_conntracks = random.randint(0, OPENWRT_CONFS["max_conntrack"]+1)
    
    # Sent the three messages
    result = client.publish(f"{publish_topic_prefix}/conntrack", f"{epoch}:{current_conntracks}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{current_conntracks}` to topic `{publish_topic_prefix}/conntrack`")
    else:
        print(f"Failed to send `{epoch}:{current_conntracks}` to topic `{publish_topic_prefix}/conntrack`")

    result = client.publish(f"{publish_topic_prefix}/conntrack-max", f"{epoch}:{OPENWRT_CONFS["max_conntrack"]}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{OPENWRT_CONFS["max_conntrack"]}` to topic `{publish_topic_prefix}/conntrack-max`")
    else:
        print(f"Failed to send `{epoch}:{OPENWRT_CONFS["max_conntrack"]}` to topic `{publish_topic_prefix}/conntrack-max`")

    percent = round(current_conntracks / OPENWRT_CONFS["max_conntrack"] * 100, 16)
    result = client.publish(f"{publish_topic_prefix}/percent-used", f"{epoch}:{percent}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{percent}` to topic `{publish_topic_prefix}/percent-used`")
    else:
        print(f"Failed to send `{epoch}:{percent}` to topic `{publish_topic_prefix}/percent-used`")

    scheduler.enter(MESSAGES_DELAY, 1, publish_conntrack, (client, topic, scheduler))

def publish_contextswitch(client, topic, scheduler):
    publish_topic_prefix = f"{topic}/contextswitch"
    epoch = time.time()
    current_contextswitch = random.uniform(0.0, 10000.0)
    
    # Sent the three messages
    result = client.publish(f"{publish_topic_prefix}/contextswitch", f"{epoch}:{current_contextswitch}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{current_contextswitch}` to topic `{publish_topic_prefix}/contextswitch`")
    else:
        print(f"Failed to send `{epoch}:{current_contextswitch}` to topic `{publish_topic_prefix}/contextswitch`")

    scheduler.enter(MESSAGES_DELAY, 1, publish_contextswitch, (client, topic, scheduler))

def publish_processor(client, topic, scheduler):
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
    for i in range(OPENWRT_CONFS["simulated_cpu"]):
        publish_topic_prefix = f"{topic}/cpu-{i}/"
        for value in values:
            epoch = time.time()
            percent = random.uniform(0.0, 100.0)
            publish_topic = publish_topic_prefix + value

            result = client.publish(publish_topic, f"{epoch}:{percent}")
            if result[0] == 0:
                print(f"Sent `{epoch}:{percent}` to topic `{publish_topic}`")
            else:
                print(f"Failed to send `{epoch}:{percent}` to topic `{publish_topic}`")

    scheduler.enter(MESSAGES_DELAY, 1, publish_processor, (client, topic, scheduler))

def run():
    client = connect_mqtt()
    client.loop_start()

    my_scheduler = sched.scheduler(time.time, time.sleep)
    for router in OPENWRT_ROUTERS_NAME:
        if MESSAGES_GROUPS["conntrack"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_conntrack, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
        if MESSAGES_GROUPS["contextswitch"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_contextswitch, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
        if MESSAGES_GROUPS["processor"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_processor, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
            


    my_scheduler.run()

    client.loop_stop()


if __name__ == '__main__':
    run()
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
    "max_bandwidth": int(1 * 1024 * 1024 * 1024 / 8), # 1 Gbit converted to octets
    "simulated_cpu": 2
}
MESSAGES_DELAY = 30

MESSAGES_GROUPS = {
    "conntrack": False,
    "contextswitch": False,
    "dhcpleases": False,
    "interfaces": False,
    "ipstatistics": True,
    "memory": False,
    "processes": False,
    "processor": False,
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


def publish_dhcpleases(client, topic, scheduler):
    publish_topic_prefix = f"{topic}/dhcpleases"
    epoch = time.time()
    current_dhcpleases = random.randint(0, 500)
    
    # Sent the message
    result = client.publish(f"{publish_topic_prefix}/count", f"{epoch}:{current_dhcpleases}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{current_dhcpleases}` to topic `{publish_topic_prefix}/count`")
    else:
        print(f"Failed to send `{epoch}:{current_dhcpleases}` to topic `{publish_topic_prefix}/count`")

    scheduler.enter(MESSAGES_DELAY, 1, publish_dhcpleases, (client, topic, scheduler))


def publish_interfaces(client, topic, scheduler):
    publish_topic_prefix = f"{topic}/interface-wlan0"
    epoch = time.time()
    
    # Sent the four messages
    first_value = random.randint(0, 500)
    second_value = random.randint(0, 500)
    result = client.publish(f"{publish_topic_prefix}/if_dropped", f"{epoch}:{first_value}:{second_value}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_dropped`")
    else:
        print(f"Failed to send `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_dropped`")
    
    # Sent the four messages
    first_value = random.randint(0, 500)
    second_value = random.randint(0, 500)
    result = client.publish(f"{publish_topic_prefix}/if_errors", f"{epoch}:{first_value}:{second_value}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_errors`")
    else:
        print(f"Failed to send `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_errors`")

    # Sent the four messages
    first_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    second_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    result = client.publish(f"{publish_topic_prefix}/if_octets", f"{epoch}:{first_value}:{second_value}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_octets`")
    else:
        print(f"Failed to send `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_octets`")

    # Sent the four messages
    first_value = random.uniform(0.0, 500.0)
    second_value = random.uniform(0.0, 500.0)
    result = client.publish(f"{publish_topic_prefix}/if_packets", f"{epoch}:{first_value}:{second_value}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_packets`")
    else:
        print(f"Failed to send `{epoch}:{first_value}:{second_value}` to topic `{publish_topic_prefix}/if_packets`")

    scheduler.enter(MESSAGES_DELAY, 1, publish_interfaces, (client, topic, scheduler))


def publish_ipstatistics(client, topic, scheduler):
    publish_topic_prefix = f"{topic}/ipstatistics-all"
    epoch = time.time()
    
    # Sent the four messages
    first_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    second_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    third_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    fourth_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    result = client.publish(f"{publish_topic_prefix}/ip_stats_octets", f"{epoch}:{first_value}:{second_value}:{third_value}:{fourth_value}")
    if result[0] == 0:
        print(f"Sent `{epoch}:{first_value}:{second_value}:{third_value}:{fourth_value}` to topic `{publish_topic_prefix}/ip_stats_octets`")
    else:
        print(f"Failed to send `{epoch}:{first_value}:{second_value}:{third_value}:{fourth_value}` to topic `{publish_topic_prefix}/ip_stats_octets`")
    
    scheduler.enter(MESSAGES_DELAY, 1, publish_ipstatistics, (client, topic, scheduler))


def publish_memory(client, topic, scheduler):
    """
    Publish the router memory messages to the MQTT topic.
    
    I Know, the numbers doesn't matches a real system, but is just for testing ;)
    """
    publish_topic_prefix = f"{topic}/memory"
    epoch = time.time()
    numeric = [
        "memory-buffered",
        "memory-cached",
        "memory-free",
        "memory-slab_recl",
        "memory-slab_unrecl",
        "memory-used"
    ]
    percentage = [
        "percent-buffered",
        "percent-cached",
        "percent-free",
        "percent-slab_recl",
        "percent-slab_unrecl",
        "percent-used"
    ]
    
    for item in numeric:
        current = random.randint(0, 1048576)
    
        # Sent the three messages
        result = client.publish(f"{publish_topic_prefix}/{item}", f"{epoch}:{current}")
        if result[0] == 0:
            print(f"Sent `{epoch}:{current}` to topic `{publish_topic_prefix}/{item}`")
        else:
            print(f"Failed to send `{epoch}:{current}` to topic `{publish_topic_prefix}/{item}`")

    for item in percentage:
        current = random.uniform(0.0, 100.0)
    
        # Sent the three messages
        result = client.publish(f"{publish_topic_prefix}/{item}", f"{epoch}:{current}")
        if result[0] == 0:
            print(f"Sent `{epoch}:{current}` to topic `{publish_topic_prefix}/{item}`")
        else:
            print(f"Failed to send `{epoch}:{current}` to topic `{publish_topic_prefix}/{item}`")

    scheduler.enter(MESSAGES_DELAY, 1, publish_memory, (client, topic, scheduler))




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
        if MESSAGES_GROUPS["dhcpleases"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_dhcpleases, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
        if MESSAGES_GROUPS["interfaces"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_interfaces, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
        if MESSAGES_GROUPS["memory"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_memory, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
        if MESSAGES_GROUPS["ipstatistics"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_ipstatistics, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
        if MESSAGES_GROUPS["processor"]:
            my_scheduler.enter(random.randint(1, MESSAGES_DELAY+1), 1, publish_processor, (client, f"{MQTT_TOPIC}/{router}", my_scheduler))
            


    my_scheduler.run()

    client.loop_stop()


if __name__ == '__main__':
    run()
"""
Script made for sending test messages to the MQTT server, allowing to simulate a OpenWRT device
"""

#!/usr/bin/env python3

import datetime
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
OPENWRT_ROUTERS_WLANS = [
    "wlan0",
    "wlan1"
]
OPENWRT_CONFS = {
    "max_conntrack": 15360,
    "max_bandwidth": int(1 * 1024 * 1024 * 1024 / 8), # 1 Gbit converted to octets
    "simulated_cpu": 2
}
MESSAGES_DELAY = 30

MESSAGES_GROUPS = {
    "conntrack": True,
    "contextswitch": True,
    "dhcpleases": True,
    "interfaces": True,
    "ipstatistics": True,
    "memory": True,
    "processor": True,
    "systemload": True,
    "thermal": True,
    "uptime": True,
    "wireless": True
}

start_time = datetime.datetime.now()

def connect_mqtt():
    """
    Function to connect to the MQTT server
    """
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
    client = mqtt_client.Client(
        client_id=MQTT_CLIENT_ID,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2
    )

    if MQTT_USER != "" and MQTT_PASS != "":
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_HOST, MQTT_PORT)
    return client

def send_message(client, topic, msg):
    """
    This function will send the message to the topic
    """
    result = client.publish(topic, msg)
    if result[0] == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send `{msg}` to topic `{topic}`")


def publish_conntrack(client, topic, scheduler):
    """
    Test data for the collectd-mod-conntrack module
    """
    publish_topic_prefix = f"{topic}/conntrack"
    epoch = time.time()
    current_conntracks = random.randint(0, OPENWRT_CONFS["max_conntrack"]+1)

    # Sent the three messages
    send_message(client, f"{publish_topic_prefix}/conntrack", f"{epoch}:{current_conntracks}\x00")
    send_message(client,
                 f"{publish_topic_prefix}/conntrack-max",
                 f"{epoch}:{OPENWRT_CONFS["max_conntrack"]}\x00")

    percent = round(current_conntracks / OPENWRT_CONFS["max_conntrack"] * 100, 16)
    send_message(client, f"{publish_topic_prefix}/percent-used", f"{epoch}:{percent}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_conntrack, (client, topic, scheduler))


def publish_contextswitch(client, topic, scheduler):
    """
    Test data for the collectd-mod-contextswitch module
    """
    publish_topic_prefix = f"{topic}/contextswitch"
    epoch = time.time()
    current_contextswitch = random.uniform(0.0, 10000.0)

    # Sent the three messages
    send_message(client,
                 f"{publish_topic_prefix}/contextswitch",
                 f"{epoch}:{current_contextswitch}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_contextswitch, (client, topic, scheduler))


def publish_dhcpleases(client, topic, scheduler):
    """
    Test data for the collectd-mod-dhcpleases module
    """
    publish_topic_prefix = f"{topic}/dhcpleases"
    epoch = time.time()
    current_dhcpleases = random.randint(0, 500)

    # Sent the message
    send_message(client, f"{publish_topic_prefix}/count", f"{epoch}:{current_dhcpleases}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_dhcpleases, (client, topic, scheduler))


def publish_interfaces(client, topic, scheduler):
    """
    Test data for the collectd-mod-interface module
    """
    publish_topic_prefix = f"{topic}/interface-wlan0"
    epoch = time.time()

    # Sent the four messages
    first_value = random.randint(0, 500)
    second_value = random.randint(0, 500)
    send_message(client,
                 f"{publish_topic_prefix}/if_dropped",
                 f"{epoch}:{first_value}:{second_value}\x00")

    # Sent the four messages
    first_value = random.randint(0, 500)
    second_value = random.randint(0, 500)
    send_message(client,
                 f"{publish_topic_prefix}/if_errors",
                 f"{epoch}:{first_value}:{second_value}\x00")

    # Sent the four messages
    first_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    second_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    send_message(client,
                 f"{publish_topic_prefix}/if_octets",
                 f"{epoch}:{first_value}:{second_value}\x00")

    # Sent the four messages
    first_value = random.uniform(0.0, 500.0)
    second_value = random.uniform(0.0, 500.0)
    send_message(client,
                 f"{publish_topic_prefix}/if_packets",
                 f"{epoch}:{first_value}:{second_value}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_interfaces, (client, topic, scheduler))


def publish_ipstatistics(client, topic, scheduler):
    """
    Test data for the collectd-mod-ipstatistics module
    """
    publish_topic_prefix = f"{topic}/ipstatistics-all"
    epoch = time.time()

    # Sent the four messages
    first_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    second_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    third_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    fourth_value = random.randint(0, OPENWRT_CONFS["max_bandwidth"])
    send_message(client,
                 f"{publish_topic_prefix}/ip_stats_octets",
                 f"{epoch}:{first_value}:{second_value}:{third_value}:{fourth_value}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_ipstatistics, (client, topic, scheduler))


def publish_memory(client, topic, scheduler):
    """
    Test data for the collectd-mod-memory module
    
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
        current = random.randint(0, 134217728)

        # Sent the three messages
        send_message(client, f"{publish_topic_prefix}/{item}", f"{epoch}:{current}\x00")

    for item in percentage:
        current = random.uniform(0.0, 100.0)

        # Sent the three messages
        send_message(client, f"{publish_topic_prefix}/{item}", f"{epoch}:{current}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_memory, (client, topic, scheduler))



def publish_processor(client, topic, scheduler):
    """
    Test data for the collectd-mod-cpu module
    """
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

            send_message(client, publish_topic, f"{epoch}:{percent}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_processor, (client, topic, scheduler))



def publish_systemload(client, topic, scheduler):
    """
    Test data for the collectd-mod-load module
    """
    publish_topic_prefix = f"{topic}/load"
    epoch = time.time()

    # Sent the four messages
    first_value = random.uniform(0, OPENWRT_CONFS["simulated_cpu"] * 2)
    second_value = random.uniform(0, OPENWRT_CONFS["simulated_cpu"] * 2)
    third_value = random.uniform(0, OPENWRT_CONFS["simulated_cpu"] * 2)
    send_message(client,
                 f"{publish_topic_prefix}/load",
                 f"{epoch}:{first_value}:{second_value}:{third_value}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_systemload, (client, topic, scheduler))


def publish_thermal(client, topic, scheduler):
    """
    Test data for the collectd-mod-thermal module
    """
    publish_topic_prefix = f"{topic}/thermal"
    epoch = time.time()

    # Send the temperature measurement
    temperature = random.uniform(0, 90)
    send_message(client,
                 f"{publish_topic_prefix}-thermal_zone0/temperature",
                 f"{epoch}:{temperature}\x00")

    # Send the cooling device state
    cooling_state = random.randint(0, 3)
    send_message(client,
                 f"{publish_topic_prefix}-cooling_device0/gauge",
                 f"{epoch}:{cooling_state}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_thermal, (client, topic, scheduler))


def publish_uptime(client, topic, scheduler):
    """
    Test data for the collectd-mod-uptime module
    """
    publish_topic_prefix = f"{topic}/uptime"
    epoch = time.time()

    # Send the temperature measurement
    elapsed = datetime.datetime.now() - start_time
    send_message(client, f"{publish_topic_prefix}/uptime", f"{epoch}:{elapsed.seconds}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_uptime, (client, topic, scheduler))


def publish_wireless(client, topic, scheduler):
    """
    Test data for the collectd-mod-iwinfo module
    """
    publish_topic_prefix = f"{topic}/iwinfo"
    epoch = time.time()

    for wl_device in OPENWRT_ROUTERS_WLANS:
        # Send the stations
        stations = random.randint(0, 100)
        final_topic = f"{publish_topic_prefix}-{wl_device}/stations"
        send_message(client, final_topic, f"{epoch}:{stations}\x00")

        # Send the Signal Quality
        signal_quality = -(random.randint(30, 100))
        final_topic = f"{publish_topic_prefix}-{wl_device}/signal_quality"
        send_message(client, final_topic, f"{epoch}:{signal_quality}\x00")

        # Send the Signal Noise
        signal_noise = -(random.randint(30, 100))
        final_topic = f"{publish_topic_prefix}-{wl_device}/signal_noise"
        send_message(client, final_topic, f"{epoch}:{signal_noise}\x00")

        # Send the Signal Power
        signal_power = -(random.randint(30, 100))
        final_topic = f"{publish_topic_prefix}-{wl_device}/signal_power"
        send_message(client, final_topic, f"{epoch}:{signal_power}\x00")

        # Send the bitrate
        bitrate = random.randint(52000000, 1000000000)
        final_topic = f"{publish_topic_prefix}-{wl_device}/bitrate"
        send_message(client, final_topic, f"{epoch}:{bitrate}\x00")

    scheduler.enter(MESSAGES_DELAY, 1, publish_wireless, (client, topic, scheduler))


def send_router_messages(client, scheduler, router):
    if MESSAGES_GROUPS["conntrack"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_conntrack,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["contextswitch"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_contextswitch,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["dhcpleases"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_dhcpleases,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["interfaces"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_interfaces,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["ipstatistics"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_ipstatistics,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["memory"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_memory,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["processor"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_processor,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["systemload"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_systemload,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["thermal"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_thermal,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["uptime"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_uptime,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))
    if MESSAGES_GROUPS["wireless"]:
        scheduler.enter(
            random.randint(1, MESSAGES_DELAY+1),
            1,
            publish_wireless,
            (client, f"{MQTT_TOPIC}/{router}", scheduler))

def run():
    """
    Main function executed when the script runs
    """
    client = connect_mqtt()
    client.loop_start()

    scheduler = sched.scheduler(time.time, time.sleep)
    for router in OPENWRT_ROUTERS_NAME:
        send_router_messages(client, scheduler, router)

    scheduler.run()

    client.loop_stop()


if __name__ == '__main__':
    run()

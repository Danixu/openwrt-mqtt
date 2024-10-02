"""Global module data"""
DOMAIN = 'openwrt_mqtt'
ALLOWED_SENSORS = {
    "processor": {
        "percent-idle": {
            "name": "Processor {!s}: Idle (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-interrupt": {
            "name": "Processor {!s}: Interrupt (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-nice": {
            "name": "Processor {!s}: Nice (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-softirq": {
            "name": "Processor {!s}: SoftIRQ (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-steal": {
            "name": "Processor {!s}: Steal (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-system": {
            "name": "Processor {!s}: System (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-user": {
            "name": "Processor {!s}: User (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        },
        "percent-wait": {
            "name": "Processor {!s}: Wait (%)",
            "sensor_type": "percent",
            "icon": "mdi:chip"
        }
    }
}
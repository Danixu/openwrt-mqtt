"""Global module data"""
DOMAIN = 'openwrt_mqtt'
ALLOWED_SENSORS = {
    "processor": {
        "percent-idle": {
            "name": "Processor {!s}: Idle",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "diagnostic": True
        },
        "percent-interrupt": {
            "name": "Processor {!s}: Interrupt",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "diagnostic": True
        },
        "percent-nice": {
            "name": "Processor {!s}: Nice",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "diagnostic": True
        },
        "percent-softirq": {
            "name": "Processor {!s}: SoftIRQ",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "diagnostic": True
        },
        "percent-steal": {
            "name": "Processor {!s}: Steal",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "diagnostic": True
        },
        "percent-system": {
            "name": "Processor {!s}: System",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "enabled_default": True
        },
        "percent-user": {
            "name": "Processor {!s}: User",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "enabled_default": True
        },
        "percent-wait": {
            "name": "Processor {!s}: Wait",
            "sensor_type": "percent",
            "icon": "mdi:chip",
            "diagnostic": True
        }
    }
}
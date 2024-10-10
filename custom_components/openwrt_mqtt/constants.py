"""Global module data"""
DOMAIN = 'openwrt_mqtt'
ICONS = {
    "processor": "mdi:chip",
    "conntrack": "mdi:lan-connect",
    "contextswitch": "mdi:swap-horizontal"
}
ALLOWED_SENSORS = {
    "conntrack": {
        "conntrack": {
            "name": "Conntrack: Used",
            "sensor_type": "numeric",
            "icon": ICONS["conntrack"],
            "diagnostic": True
        },
        "conntrack-max": {
            "name": "Conntrack: Max",
            "sensor_type": "numeric",
            "icon": ICONS["conntrack"],
            "diagnostic": True
        },
        "percent-used": {
            "name": "Conntrack: Used (%)",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["conntrack"],
            "enabled_default": True
        }
    },
    "contextswitch": {
        "contextswitch": {
            "name": "Context Switch",
            "sensor_type": "float",
            "icon": ICONS["contextswitch"],
            "enabled_default": True
        }
    },
    "processor": {
        "percent-idle": {
            "name": "Processor {!s}: Idle",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "diagnostic": True
        },
        "percent-interrupt": {
            "name": "Processor {!s}: Interrupt",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "diagnostic": True
        },
        "percent-nice": {
            "name": "Processor {!s}: Nice",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "diagnostic": True
        },
        "percent-softirq": {
            "name": "Processor {!s}: SoftIRQ",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "diagnostic": True
        },
        "percent-steal": {
            "name": "Processor {!s}: Steal",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "diagnostic": True
        },
        "percent-system": {
            "name": "Processor {!s}: System",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "enabled_default": True
        },
        "percent-user": {
            "name": "Processor {!s}: User",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "enabled_default": True
        },
        "percent-wait": {
            "name": "Processor {!s}: Wait",
            "sensor_type": "float",
            "unit": "%",
            "icon": ICONS["processor"],
            "diagnostic": True
        }
    }
}
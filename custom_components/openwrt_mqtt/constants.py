"""Global module data"""
DOMAIN = 'openwrt_mqtt'
ICONS = {
    "processor": "mdi:chip",
    "memory": "mdi:memory",
    "conntrack": "mdi:lan-connect",
    "contextswitch": "mdi:swap-horizontal"
}
ALLOWED_SENSORS = {
    "conntrack": {
        "conntrack": {
            "sensor_type": "numeric",
            "icon": ICONS["conntrack"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Conntrack: Used"
                }
            ]
        },
        "conntrack-max": {
            "sensor_type": "numeric",
            "icon": ICONS["conntrack"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Conntrack: Max"
                }
            ]
        },
        "percent-used": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["conntrack"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Conntrack: Used (%)"
                }
            ]
        }
    },
    "contextswitch": {
        "contextswitch": {
            "sensor_type": "float",
            "icon": ICONS["contextswitch"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Context Switch"
                }
            ]
        }
    },
    "dhcpleases": {
        "count": {
            "sensor_type": "numeric",
            "icon": "mdi:router",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "DHCP Leases"
                }
            ]
        }
    },
    "memory": {
        "memory-buffered": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Buffered"
                }
            ]
        },
        "memory-cached": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Cached"
                }
            ]
        },
        "memory-free": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Free"
                }
            ]
        },
        "memory-slab_recl": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Slab Reclaimable"
                }
            ]
        },
        "memory-slab_unrecl": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Slab Unreclaimable"
                }
            ]
        },
        "memory-used": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Used"
                }
            ]
        },
        "percent-buffered": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["memory"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Memory: Percent Buffered"
                }
            ]
        },
        "percent-cached": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["memory"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Memory: Percent Cached"
                }
            ]
        },
        "percent-free": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["memory"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Memory: Percent Free"
                }
            ]
        },
        "percent-slab_recl": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Percent Slab Reclaimable"
                }
            ]
        },
        "percent-slab_unrecl": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["memory"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Memory: Pecent Slab Unreclaimable"
                }
            ]
        },
        "percent-used": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["memory"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Memory: Percent Used"
                }
            ]
        },
    },
    "processor": {
        "percent-idle": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: Idle"
                }
            ]
        },
        "percent-interrupt": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: Interrupt"
                }
            ]
        },
        "percent-nice": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: Nice"
                }
            ]
        },
        "percent-softirq": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: SoftIRQ"
                }
            ]
        },
        "percent-steal": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: Steal"
                }
            ]
        },
        "percent-system": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Processor {!s}: System"
                }
            ]
        },
        "percent-user": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Processor {!s}: User"
                }
            ]
        },
        "percent-wait": {
            "sensor_type": "float",
            "unit": "%",
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: Wait"
                }
            ]
        }
    }
}
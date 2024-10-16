from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTemperature,
    UnitOfTime
)

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
            "native_unit_of_measurement": PERCENTAGE,
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
            "precision": 2,
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
    "interface": {
        "if_dropped": {
            "sensor_type": "numeric",
            "icon": "mdi:router",
            "diagnostic": True,
            "unit": "packets",
            "partitions": [
                {
                    "name": "Interface {!s}: Dropped/s (TX)"
                },
                {
                    "name": "Interface {!s}: Dropped/s (RX)"
                }
            ]
        },
        "if_errors": {
            "sensor_type": "numeric",
            "icon": "mdi:router",
            "diagnostics": True,
            "unit": "packets",
            "partitions": [
                {
                    "name": "Interface {!s}: Errors/s (TX)"
                },
                {
                    "name": "Interface {!s}: Errors/s (RX)"
                }
            ]
        },
        "if_octets": {
            "sensor_type": "octets",
            "icon": "mdi:router",
            "enabled_default": True,
            "precision": 2,
            "native_unit_of_measurement": UnitOfDataRate.BITS_PER_SECOND,
            "suggested_unit_of_measurement": UnitOfDataRate.MEGABITS_PER_SECOND,
            "device_class": SensorDeviceClass.DATA_RATE,
            "partitions": [
                {
                    "name": "Interface {!s}: Bandwidth (TX)"
                },
                {
                    "name": "Interface {!s}: Bandwidth (RX)"
                }
            ]
        },
        "if_packets": {
            "sensor_type": "float",
            "icon": "mdi:router",
            "enabled_default": True,
            "unit": "packets",
            "precision": 2,
            "partitions": [
                {
                    "name": "Interface {!s}: Packets/s (TX)"
                },
                {
                    "name": "Interface {!s}: Packets/s (RX)"
                }
            ]
        }
    },
    "ipstatistics-all": {
        "ip_stats_octets": {
            "sensor_type": "octets",
            "enabled_default": True,
            "precision": 2,
            "native_unit_of_measurement": UnitOfDataRate.BITS_PER_SECOND,
            "suggested_unit_of_measurement": UnitOfDataRate.MEGABITS_PER_SECOND,
            "device_class": SensorDeviceClass.DATA_RATE,
            "partitions": [
                {
                    "name": "IP Statistics: IPv4 (RX)",
                    "icon": "mdi:upload-network-outline"
                },
                {
                    "name": "IP Statistics: IPv4 (TX)",
                    "icon": "mdi:download-network-outline"
                },
                {
                    "name": "IP Statistics: IPv6 (RX)",
                    "icon": "mdi:upload-network-outline"
                },
                {
                    "name": "IP Statistics: IPv6 (TX)",
                    "icon": "mdi:download-network-outline"
                }
            ]
        }
    },
    "memory": {
        "memory-buffered": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "native_unit_of_measurement": UnitOfInformation.BYTES,
            "suggested_unit_of_measurement": UnitOfInformation.MEGABYTES,
            "device_class": SensorDeviceClass.DATA_SIZE,
            "enabled_default": False,
            "partitions": [
                {
                    "name": "Memory: Buffered"
                }
            ]
        },
        "memory-cached": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "native_unit_of_measurement": UnitOfInformation.BYTES,
            "suggested_unit_of_measurement": UnitOfInformation.MEGABYTES,
            "device_class": SensorDeviceClass.DATA_SIZE,
            "enabled_default": False,
            "partitions": [
                {
                    "name": "Memory: Cached"
                }
            ]
        },
        "memory-free": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "native_unit_of_measurement": UnitOfInformation.BYTES,
            "suggested_unit_of_measurement": UnitOfInformation.MEGABYTES,
            "device_class": SensorDeviceClass.DATA_SIZE,
            "enabled_default": False,
            "partitions": [
                {
                    "name": "Memory: Free"
                }
            ]
        },
        "memory-slab_recl": {
            "sensor_type": "numeric",
            "icon": ICONS["memory"],
            "native_unit_of_measurement": UnitOfInformation.BYTES,
            "suggested_unit_of_measurement": UnitOfInformation.MEGABYTES,
            "device_class": SensorDeviceClass.DATA_SIZE,
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
            "native_unit_of_measurement": UnitOfInformation.BYTES,
            "suggested_unit_of_measurement": UnitOfInformation.MEGABYTES,
            "device_class": SensorDeviceClass.DATA_SIZE,
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
            "native_unit_of_measurement": UnitOfInformation.BYTES,
            "suggested_unit_of_measurement": UnitOfInformation.MEGABYTES,
            "device_class": SensorDeviceClass.DATA_SIZE,
            "enabled_default": False,
            "partitions": [
                {
                    "name": "Memory: Used"
                }
            ]
        },
        "percent-buffered": {
            "sensor_type": "float",
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
            "precision": 2,
            "icon": ICONS["processor"],
            "enabled_default": False,
            "partitions": [
                {
                    "name": "Processor {!s}: Idle"
                }
            ]
        },
        "percent-interrupt": {
            "sensor_type": "float",
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
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
            "native_unit_of_measurement": PERCENTAGE,
            "precision": 2,
            "icon": ICONS["processor"],
            "diagnostic": True,
            "partitions": [
                {
                    "name": "Processor {!s}: Wait"
                }
            ]
        }
    },
    "load": {
        "load": {
            "sensor_type": "float",
            "precision": 2,
            "icon": ICONS["processor"],
            "enabled_default": True,
            "partitions": [
                {
                    "name": "System Load: 1m"
                },
                {
                    "name": "System Load: 5m"
                },
                {
                    "name": "System Load: 15m"
                }
            ]
        }
    },
    "thermal-thermal": {
        "temperature": {
            "sensor_type": "float",
            "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
            "device_class": SensorDeviceClass.TEMPERATURE,
            "precision": 2,
            "icon": "mdi:thermometer-lines",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Thermal: {!s}"
                }
            ]
        }
    },
    "thermal-cooling": {
        "gauge": {
            "sensor_type": "numeric",
            "icon": "mdi:fan",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Cooling: {!s}"
                }
            ]
        }
    },
    "uptime": {
        "uptime": {
            "sensor_type": "numeric",
            "native_unit_of_measurement": UnitOfTime.SECONDS,
            "device_class": SensorDeviceClass.DURATION,
            "icon": "mdi:timelapse",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Uptime"
                }
            ]
        }
    },
    "wireless": {
        "stations": {
            "sensor_type": "numeric",
            "icon": "mdi:router-wireless",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Wireless {!s}: Stations"
                }
            ]
        },
        "signal_quality": {
            "sensor_type": "numeric",
            "native_unit_of_measurement": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
            "icon": "mdi:router-wireless",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Wireless {!s}: Signal Quality"
                }
            ]
        },
        "signal_noise": {
            "sensor_type": "numeric",
            "native_unit_of_measurement": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
            "icon": "mdi:router-wireless",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Wireless {!s}: Signal Noise"
                }
            ]
        },
        "signal_power": {
            "sensor_type": "numeric",
            "native_unit_of_measurement": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
            "icon": "mdi:router-wireless",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Wireless {!s}: Signal Power"
                }
            ]
        },
        "bitrate": {
            "sensor_type": "numeric",
            "native_unit_of_measurement": UnitOfDataRate.BITS_PER_SECOND,
            "device_class": SensorDeviceClass.DATA_RATE,
            "icon": "mdi:router-wireless",
            "enabled_default": True,
            "partitions": [
                {
                    "name": "Wireless {!s}: Bitrate"
                }
            ]
        }
    }
}

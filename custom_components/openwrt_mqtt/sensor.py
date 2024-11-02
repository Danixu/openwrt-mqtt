import logging
import re

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.mqtt import async_subscribe

from .constants import DOMAIN, ALLOWED_SENSORS

_LOGGER = logging.getLogger(__name__)

def get_device_name(device_type, sensor_data):
    name = sensor_data["name"]

    if device_type == "processor":
        name = name.format(sensor_data["extracted_data"][0].upper())
    elif device_type == "interface":
        interface = re.match("interface-(.+)", sensor_data["extracted_data"][0])
        name = name.format(interface.groups()[0])
    elif device_type in ["thermal-thermal", "thermal-cooling"]:
        device = re.match(
            "thermal-(thermal|cooling)_(.+)",
            sensor_data["extracted_data"][0]
        )
        name = name.format(device.groups()[1].capitalize())
    elif device_type == "wireless":
        interface = re.match("iwinfo-(.+)", sensor_data["extracted_data"][0])
        name = name.format(interface.groups()[0])

    return name

def _determine_entity_device_group(entity_name):
    if re.match("cpu-[\\d]+", entity_name):
        return "processor"
    elif re.match("interface-.+", entity_name):
        return "interface"
    elif re.match("thermal-thermal_.*", entity_name):
        return "thermal-thermal"
    elif re.match("thermal-cooling_.*", entity_name):
        return "thermal-cooling"
    elif re.match("iwinfo-.*", entity_name):
        return "wireless"
    else:
        return entity_name



async def async_setup_entry(hass, entry, async_add_entities):
    # = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async def _received_message(msg):
        """
        Function called when MQTT message arrives.
        This function updates the devices and sensors in the coordinator if requried.
        """
        _LOGGER.info("Received message in %s: %s", msg.topic, msg.payload)
        # Extract the device type and the entity from the topic
        entity_found = re.match(".*\\/(.+)\\/(.+)$", msg.topic)

        if not entity_found:
            _LOGGER.debug("Unable to extract the data from the topic.")
        else:
            _LOGGER.debug(
                "Detected a device %s with an entity %s",
                entity_found.groups()[0],
                entity_found.groups()[1]
            )

            # Get the device group to avoid to create a device by every cpu for example
            device_group = _determine_entity_device_group(entity_found.groups()[0])
            if device_group is None:
                _LOGGER.debug(
                    "The device group for the device %s cannot be determined.",
                    entity_found.groups()[0]
                )
                return

            sensor_config = ALLOWED_SENSORS.get(
                device_group, {}).get(entity_found.groups()[1], None)
            if not sensor_config:
                _LOGGER.debug(
                    "The sensor %s of the device group %s is not allowed.",
                    device_group,
                    entity_found.groups()[1]
                )
                return

            # Check if the group already exists and if not, create it
            if device_group not in hass.data[DOMAIN][entry.entry_id]["devices"]:
                hass.data[DOMAIN][entry.entry_id]["devices"][device_group]= {}

            # Now just update the entity data:
            splitted_values = msg.payload.rstrip('\x00').split(":")
            if len(sensor_config["partitions"]) != (len(splitted_values) - 1):
                _LOGGER.warning(
                    "The sensor %s of the device group %s partitions doesn't matches the template. "
                    "Sensor will not be changed.",
                    device_group,
                    entity_found.groups()[1]
                )
                return

            for idx, partition in enumerate(sensor_config["partitions"]):
                sensor_id = f"{entity_found.groups()[0]}_{entity_found.groups()[1]}_{idx}"
                append = False
                if not sensor_id in hass.data[DOMAIN][entry.entry_id]["devices"][device_group]:
                    append = True
                hass.data[DOMAIN][entry.entry_id]["devices"][device_group][sensor_id] = {
                    "sensor_config": sensor_config,
                    "extracted_data": entity_found.groups(),
                    "sensor_id": sensor_id,
                    "device_group": device_group,
                    "icon": partition.get(
                        "icon",
                        sensor_config.get("icon", "mdi:cancel")
                    ),
                    "timestamp": splitted_values[0],
                    "name": partition["name"],
                    "value": splitted_values[(1 + idx)]
                }

                if append:
                    sensor_data = hass.data[DOMAIN][entry.entry_id]["devices"][device_group][sensor_id]
                    device_name = get_device_name(device_group, sensor_data )
                    _LOGGER.debug(
                        "The sensor doesn't exists yet. Adding the entity for %s",
                        sensor_id
                    )
                    if sensor_config["sensor_type"] == "numeric":
                        entity = NumericEntity(entry, device_name, sensor_data)
                        async_add_entities([entity])
                    elif sensor_config["sensor_type"] == "float":
                        entity = FloatEntity(entry, device_name, sensor_data)
                        async_add_entities([entity])
                    else:
                        _LOGGER.warning("The sensor type %s is not managed by the entities setup. "
                                        "Please, report this to the developer.",
                                        sensor_config["type"])
                        continue

    hass.data[DOMAIN].get(entry.entry_id)["unsubscribe"] = (
        await async_subscribe(hass, f"{entry.data["mqtt_topic"]}/#", _received_message)
    )

class BaseEntity(SensorEntity):
    def __init__(self, entry, device_name, sensor_data):
        self.entry = entry
        self.sensor_data = sensor_data

        sc = sensor_data["sensor_config"]

        # Sensor attributes
        self._attr_name = device_name
        self._attr_icon = sensor_data["icon"]
        self._attr_unique_id = f"{entry.data['id']}_{sensor_data["sensor_id"]}"
        self._attr_suggested_display_precision = sc.get("precision", None)
        self._attr_entity_registry_enabled_default = sc.get("enabled_default", None)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if sc.get("diagnostic", False) else None

        self._attr_native_unit_of_measurement = sc.get("native_unit_of_measurement", None)
        self._attr_suggested_unit_of_measurement = sc.get("suggested_unit_of_measurement", None)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = sc.get("device_class", None)

    def _value_conversion(self, value):
        """Function to process the original value. The default will be just return the value, 
        so must be overriden in the derived classes.

        Args:
            value: The original value of the sensor

        Returns:
            The converted value of the sensor.
            Can be a type change (str -> float for example), conversion (bytes -> bits)...
        """
        return value

    @property
    def native_value(self):
        # Get the current state from the coordinator
        sensor_id = self.sensor_data["sensor_id"]
        _LOGGER.debug("Getting the state of the sensor %s", sensor_id)
        value = self.hass.data[DOMAIN][self.entry.entry_id]["devices"][
            self.sensor_data["device_group"]
        ][sensor_id]["value"]
        # Convert the value using the internal function and return it
        return self._value_conversion(value)

    #async def async_update(self):
        # Request a data update to the coordinator
        #await self.coordinador.async_request_refresh()

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"OpenWRT Device: {self.entry.data['id']}",
            "manufacturer": "OpenWRT",
        }
        _LOGGER.debug("Device Info: %s", device_info)
        return device_info


class FloatEntity(BaseEntity):
    def _value_conversion(self, value):
        # Convert the value from str to float and then from octets to bits.
        # Bits should not have decimals, so will be converted to int.
        try:
            value = float(value)

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted: %s", self._attr_name, e)

        _LOGGER.debug("Value: %f", value)
        return value


class NumericEntity(BaseEntity):
    def _value_conversion(self, value):
        # Convert the value from str to int.
        # Bits should not have decimals, so will be converted to int.
        try:
            # Fist we will convert it to float because sometimes the values contains decimals
            # and then we will round it.
            value = round(float(value))

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted: %s", self._attr_name, e)

        _LOGGER.debug("Value: %d", value)
        return value

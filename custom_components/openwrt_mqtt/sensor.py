import logging
import re

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.mqtt import async_subscribe

from .constants import DOMAIN, ALLOWED_SENSORS

_LOGGER = logging.getLogger(__name__)

def get_device_name(device_type, name, entity_name):
    if device_type == "processor":
        name = name.format(entity_name.upper())
    elif device_type == "interface":
        interface = re.match("interface-(.+)", entity_name)
        name = name.format(interface.groups()[0])
    elif device_type in ["thermal-thermal", "thermal-cooling"]:
        device = re.match(
            "thermal-(thermal|cooling)_(.+)",
            entity_name
        )
        name = name.format(device.groups()[1].capitalize())
    elif device_type == "wireless":
        interface = re.match("iwinfo-(.+)", entity_name)
        name = name.format(interface.groups()[0])

    return name

def _determine_entity_device_group(entity_name):
    if re.match("cpu-[\\d]+", entity_name):
        return "processor"
    if re.match("interface-.+", entity_name):
        return "interface"
    if re.match("thermal-thermal_.*", entity_name):
        return "thermal-thermal"
    if re.match("thermal-cooling_.*", entity_name):
        return "thermal-cooling"
    if re.match("iwinfo-.*", entity_name):
        return "wireless"
    return entity_name



async def async_setup_entry(hass, entry, async_add_entities):
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
                entity = None
                if not sensor_id in hass.data[DOMAIN][entry.entry_id]["devices"][device_group]:
                    device_name = get_device_name(device_group, partition["name"], entity_found.groups()[0])
                    _LOGGER.debug(
                        "The sensor doesn't exists yet. Adding the entity for %s",
                        sensor_id
                    )
                    if sensor_config["sensor_type"] == "numeric":
                        entity = NumericEntity(
                            entry, device_name, sensor_config,
                            f"{entry.data['id']}_{sensor_id}",
                            partition.get("icon", sensor_config.get("icon", "mdi:cancel"))
                        )
                    elif sensor_config["sensor_type"] == "float":
                        entity = FloatEntity(
                            entry, device_name, sensor_config,
                            f"{entry.data['id']}_{sensor_id}",
                            partition.get("icon", sensor_config.get("icon", "mdi:cancel"))
                        )
                    else:
                        _LOGGER.warning("The sensor type %s is not managed by the entities setup. "
                                        "Please, report this to the developer.",
                                        sensor_config["type"])
                        continue
                    async_add_entities([entity])
                    hass.data[DOMAIN][entry.entry_id]["devices"][device_group][sensor_id] = entity
                    if entity.enabled:
                        entity.update_value(splitted_values[(1 + idx)])
                    
                else:
                    entity = hass.data[DOMAIN][entry.entry_id]["devices"][device_group][sensor_id]
                    if entity.enabled:
                        entity.update_value(splitted_values[(1 + idx)])

    hass.data[DOMAIN].get(entry.entry_id)["unsubscribe"] = (
        await async_subscribe(hass, f"{entry.data["mqtt_topic"]}/#", _received_message)
    )

class BaseEntity(SensorEntity):
    should_poll = False
    def __init__(self, entry, device_name, sensor_config, unique_id, icon):
        self.entry = entry
        self._native_value = None

        # Sensor attributes
        self._attr_name = device_name
        self._attr_icon = icon
        self._attr_unique_id = unique_id
        self._attr_suggested_display_precision = sensor_config.get("precision", None)
        self._attr_entity_registry_enabled_default = sensor_config.get("enabled_default", None)
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC if sensor_config.get("diagnostic", False) else None)

        self._attr_native_unit_of_measurement = sensor_config.get("native_unit_of_measurement", None)
        self._attr_suggested_unit_of_measurement = sensor_config.get("suggested_unit_of_measurement", None)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = sensor_config.get("device_class", None)

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

    def update_value(self, value):
        # Convert the retrieved value
        self._native_value = self._value_conversion(value)
        # Inform to HASS about the update
        self.async_write_ha_state()

    @property
    def native_value(self):
        _LOGGER.debug("GETTING NATIVE VALUE: %r", self._attr_device_class)
        # Return the stored value
        return self._native_value

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

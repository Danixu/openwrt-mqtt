from datetime import timedelta
import logging
import re

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.components.mqtt import async_subscribe

from .constants import DOMAIN, ALLOWED_SENSORS

_LOGGER = logging.getLogger(__name__)

class OpenWRTMqttCoordinator(DataUpdateCoordinator):
    """
    Integration corrdinator which will centralice all the sensors updates.
    """
    def __init__(self, hass: HomeAssistant, entry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{entry.data["id"]} Coortinator",
            update_interval=timedelta(seconds=30),  # Update it every minute
        )
        self.entry = entry
        self.hass = hass
        self._unsubscribe = None

        _LOGGER.setLevel(logging.DEBUG)

        # Subscribe to the topic
        _LOGGER.debug("Suscribing to the topic %s/#", entry.data["mqtt_topic"])
        hass.async_create_task(self.async_subscribe_to_topic(f"{entry.data["mqtt_topic"]}/#"))

    async def async_subscribe_to_topic(self, topic):
        """Function that manage the subscription and store the unsubscribe function."""
        # Wait until the suscription is done and store the unsubscribe function
        self._unsubscribe = await async_subscribe(self.hass, topic, self._received_message)

    async def async_unsubscribe_from_topic(self):
        """Unsubscribe if the function was defined."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    async def _async_update_data(self):
        return self.hass.data[DOMAIN][self.entry.entry_id]["devices"]


    def _determine_entity_device_group(self, entity_name):
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

    async def _received_message(self, msg):
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
            device_group = self._determine_entity_device_group(entity_found.groups()[0])
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
            if device_group not in self.hass.data[DOMAIN][self.entry.entry_id]["devices"]:
                self.hass.data[DOMAIN][self.entry.entry_id]["devices"][device_group]= {}

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
                self.hass.data[DOMAIN][self.entry.entry_id]["devices"][device_group][sensor_id] = {
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

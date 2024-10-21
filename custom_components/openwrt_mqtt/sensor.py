import logging
import re

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorEntity, SensorStateClass

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

def get_devices(entry_id, devices):
    out_devices = {}
    for device_type, sensors in devices.items():
        for sensor_name, sensor_data in sensors.items():
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

            out_devices[f"{entry_id}_{device_type}_{sensor_name}"] = {
                "name": name,
                "type": sensor_data["sensor_config"]["sensor_type"],
                "data": sensor_data
            }

    return out_devices



async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    _LOGGER.setLevel(logging.DEBUG)

    # Function to dynamically update the entities.
    async def entities_update():
        new_entities = []
        _LOGGER.debug("Updating entities")

        devices = get_devices(entry.data['id'], hass.data[DOMAIN][entry.entry_id]["devices"])

        # Iterate over the devices and sensor in the coordinator
        for device_id, device_data in devices.items():
            # Verificar si la entidad ya existe
            if device_id not in hass.data[DOMAIN][entry.entry_id]["entities"]:
                entity = None

                if device_data["type"] == "numeric":
                    entity = NumericEntity(coordinator, entry, device_data)
                elif device_data["type"] == "float":
                    entity = FloatEntity(coordinator, entry, device_data)
                elif device_data["type"] == "octets":
                    entity = OctectsEntity(coordinator, entry, device_data)
                else:
                    _LOGGER.warning("The sensor type %s is not managed by the entities setup. "
                                    "Please, report this to the developer.", device_data["type"])
                    continue

                hass.data[DOMAIN][entry.entry_id]["entities"][device_id] = entity
                new_entities.append(entity)

        # Add the new entities to Home Assistant if there is any new
        if new_entities:
            _LOGGER.debug("There are new entities. Creating it...")
            async_add_entities(new_entities.copy())

    # Execute the first update
    await entities_update()

    # Dynamically update when the coordinator is updated
    coordinator.async_add_listener(lambda: hass.async_create_task(entities_update()))

class BaseEntity(SensorEntity):
    def __init__(self, coordinador, entry, sensor_data):
        self.coordinador = coordinador
        self.entry = entry
        self.sensor_data = sensor_data

        sc = sensor_data["data"]["sensor_config"]

        # Sensor attributes
        self._attr_name = sensor_data["name"]
        self._attr_icon = sensor_data["data"]["icon"]
        self._attr_unique_id = f"{entry.data['id']}_{sensor_data["data"]["sensor_id"]}"
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
        sensor_id = self.sensor_data["data"]["sensor_id"]
        _LOGGER.debug("Getting the state of the sensor %s", sensor_id)
        value = self.hass.data[DOMAIN][self.entry.entry_id]["devices"][
            self.sensor_data["data"]["device_group"]
        ][sensor_id]["value"]
        # Convert the value using the internal function and return it
        return self._value_conversion(value)

    async def async_update(self):
        # Request a data update to the coordinator
        await self.coordinador.async_request_refresh()

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
        # Convert the value from str to float and then from octets to bits.
        # Bits should not have decimals, so will be converted to int.
        try:
            value = int(value)

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted: %s", self._attr_name, e)

        _LOGGER.debug("Value: %d", value)
        return value


class OctectsEntity(BaseEntity):
    def _value_conversion(self, value):
        # Convert the value from str to float and then from octets to bits.
        # Bits should not have decimals, so will be converted to int.
        try:
            value = int(round(float(value) * 8, 0))

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted: %s", self._attr_name, e)

        _LOGGER.debug("Value: %d", value)
        return value

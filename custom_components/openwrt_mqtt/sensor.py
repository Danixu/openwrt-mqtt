import logging

from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.components.sensor import SensorStateClass

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

def get_devices(id, devices):
    out_devices = {}
    for device_type, sensors in devices.items():
        for sensor_name, sensor_data in sensors.items():
            name = sensor_data["sensor_data"]["name"]

            if device_type == "processor":
                name = name.format(sensor_data["extracted_data"][0].upper())

            out_devices[f"{id}_{device_type}_{sensor_name}"] = {
                "name": name,
                "type": sensor_data["sensor_data"]["sensor_type"],
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
                    entity = NumericEntity(
                        coordinator, entry, device_data["data"], device_data["name"],
                        device_data["data"]["sensor_data"].get("unit", ""),                        
                    )
                elif device_data["type"] == "float":
                    entity = FloatEntity(
                        coordinator, entry, device_data["data"], device_data["name"], 
                        device_data["data"]["sensor_data"].get("unit", ""),
                        device_data["data"]["sensor_data"].get("precision", 10),
                    )
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

class FloatEntity(Entity):
    def __init__(self, coordinador, entry, sensor_data, name, unit = "", precision = 10):
        self.coordinador = coordinador
        self.entry = entry
        self.sensor_data = sensor_data
        self.precision = precision

        self._attr_entity_registry_enabled_default = self.sensor_data["sensor_data"].get("enabled_default", False)
        self._attr_name = name
        self._attr_icon = self.sensor_data["sensor_data"]["icon"]
        self._attr_unique_id = f"{self.entry.data['id']}_{self.sensor_data["extracted_data"][0]}_{self.sensor_data["extracted_data"][1]}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if self.sensor_data["sensor_data"].get("diagnostic", False) else None
        self._state = None
        self._attr_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        # Get the current state from the coordinator
        sensor_id = f"{self.sensor_data["extracted_data"][0]}_{self.sensor_data["extracted_data"][1]}"
        _LOGGER.debug("Getting the state of the sensor %s", sensor_id)
        value = None
        try:
            value = float(self.hass.data[DOMAIN][self.entry.entry_id]["devices"][self.sensor_data["device_group"]][sensor_id]["value"].split(":")[1])
            value = round(value, self.precision)

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted to float: %s", self._attr_name, e)
        
        _LOGGER.debug("Value: %f%s", value, self._attr_unit_of_measurement)
        return value

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
        _LOGGER.debug(f"Device Info: {device_info}")
        return device_info

class NumericEntity(Entity):
    def __init__(self, coordinador, entry, sensor_data, name, unit = ""):
        self.coordinador = coordinador
        self.entry = entry
        self.sensor_data = sensor_data

        self._attr_entity_registry_enabled_default = self.sensor_data["sensor_data"].get("enabled_default", False)
        self._attr_name = name
        self._attr_icon = self.sensor_data["sensor_data"]["icon"]
        self._attr_unique_id = f"{self.entry.data['id']}_{self.sensor_data["extracted_data"][0]}_{self.sensor_data["extracted_data"][1]}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if self.sensor_data["sensor_data"].get("diagnostic", False) else None
        self._state = None
        self._attr_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        # Get the current state from the coordinator
        sensor_id = f"{self.sensor_data["extracted_data"][0]}_{self.sensor_data["extracted_data"][1]}"
        _LOGGER.debug("Getting the state of the sensor %s", sensor_id)
        value = None
        try:
            value = int(self.hass.data[DOMAIN][self.entry.entry_id]["devices"][self.sensor_data["device_group"]][sensor_id]["value"].split(":")[1])

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted to int: %s", self._attr_name, e)
        
        _LOGGER.debug("Value: %d%s", value, self._attr_unit_of_measurement)
        return value

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
        _LOGGER.debug(f"Device Info: {device_info}")
        return device_info

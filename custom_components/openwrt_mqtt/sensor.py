import logging

from homeassistant.helpers.entity import Entity
from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.setLevel(logging.DEBUG)

    # Create a container for the entitiesif it doesn't exists.
    if "entities" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entities"] = {}

    # Función para actualizar las entidades dinámicamente
    async def entities_update():
        new_entities = []
        _LOGGER.debug(entry.data)
        
        # Iterar sobre los dispositivos y sensores en el coordinador
        for device_name, sensors in coordinator.devices.items():
            for sensor_name in sensors:
                unique_id = f"{entry.data['id']}_{device_name}_{sensor_name}"
                
                # Verificar si la entidad ya existe
                if unique_id not in hass.data[DOMAIN]["entities"]:
                    entity = MiEntidad(coordinator, entry, device_name, sensor_name)
                    hass.data[DOMAIN]["entities"][unique_id] = entity
                    new_entities.append(entity)

        # Añadir nuevas entidades a Home Assistant si existen
        if new_entities:
            async_add_entities(new_entities)

    # Ejecutar la primera actualización
    await entities_update()

    # Actualizar dinámicamente cuando el coordinador se actualice
    coordinator.async_add_listener(lambda: hass.async_create_task(entities_update()))

class MiEntidad(Entity):
    def __init__(self, coordinador, entry, device_name, sensor_name):
        self.coordinador = coordinador
        self.entry = entry
        self.device_name = device_name
        self.sensor_name = sensor_name
        self._state = None

    @property
    def name(self):
        return f"{self.device_name} {self.sensor_name}"

    @property
    def unique_id(self):
        return f"{self.entry.data['id']}_{self.device_name}_{self.sensor_name}"

    @property
    def state(self):
        # Obtener el estado actual desde el coordinador
        return self.coordinador.devices[self.device_name][self.sensor_name]

    async def async_update(self):
        # Solicitar al coordinador que actualice los datos
        await self.coordinador.async_request_refresh()

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self.entry.data['id'])},
            "name": f"{self.entry.data['id']}: {self.device_name}",
            "manufacturer": "OpenWRT",
        }
        _LOGGER.debug(f"Device Info: {device_info}")
        return device_info

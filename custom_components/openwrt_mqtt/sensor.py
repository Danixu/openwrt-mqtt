from homeassistant.helpers.entity import Entity
from .constants import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinador = hass.data[DOMAIN][entry.entry_id]

    # Creamos un contenedor para las entidades dinámicas si no existe
    if "entities" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entities"] = {}

    # Función para actualizar las entidades dinámicamente
    async def actualizar_entidades():
        entidades_nuevas = []
        
        # Iterar sobre los dispositivos y sensores en el coordinador
        for device_name, sensors in coordinador.devices.items():
            for sensor_name in sensors:
                unique_id = f"{device_name}_{sensor_name}"
                
                # Verificar si la entidad ya existe
                if unique_id not in hass.data[DOMAIN]["entities"]:
                    entidad = MiEntidad(coordinador, device_name, sensor_name)
                    hass.data[DOMAIN]["entities"][unique_id] = entidad
                    entidades_nuevas.append(entidad)

        # Añadir nuevas entidades a Home Assistant si existen
        if entidades_nuevas:
            async_add_entities(entidades_nuevas)

    # Ejecutar la primera actualización
    await actualizar_entidades()

    # Actualizar dinámicamente cuando el coordinador se actualice
    coordinador.async_add_listener(lambda: hass.async_create_task(actualizar_entidades()))

class MiEntidad(Entity):
    def __init__(self, coordinador, device_name, sensor_name):
        self.coordinador = coordinador
        self.device_name = device_name
        self.sensor_name = sensor_name
        self._state = None

    @property
    def name(self):
        return f"{self.device_name} {self.sensor_name}"

    @property
    def unique_id(self):
        return f"{self.device_name}_{self.sensor_name}"

    @property
    def state(self):
        # Obtener el estado actual desde el coordinador
        return self.coordinador.devices[self.device_name][self.sensor_name]

    async def async_update(self):
        # Solicitar al coordinador que actualice los datos
        await self.coordinador.async_request_refresh()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_name)},
            "name": self.device_name,
            "manufacturer": "OpenWRT",
        }

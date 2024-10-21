import logging
import re
import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required('id'): cv.string,
    vol.Required('mqtt_topic'): cv.string,
})

_LOGGER.setLevel(logging.DEBUG)

class OpenWrtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the ipmi config flow."""
        self.discovery_info = None

    async def async_step_mqtt(self, discovery_info):
        """Handle discovery from MQTT."""
        _LOGGER.debug("Received MQTT discovery info: %s", discovery_info)
        self.discovery_info = discovery_info

        topic_data = re.match("^(openwrt\\/([\\w\\s\\-]+))\\/.*$", discovery_info.topic)

        if not topic_data:
            _LOGGER.warning("Cannot extract the device info from the autodiscovery data")
            return self.async_abort(
                reason="Cannot extract the device info from autodiscovery the data")

        _LOGGER.debug("Extracted Data: %r", topic_data.groups())

        # Verifica si ya existe una entrada con este ID
        for entry in self.hass.config_entries.async_entries('openwrt_mqtt'):
            if entry.data['id'] == topic_data.groups()[1]:
                _LOGGER.debug("The device was already configured")
                return self.async_abort(reason="Device already configured")

        _LOGGER.debug(
            "Detected a device with the ID %s and the topic %s.",
            topic_data.groups()[1], topic_data.groups()[0])

        self.context.update(
            {"title_placeholders": {"name": f"{topic_data.groups()[1]}"}}
        )

        # Presentar la opción de configuración
        return self.async_show_form(
            step_id='user',
            data_schema=STEP_USER_DATA_SCHEMA.extend(
                {
                    vol.Optional('id', default = topic_data.groups()[1]): cv.string,
                    vol.Optional('mqtt_topic', default = topic_data.groups()[0]): cv.string,
                }
            )
        )


    async def async_step_user(self, user_input=None):
        _LOGGER.debug("Input: %r", user_input)
        _LOGGER.debug("Discovery: %r", self.discovery_info)
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        title = f"{user_input["id"]}"
        # Verify if an entry with the same ID exists.
        for entry in self.hass.config_entries.async_entries('openwrt_mqtt'):
            if entry.data['id'] == user_input['id']:
                return self.async_abort(reason=f"The device ID {user_input['id']} already exists.")

        return self.async_create_entry(title=title, data=user_input)

# OpenWRT MQTT HASS Integration

This Home Assistant integration is an alternative to the official integrations which doesn't requires any kind of access to the device. The data will be sent by the device itself to a centralized MQTT broker (mosquitto or similar), and the integration will retreive that data into Home Assistant.

This integration is for people like me, who doesn't like to store their OpenWRT login data into HASS. Another advantage is that HASS doesn't needs direct access to the OpenWRT device. Both (the device and the integration) works as clients, so the only requirement is to have access to the MQTT instance.

## Requirements

This integration uses the MQTT integration to connect to the Mosquitto (or similar) broker.

## Installation

WIP
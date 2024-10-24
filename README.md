# OpenWRT MQTT HASS Integration

## About

OpenWRT is a linux operating system based routers firmware targeting embedded devices. It can replace the original firmware of several routers, AP, and even can be installed into virtual machines, and allow a fully customization of the device whith extended functionalities via packages. Some of those packages are the collectd daemon with their modules, which allows to collect several metrics from the device and store it in rdd files. Another package allows to send those metrics to a MQTT server, and this HASS integration take advantage of that package.

There are official integrations in HASS to collect the data via Luci or Ubus, but they requires to store the OpenWRT credentials into HASS and even to make modifications into the device configuration.

This Home Assistant integration is an alternative to those official integrations without the requirement of modifications in the device or to store the credentials into HASS. The configuration can be made easily using the Luci interface without any kind of ssh access to the device.

## How it works

This integration uses the CollectD daemon to collect the device metrics and send it to a MQTT broker (Mosquitto or similar). The integration is connected to the broker listenning into the topic, waiting for the CollectD updates.

Once a message is received, the integration check the compatibility of the metric. If the metric is compatible, then it creates the entity if doesn't exists or will update the data if exists.

The communication is done from the OpenWRT device and the HASS instance to the Broker, so only the broker must be exposed. This allows to send the data from the OpenWRT devices which are located outside the local network without to expose it, just exposing the broker.

## Requirements

* MQTT Home Assistant integration (MQTT client)
* Mosquitto or similar (Broker)
* CollectD, the metrics modules depending of which data you want to collect, and the MQTT module to send the data to the Broker.

## ToDo

* Update the entity in real time (Actually the HASS instance is polling for updates)
* Devices autodiscovery

## Installation

### Install the Mosquitto Broker

Install and configure the Broker, which will manage all the metrics messages. The broker can be installed as [Home Assistant AddOn](https://github.com/home-assistant/addons/blob/master/mosquitto/DOCS.md), or using the [standalone installation website](https://mosquitto.org/).

Configure an user into the broker for the integration, and other for the OpenWRT device (you can use a common user or to create one by device).

### Install the MQTT AddOn into HASS

The MQTT AddOn will be used as client, so must be installed into HASS prior to install this integration. To do it you have to follow this steps.

* Settings -> Devices and services -> Add Integration
* Search "MQTT" to see the integration and add it
* Configure the settings according with the installation of the broker you made and save it

### Install the integration

* Navigate to Hacs in Home assistant
* Press the three dots in the top right corner to open the options menu
* Select the `Custom repositories` option
* On the new window, paste the url of this repository on the `Repository` option (`https://github.com/Danixu/openwrt-mqtt`), and select the `Integration` type.
* Search for `OpenWRT MQTT` in the search box and you will see the integration.

### Install the OpenWRT packages

In order to receive the data on the MQTT broker, we need some CollectD packages to collect it from the device. To install it we will have to follow this steps:

* Navigate to the `xxxxxx` menu and select the `xxxxx` option.
* Press the `Update packages` button to get an updated list of packages
* Search for `collectd` using the search box and you will see the available packages
* Install the packages:
  * collectd (Main application)
  * collectd-mod-mqtt (Send the data to the broker)
  * xxxx (Allows to manage the configuration in the LuCi interface)
* Alternatively, you can connect via ssh and use this command:
  `pkg install `
* Once the packages are installed, we will have to navigate to the `xxxxxx` menu and select the `xxxxx` option.
* There we will go to the tab `yyyyyy` and we will press the `configure` button next to the mqtt exporter.
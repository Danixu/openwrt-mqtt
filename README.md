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

* Navigate to the `System` menu and select the `Software` option.
* Press the `Update packages` button to get an updated list of packages
* Search for `collectd` using the search box and you will see the available packages
* Install the packages:
  * collectd (Main application)
  * collectd-mod-mqtt (Send the data to the broker)
  * luci-app-statistics (Allows to manage the configuration in the LuCi interface)
* Alternatively, you can connect via ssh and use this command:
  `opkg install collectd collectd-mod-mqtt luci-app-statistics`
  This will install other packages like for example the `collectd-mod-cpu` or `collectd-mod-iwinfo`.

The available packages compatible with this integrations are:
* **collectd-mod-conntrack**: in-kernel connection tracking state table.
* **collectd-mod-contextswitch**: CPU context switches
* **collectd-mod-cpu**: Device CPU usage
* **collectd-mod-dhcpleases**: DHCP Leases info
* **collectd-mod-interface**: Interface information like Bandwidth and Packets
* **collectd-mod-ipstatistics**: Received, sent, dropped and errors in Packets
* **collectd-mod-iwinfo**: Wireless information
* **collectd-mod-load**: Device Load
* **collectd-mod-memory**: Device memory usage 
* **collectd-mod-thermal**: Device temperatures
* **collectd-mod-uptime**: Device Uptime

To install all the packages you can use this command:

```
opkg install collectd collectd-mod-mqtt luci-app-statistics collectd-mod-conntrack collectd-mod-contextswitch collectd-mod-cpu collectd-mod-dhcpleases collectd-mod-interface collectd-mod-ipstatistics collectd-mod-iwinfo collectd-mod-load collectd-mod-memory collectd-mod-thermal collectd-mod-uptime
```

## Configuration

### Configure the Collectd Exporter

The first we will need is to configure the Collectd exporter to send the metrics to the MQTT broker. To do it we will follow this steps:

* On the OpenWRT device we will have to navigate to the `Stadistics` menu and select the `Setup` option. If the menu doesn't exists then a logout/login can be necessary.
* There we will go to the tab `Output plugins` and we will activate the checkboxt next to it.
* A new Window will be open where we will be able to configure the server and the credentials. Just we will press `Add` and we will fill the fields.
* An important field is the Prefix field, which we will use to configure the integration.
* On the `Collectd Settings` tab, we can configure the `Hostname`, which will be used to configure the integration too. It's important to set an unique hostname or the data will be mixed.

In some versions of OpenWRT the MQTT plugin doesn't appear in Luci after installing it. In this case, the configuration must be done manually.

* Connect to the device via SSH
* Edit the file `/etc/collectd.conf`
* In this file we will add the following lines:

```
LoadPlugin mqtt              
<Plugin mqtt>          
        <Publish "Home Assistant">
                Host "<Host>"
                Port 1883
                User "<user>"    
                Password "<password>"
                Qos 0    
                Prefix openwrt    
                Retain true                          
                Retain false
        </Publish>                
</Plugin> 
```

Changing the `Host`, `Port`, `User` and `Password` fields with the correct data of our MQTT server.

We will have to configure which modules data we want to export to our integration on the `General` and `Network` plugins tabs. Here we can select with the checkbox the plugins to use. Also the CPU and Memory plugins will require to enable the Percentage values to be visible (the integration uses that values).

### Configure the integration

Once we have the exported configured, it's time to capture the data into the Home Assistant integration. To do it we will do the following steps:

* Navigate to the `Settings` menu -> `Devices & Services` -> `Integrations`
* Here we will have to press the `Add Integration` button and search for the `OpenWRT MQTT` Integration
* On the new window that will be opened, we will configure the settings according to the previous exporter configuration.
  * `Device Name`: The name that we want to set to our device. Must be unique.
  * `MQTT Topic prefix`: The Prefix configured in the Collectd exporter followed by the device hostname: `<prefix>/<hostname>`. For example `collectd/MyDevice`.
* We will press `Submit` to save the settings and the new device will be added

The entities will be added automatically once that data is received. Depending of the configured data sent inteval
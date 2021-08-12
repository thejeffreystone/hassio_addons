# Home Assistant Add-on: Acurite2mqtt

A Home Assistant addon for a software defined radio tuned to listen for 433MHz RF transmissions from Acurite Weather Sensors and republish the data via MQTT.

## Installation

Add the repository URL under **Supervisor → Add-on store → ⋮ → Manage add-on repositories**:

    https://github.com/thejeffreystone/hassio-addons

Then search for `Accurite to home Assistant` and install it.

## Configuration

Example add-on configuration:

```yaml
mqtt_host: 192.168.7.100
mqtt_user: mqtt_user
mqtt_password: mqtt_pass
mqtt_topic: rtl_433
mqtt_retain: 'true'
protocol: '-R 11 -R 40 -R 41 -R 55 -R 74'
whitelist_enable: true
whitelist: 2169 6417 9143 6449 6000 3125
units: 'si'
discovery_prefix: homeassistant
discovery_interval: 600
debug: false
```

### Option: `mqtt_host`

The `mqtt_host` option is the ip address of your mqtt server. If you are using the embeded server in Home Assistant just use your instances ip address.

### Option: `mqtt_user`

This is the username required to access your mqtt server.

### Option: `mqtt_password`

The password of the mqtt user account.

### Option: `mqtt_topic`

This si the topic your devices will use.

### Option: `mqtt_retain`

Setting this to `true` means the mqtt server will keep your last value 
until it is changed. Setting it to `false` means the server will forget values after a period of time, 
so you will onyl see a valus it one has been sent recently.

### Option: `protocol`

This determines what devices the software listens to. `-R 11 -R 40 -R 41 -R 55 -R 74` 
is the Accurite sensors. If the protocol is blank it will listen for all devices
which may be noisy.

For all possible protocols visit <https://github.com/thejeffreystone/hassio_addons/blob/main/acurite2mqtt/PROTOCOLS.md>

### Option: `whitelist_enable`

Set to `true` to enable filtering to allow only the delcared device id's to be processed.  You may turn this off periodically
to scan/acquire new device id's.  But be cautious... any undesirable devices will need to be deleted from your configuration.

### Option: `whitelist`

This is a `space separated` list of device id's that are desired to be received and processed.  Any devices that are not in this
list will be ignored (if whitelist_enables is set to true).

### Option: `units`

Sets the meansurement units. 
- `si` = Metric
- `customary` = Imperial / Customary  

### Option: `discovery_prefix`

The mqtt prefix for autodiscovery. `homeassistant` should work. If you use another autodiscovery may not work.

### Option: `discovery_interval`

`600` means Home Assisatnt will check for new devices every 600 seconds. 

### Option: 'debug'

Set debug to `true` if you want to see extra logging. This is noisy though, so I would only run it when actively troubleshooting. Leave at false all other times. 

## Known issues and limitations

- This add-on is totally beta. 

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality. The format of the log is based on
[Keep a Changelog][keepchangelog].

Releases are based on [Semantic Versioning][semver], and use the format
of ``MAJOR.MINOR.PATCH``. In a nutshell, the version will be incremented
based on the following:

- ``MAJOR``: Incompatible or major changes.
- ``MINOR``: Backwards-compatible new features and enhancements.
- ``PATCH``: Backwards-compatible bugfixes and package updates.

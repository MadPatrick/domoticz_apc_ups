# domoticz-apc-ups-plugin
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![Domoticz](https://img.shields.io/badge/Domoticz-2022%2B-blue)
![Python](https://img.shields.io/badge/Python-3.7+-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Domoticz APC UPS plugin

This plugin retrieves data from the APC UPS. It uses `apcaccess` to retrieve the details.

**Installation**

On your machine with USB or connectivity to the APC UPS:

```sudo apt-get install apcupsd ```

And configure it to be able to retrieve the APC UPS data

If domoticz runs on another machine, install it again there so the `apcaccess` executable exists. But disable apcupsd:

```
sudo systemctl stop apcupsd
sudo systemctl disable apcupsd
```


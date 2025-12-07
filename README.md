# 🔋 APC UPS Plugin for Domoticz

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![Domoticz](https://img.shields.io/badge/Domoticz-2022%2B-blue)
![Python](https://img.shields.io/badge/Python-3.7+-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

This Domoticz plugin allows you to monitor an **APC UPS** using the `apcaccess` command-line tool provided by **apcupsd**.  
It retrieves real-time UPS metrics including battery level, load percentage, input voltage, runtime remaining, transfer reasons, and much more.

> Original author of the base implementation: **Joerek van Gaalen**  
> Extended, modernized and maintained by **MadPatrick**

---

## 🧰 Features

✔️ Retrieves live UPS status from **APC UPS units**  
✔️ Uses reliable `apcaccess` interface  
✔️ Displays power metrics, battery metrics, timings and device specifics  
✔️ Supports multiple data fields (Line voltage, Time on battery, Load %, Last test, etc.)  
✔️ Works via USB, network-connected UPS, or remote system  
✔️ No cloud dependencies  
✔️ Runs on Linux-based Domoticz installations

---

## 🚀 Requirements

The plugin depends on the **apcupsd** package.  
It provides the `apcaccess` executable used to query the UPS.

Install it on the machine connected to your UPS:

```bash
sudo apt-get install apcupsd
```

If your **Domoticz server runs elsewhere**, install apcupsd there too so `apcaccess` exists:

```bash
sudo systemctl stop apcupsd
sudo systemctl disable apcupsd
```

This avoids running two UPS daemons while still allowing status retrieval.

---

## 📦 Installation

Clone the plugin into the Domoticz `plugins` directory:

```bash
cd domoticz/plugins
git clone https://github.com/MadPatrick/domoticz_apc_ups apc-ups
sudo systemctl restart domoticz
```

Domoticz will load the plugin automatically on restart.

---

## ⚙️ Configuration

Open **Domoticz → Hardware** and add:

**APC UPS**

| Field | Description |
|-------|-------------|
| Address | IP address of the APC UPS (default: 127.0.0.1) |
| Port | UPS port number (default: 3551) |
| Reading Interval | Polling interval in seconds |
| apcaccess path | Full path to the `apcaccess` binary (default: `/sbin/apcaccess`) |

Once saved, Domoticz will create devices based on detected UPS parameters.

---

## 📊 Available Metrics

Depending on your UPS model, the plugin creates devices for:

- Status
- Load %
- Battery charge
- Line voltage
- Transfer reason
- Time remaining
- Last self-test date
- Battery date
- UPS nominal power
- Runtime statistics
- Cumulative battery usage
- Nominal / Battery voltages
- And many more UPS details

Unused fields are created but disabled by default — enable only what you need.

---

## 🔄 Updating the Plugin

```bash
cd domoticz/plugins/domoticz_apc_ups
git pull
sudo systemctl restart domoticz
```

---

## 🧪 Tested On

- APC Back-UPS series  
- apcupsd 3.x  
- Domoticz 2022+  
- Python 3.7 – 3.11

---

## 📜 License

Released under the **MIT License**  
You may use, modify and distribute this plugin freely.

---

## 🎉 Done!

Your APC UPS data is now fully integrated in Domoticz 🟢  
Monitor power conditions, battery health and UPS performance directly in your home automation dashboard!


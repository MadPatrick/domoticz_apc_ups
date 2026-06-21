#!/usr/bin/env python
# ORIGINAL AUTHOR Joerek van Gaalen
# Modified by MadPatrick
# Version 1.0 - Reliability fixes, debug label localization

"""
<plugin key="APCUPS" name="APC UPS" author="Joerek van Gaalen" version="1.0" externallink="https://github.com/jgaalen/domoticz-apc-ups-plugin" wikilink="https://github.com/MadPatrick/domoticz_apc_ups" >
    <description>
        <br/><h2>APC UPS plugin</h2>
        Version: 1.0<br/>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="40px" required="true" default="3551"/>
        <param field="Mode1" label="Reading Interval (sec)" width="40px" required="true" default="10" />
        <param field="Mode2" label="APC Access Path" width="200px" required="true" default="/sbin/apcaccess" />
        <param field="Mode3" label="Enable Debug Logging" width="75px">
            <options>
                <option label="Nee" value="0" default="true" />
                <option label="Ja" value="1" />
            </options>
        </param>
    </params>
</plugin>"""

import Domoticz
import subprocess
import os

imageID = 0

def DebugLog(message):
    try:
        if Parameters.get("Mode3") == "1":
            Domoticz.Debug(message)
    except Exception:
        pass

# Device definities
# Used: 1 = zichtbaar in Domoticz, 0 = verborgen
values = {
    'STATUS':    {'dname': 'Status',                    'dunit':  1, 'dtype': 243, 'dsubtype': 19, 'Used': 1},
    'LINEV':     {'dname': 'Line Voltage',              'dunit':  2, 'dtype': 243, 'dsubtype':  8, 'Used': 1},
    'LOADPCT':   {'dname': 'Load Percentage',           'dunit':  3, 'dtype': 243, 'dsubtype':  6, 'options': {'Custom': '1;%'},       'Used': 1},
    'BCHARGE':   {'dname': 'Battery Charge',            'dunit':  4, 'dtype': 243, 'dsubtype':  6, 'options': {'Custom': '1;%'},       'Used': 1},
    'MODEL':     {'dname': 'Model',                     'dunit':  5, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'SERIALNO':  {'dname': 'Serial Number',             'dunit':  6, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'BATTV':     {'dname': 'Battery Voltage',           'dunit':  7, 'dtype': 243, 'dsubtype':  8, 'Used': 0},
    'NOMBATTV':  {'dname': 'Nominal Battery Voltage',   'dunit':  8, 'dtype': 243, 'dsubtype':  8, 'Used': 0},
    'BATTDATE':  {'dname': 'Battery Date',              'dunit':  9, 'dtype': 243, 'dsubtype': 19, 'Used': 1},
    'SELFTEST':  {'dname': 'Last Self Test',            'dunit': 10, 'dtype': 243, 'dsubtype': 19, 'Used': 1},
    'LASTXFER':  {'dname': 'Last Transfer Reason',      'dunit': 11, 'dtype': 243, 'dsubtype': 19, 'Used': 1},
    'NOMPOWER':  {'dname': 'Nominal UPS Power',         'dunit': 12, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;W'},    'Used': 1},
    'TIMELEFT':  {'dname': 'Time Left on Battery',      'dunit': 13, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;MIN'}, 'Used': 1},
    'NUMXFERS':  {'dname': 'Number of Transfers',       'dunit': 14, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;times'},   'Used': 1},
    'TONBATT':   {'dname': 'Time on Battery',           'dunit': 15, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;MIN'}, 'Used': 1},
    'CUMONBATT': {'dname': 'Cumulative Time on Battery','dunit': 16, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;MIN'}, 'Used': 1},
    'UPSNAME':   {'dname': 'UPS Name',                  'dunit': 17, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'CABLE':     {'dname': 'Cable Type',                'dunit': 18, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'FIRMWARE':  {'dname': 'Firmware',                  'dunit': 19, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'UPSMODE':   {'dname': 'UPS Mode',                  'dunit': 20, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'STARTTIME': {'dname': 'UPS Start Time',            'dunit': 21, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'MINTIMEL':  {'dname': 'Minimum Battery Time',      'dunit': 22, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;MIN'}, 'Used': 0},
    'MAXTIME':   {'dname': 'Maximum Battery Time',      'dunit': 23, 'dtype': 243, 'dsubtype': 31, 'options': {'Custom': '1;MIN'}, 'Used': 0},
    'SENSE':     {'dname': 'Voltage Sense',             'dunit': 24, 'dtype': 243, 'dsubtype': 19, 'Used': 0},
    'LOTRANS':   {'dname': 'Low Transfer Voltage',      'dunit': 25, 'dtype': 243, 'dsubtype':  8, 'Used': 1},
    'HITRANS':   {'dname': 'High Transfer Voltage',     'dunit': 26, 'dtype': 243, 'dsubtype':  8, 'Used': 1},
    'NOMINV':    {'dname': 'Nominal Input Voltage',     'dunit': 27, 'dtype': 243, 'dsubtype':  8, 'Used': 0},
}

def UpdateDevice(Unit, nValue, sValue, BatteryLevel=None):
    if Unit in Devices:
        dev = Devices[Unit]
        if (dev.nValue != nValue) or (dev.sValue != str(sValue)) or \
           (BatteryLevel is not None and dev.BatteryLevel != BatteryLevel):
            kwargs = {"nValue": nValue, "sValue": str(sValue)}
            if BatteryLevel is not None:
                kwargs["BatteryLevel"] = int(BatteryLevel)
            dev.Update(**kwargs)
            DebugLog(f"Device {dev.Name} (Unit {Unit}) updated.")

def SetStatusError(message):
    try:
        UpdateDevice(values['STATUS']['dunit'], 0, message)
    except Exception as err:
        Domoticz.Error(f"Failed to update status device: {err}")

def onStart():
    global imageID
    Domoticz.Log(f"APC UPS Plugin started - version {Parameters['Version']}")
    try:
        Domoticz.Debugging(1 if Parameters.get("Mode3") == "1" else 0)
    except Exception:
        pass

    # Icon setup
    _IMAGE = "UPS"
    try:
        if _IMAGE not in Images:
            Domoticz.Image(_IMAGE + ".zip").Create()
    except Exception as e:
        Domoticz.Error(f"Failed to load icon pack '{_IMAGE}.zip': {e}")
    if _IMAGE in Images:
        imageID = Images[_IMAGE].ID
        DebugLog(f"Icon loaded (ImageID={imageID})")
    else:
        Domoticz.Log(f"Unable to load icon pack '{_IMAGE}.zip', continuing without custom icon")

    for key, val in values.items():
        if val['dunit'] not in Devices:
            try:
                Domoticz.Device(
                    Name=val['dname'],
                    Unit=val['dunit'],
                    Type=val['dtype'],
                    Subtype=val['dsubtype'],
                    Used=val.get('Used', 0),
                    Options=val.get('options', {}),
                    Image=imageID if imageID != 0 else 0
                ).Create()
            except Exception as e:
                Domoticz.Error(f"Failed to create device {val['dname']}: {e}")

    try:
        interval = int(Parameters["Mode1"])
        if interval < 1:
            Domoticz.Error("Mode1 (Reading Interval) below 1s, using 1s")
            interval = 1
        Domoticz.Heartbeat(interval)
    except (ValueError, TypeError):
        Domoticz.Error("Mode1 (Reading Interval) is invalid, using default 10s")
        Domoticz.Heartbeat(10)

def ParseBatteryLevel(raw_charge):
    if raw_charge is None:
        return None
    try:
        clean_charge = ''.join(c for c in str(raw_charge) if c.isdigit() or c == '.')
        if clean_charge == "":
            return None
        return max(0, min(100, int(float(clean_charge))))
    except (ValueError, TypeError):
        return None

def onHeartbeat():
    path = Parameters.get("Mode2", "").strip()
    if not path:
        Domoticz.Error("APC Access Path is empty. Please check plugin settings!")
        SetStatusError("apcaccess path missing")
        return
    if not os.path.exists(path):
        Domoticz.Error(f"'{path}' not found. Please check 'APC Access Path' in settings!")
        SetStatusError("apcaccess not found")
        return
    if not os.access(path, os.X_OK):
        Domoticz.Error(f"'{path}' is not executable. Please check permissions!")
        SetStatusError("apcaccess not executable")
        return

    try:
        res = subprocess.check_output(
            [path, '-u', '-h', f"{Parameters['Address']}:{Parameters['Port']}"],
            encoding='utf-8',
            errors='replace',
            timeout=5,
            stderr=subprocess.STDOUT
        )

        parsed_data = {}
        for line in res.strip().splitlines():
            key, sep, val = line.partition(':')
            if not sep:
                continue
            parsed_data[key.strip()] = val.strip()

        batt_level = ParseBatteryLevel(parsed_data.get('BCHARGE'))

        for key, config in values.items():
            if key not in parsed_data:
                continue

            raw_val = parsed_data[key]
            if raw_val.upper() in ('N/A', 'NONE', ''):
                continue

            if config['dsubtype'] != 19:
                clean_val = raw_val.split()[0]
                if key in ('TONBATT', 'CUMONBATT', 'MAXTIME'):
                    try:
                        clean_val = str(round(float(clean_val) / 60, 2))
                    except (ValueError, TypeError):
                        pass
            else:
                clean_val = raw_val

            UpdateDevice(config['dunit'], 0, clean_val, BatteryLevel=batt_level)

    except subprocess.TimeoutExpired:
        SetStatusError("Connection timeout")
        Domoticz.Error("Connection Timeout: UPS via apcaccess unreachable")
    except subprocess.CalledProcessError as e:
        SetStatusError("apcaccess error")
        Domoticz.Error(f"apcaccess returned error (exit {e.returncode}): {e.output}")
    except Exception as err:
        SetStatusError("Plugin error")
        Domoticz.Error(f"Unexpected error in onHeartbeat: {err}")

def onStop():
    Domoticz.Log("APC UPS Plugin stopped.")

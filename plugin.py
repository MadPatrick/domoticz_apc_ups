#!/usr/bin/env python
# ORIGINAL AUTHOR Joerek van Gaalen
# Modified by MadPatrick
# Version 1.5 - Added stability and better error handling

"""
<plugin key="APCUPS" name="APC UPS" author="MadPatrick" version="1.6" externallink="https://github.com/MadPatrick/APCUPS">
    <description>
        <br/><h2>APC UPS plugin</h2>
        <strong>Version:</strong> 1.6<br/>
        <strong>Author:</strong> MadPatrick (Original: Joerek van Gaalen)<br/>
        <br/>
        <hr/>
        <br/>
        <h2>= Configuration =</h2>
        <br/>
        <table style="width:100%; text-align:left; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid #ccc;">
                    <th style="padding: 8px;">Setting</th>
                    <th style="padding: 8px;">Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px;"><b>Address</b></td>
                    <td style="padding: 8px;">Fill in the IP address of the UPS.</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Port</b></td>
                    <td style="padding: 8px;">Fill in the port address of the UPS.</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Reading Interval</b></td>
                    <td style="padding: 8px;">Time (in sec) for the next refresh.</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>APC access path</b></td>
                    <td style="padding: 8px;">Location of the APC software on the system.</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Debug Log</b></td>
                    <td style="padding: 8px;">Enable or disable debug logging.</td>
                </tr>
            </tbody>
        </table>
        <br/>
    </description>
    <params>
        <param field="Address" label="UPS IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="40px" required="true" default="3551"/>
        <param field="Mode1" label="Reading Interval (sec)" width="40px" required="true" default="10" />
        <param field="Mode2" label="APC Access Path" width="200px" required="true" default="/sbin/apcaccess" />
        <param field="Mode3" label="Enable Debug Logging" width="75px">
            <options>
                <option label="Off" value="0" default="true" />
                <option label="On" value="1" />
            </options>
        </param>
    </params>
</plugin>"""

import Domoticz
import subprocess
import os

# FIX 1: imageID als globale variabele met expliciete global declaratie waar nodig
imageID = 0

def DebugLog(message):
    if Parameters.get("Mode3") == "1":
        Domoticz.Debug(message)

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
    'LOTRANS':   {'dname': 'Low Transfer Voltage',      'dunit': 25, 'dtype': 243, 'dsubtype':  8, 'options': {'Custom': '1;V'},       'Used': 1},
    'HITRANS':   {'dname': 'High Transfer Voltage',     'dunit': 26, 'dtype': 243, 'dsubtype':  8, 'options': {'Custom': '1;V'},       'Used': 1},
    'NOMINV':    {'dname': 'Nominal Input Voltage',     'dunit': 27, 'dtype': 243, 'dsubtype':  8, 'options': {'Custom': '1;V'},       'Used': 0},
}

def UpdateDevice(Unit, nValue, sValue, BatteryLevel=None):
    if Unit in Devices:
        dev = Devices[Unit]
        # Alleen updaten bij wijziging om database-vervuiling te voorkomen
        if (dev.nValue != nValue) or (dev.sValue != str(sValue)) or \
           (BatteryLevel is not None and dev.BatteryLevel != BatteryLevel):
            kwargs = {"nValue": nValue, "sValue": str(sValue)}
            if BatteryLevel is not None:
                kwargs["BatteryLevel"] = int(BatteryLevel)
            # FIX 6: Image niet meesturen bij updates â€” icoon alleen bij aanmaak zetten
            # zodat een gebruiker het icoon niet kwijtraakt bij elke sensorupdate
            dev.Update(**kwargs)
            DebugLog(f"Device {dev.Name} (Unit {Unit}) updated.")

def onStart():
    global imageID
    Domoticz.Log(f"APC UPS Plugin started - version {Parameters['Version']}")

    # Icon setup
    _IMAGE = "UPS"
    if _IMAGE not in Images:
        Domoticz.Image(_IMAGE + ".zip").Create()
    if _IMAGE in Images:
        imageID = Images[_IMAGE].ID
        DebugLog(f"Icon loaded (ImageID={imageID})")
    else:
        # FIX 5: foutmelding als icon pack niet geladen kan worden
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

    # FIX 8: veilige parse van Mode1 zodat een ongeldige waarde niet crasht
    try:
        Domoticz.Heartbeat(int(Parameters["Mode1"]))
    except (ValueError, TypeError):
        Domoticz.Error("Mode1 (Reading Interval) is invalid, using default 10s")
        Domoticz.Heartbeat(10)

def onHeartbeat():
    path = Parameters["Mode2"]
    if not os.path.exists(path):
        Domoticz.Error(f"'{path}' not found. Please check 'APC Access Path' in settings!")
        return

    try:
        # apcaccess aanroepen â€” -u verwijdert eenheden uit de output
        res = subprocess.check_output(
            [path, '-u', '-h', f"{Parameters['Address']}:{Parameters['Port']}"],
            text=True,
            timeout=5
        )

        parsed_data = {}
        for line in res.strip().split('\n'):
            key, _, val = line.partition(': ')
            parsed_data[key.strip()] = val.strip()

        # Batterij percentage bepalen voor de icoontjes/status
        raw_charge = parsed_data.get('BCHARGE', '100')
        try:
            clean_charge = ''.join(c for c in raw_charge if c.isdigit() or c == '.')
            batt_level = int(float(clean_charge))
        except (ValueError, TypeError):
            batt_level = 100

        for key, config in values.items():
            if key not in parsed_data:
                continue

            raw_val = parsed_data[key]
            if raw_val.upper() in ('N/A', 'NONE', ''):
                continue

            # Numerieke velden: verwijder eventuele eenheden (bijv. "230.0 Volts" -> "230.0")
            # Tekstvelden (subtype 19): bewaar de volledige string
            if config['dsubtype'] != 19:
                clean_val = raw_val.split(' ')[0]
            else:
                clean_val = raw_val

            UpdateDevice(config['dunit'], 0, clean_val, BatteryLevel=batt_level)

    except subprocess.TimeoutExpired:
        Domoticz.Error("Connection Timeout: UPS via apcaccess unreachable")
    # FIX 9: specifieke except voor niet-nul exitcode van apcaccess
    except subprocess.CalledProcessError as e:
        Domoticz.Error(f"apcaccess returned error (exit {e.returncode}): {e.output}")
    except Exception as err:
        Domoticz.Error(f"Unexpected error in onHeartbeat: {err}")

def onStop():
    Domoticz.Log("APC UPS Plugin stopped.")

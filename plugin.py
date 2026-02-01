#!/usr/bin/env python
# ORIGINAL AUTHOR Joerek van Gaalen
# Modified by MadPatrick
# Version 1.4 - Added stability and better error handling

"""
<plugin key="APCUPS" name="APC UPS" author="MadPatrick" version="1.4" externallink="https://github.com/MadPatrick/APCUPS">
    <description>
        <br/><h2>APC UPS plugin</h2>
        version: 1.4
        <br/>
        <br/>ORIGINAL AUTHOR : Joerek van Gaalen
        <br/>----------------------------------------------------------------------------------
        <br/>
        <br/><h2>= Configuration =</h2>
        <br/>
        <b style="padding-right:91px;">Address</b>: Fill in the IP address<br/>
        <b style="padding-right:115px;">Port</b>: Fill in the port address of the UPS<br/>
        <b style="padding-right:40px;">Reading Interval </b>: Time for the next refresh<br/>
        <b style="padding-right:40px;">APC access path </b>: location of the APC software<br/>
        <b style="padding-right:73px;">Debug Log </b>: do you want Debug loggig On or Off<br/>
    </description>
    <params>
        <param field="Address" label="Your APC UPS Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="40px" required="true" default="3551"/>
        <param field="Mode1" label="Reading Interval (sec)" width="40px" required="true" default="10" />
        <param field="Mode2" label="apcaccess path" width="200px" required="true" default="/usr/bin/apcaccess" />
        <param field="Mode3" label="Enable Debug Logging" width="75px">
            <options>
                <option label="Off" value="0" default="true" />
                <option label="On" value="1" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import subprocess
import os  # Essentieel voor bestandssysteem checks

imageID = 0

def DebugLog(message):
    if Parameters.get("Mode3") == "1":
        Domoticz.Debug(message)

values = {
    'STATUS': {'dname': 'Status', 'dunit': 1, 'dtype':243, 'dsubtype':19, 'Used': True, 'Image': True},
    'LINEV': {'dname': 'Line Voltage', 'dunit': 2, 'dtype':243, 'dsubtype':8, 'Used': True, 'Image': True},
    'LOADPCT': {'dname': 'Load Percentage', 'dunit': 3, 'dtype':243, 'dsubtype':6, 'options':'1;%', 'Used': True, 'Image': True},
    'BCHARGE': {'dname': 'Battery Charge', 'dunit': 4, 'dtype':243, 'dsubtype':6, 'options':'1;%', 'Used': True, 'Image': True},
    'MODEL': {'dname': 'Model', 'dunit': 5, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'SERIALNO': {'dname': 'Serial Number', 'dunit': 6, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'BATTV': {'dname': 'Battery Voltage', 'dunit': 7, 'dtype':243, 'dsubtype':8, 'Used': False, 'Image': True},
    'NOMBATTV': {'dname': 'Nominal Battery Voltage', 'dunit': 8, 'dtype':243, 'dsubtype':8, 'Used': False, 'Image': True},
    'BATTDATE': {'dname': 'Battery Date', 'dunit': 9, 'dtype':243, 'dsubtype':19, 'Used': True, 'Image': True},
    'SELFTEST': {'dname': 'Last Self Test', 'dunit': 10, 'dtype':243, 'dsubtype':19, 'Used': True, 'Image': True},
    'LASTXFER': {'dname': 'Last Transfer Reason', 'dunit': 11, 'dtype':243, 'dsubtype':19, 'Used': True, 'Image': True},
    'NOMPOWER': {'dname': 'Nominal UPS Power', 'dunit': 12, 'dtype':243, 'dsubtype':31, 'options':'1;Watt', 'Used': True, 'Image': True},
    'TIMELEFT': {'dname': 'Time Left on Battery', 'dunit': 13, 'dtype':243, 'dsubtype':31, 'options':'1;minutes', 'Used': True, 'Image': True},
    'NUMXFERS': {'dname': 'Number of Transfers', 'dunit': 14, 'dtype':243, 'dsubtype':31, 'options':'1;times', 'Used': True, 'Image': True},
    'TONBATT': {'dname': 'Time on Battery', 'dunit': 15, 'dtype':243, 'dsubtype':31, 'options':'1;minutes', 'Used': True, 'Image': True},
    'CUMONBATT': {'dname': 'Cumulative Time on Battery', 'dunit': 16, 'dtype':243, 'dsubtype':31, 'options':'1;minutes', 'Used': True, 'Image': True},
    'UPSNAME': {'dname': 'UPS Name', 'dunit': 17, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'CABLE': {'dname': 'Cable Type', 'dunit': 18, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'FIRMWARE': {'dname': 'Firmware', 'dunit': 19, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'UPSMODE': {'dname': 'UPS Mode', 'dunit': 20, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'STARTTIME': {'dname': 'UPS Start Time', 'dunit': 21, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'MINTIMEL': {'dname': 'Minimum Battery Time', 'dunit': 22, 'dtype':243, 'dsubtype':31, 'options':'1;minutes', 'Used': False, 'Image': True},
    'MAXTIME': {'dname': 'Maximum Battery Time', 'dunit': 23, 'dtype':243, 'dsubtype':31, 'options':'1;minutes', 'Used': False, 'Image': True},
    'SENSE': {'dname': 'Voltage Sense', 'dunit': 24, 'dtype':243, 'dsubtype':19, 'Used': False, 'Image': True},
    'LOTRANS': {'dname': 'Low Transfer Voltage', 'dunit': 25, 'dtype':243, 'dsubtype':8, 'options':'1;V', 'Used': True, 'Image': True},
    'HITRANS': {'dname': 'High Transfer Voltage', 'dunit': 26, 'dtype':243, 'dsubtype':8, 'options':'1;V', 'Used': True, 'Image': True},
    'NOMINV': {'dname': 'Nominal Input Voltage', 'dunit': 27, 'dtype':243, 'dsubtype':8, 'options':'1;V', 'Used': False, 'Image': True},
}

def UpdateDevice(Unit, nValue, sValue, BatteryLevel=None):
    if Unit in Devices:
        dev = Devices[Unit]
        if (dev.nValue != nValue) or (dev.sValue != str(sValue)) or (BatteryLevel is not None and dev.BatteryLevel != BatteryLevel):
            kwargs = {"nValue": nValue, "sValue": str(sValue)}
            if BatteryLevel is not None:
                kwargs["BatteryLevel"] = BatteryLevel
            if imageID != 0:
                kwargs["Image"] = imageID
            dev.Update(**kwargs)
            DebugLog(f"Device {dev.Name} updated.")

def onStart():
    global imageID
    Domoticz.Log("Domoticz APC UPS plugin started")
    _IMAGE = "UPS"
    if _IMAGE not in Images:
        Domoticz.Image(_IMAGE + ".zip").Create()
    if _IMAGE in Images:
        imageID = Images[_IMAGE].ID
    
    for key, val in values.items():
        if val['dunit'] not in Devices:
            try:
                Domoticz.Device(Name=val['dname'], Unit=val['dunit'], Type=val['dtype'],
                                Subtype=val['dsubtype'], Used=1 if val.get('Used') else 0,
                                Options=val.get('options', {}), Image=imageID if imageID != 0 else 0).Create()
            except Exception as e:
                Domoticz.Error(f"Failed to create device {val['dname']}: {e}")

    Domoticz.Heartbeat(int(Parameters["Mode1"]))

def onHeartbeat():
    path = Parameters["Mode2"]
    if not os.path.exists(path):
        Domoticz.Error(f"Fout: '{path}' niet gevonden. Pas het pad aan in de Hardware instellingen!")
        return

    try:
        res = subprocess.check_output([path, '-u', '-h', f"{Parameters['Address']}:{Parameters['Port']}"], text=True, timeout=5)
        parsed_data = {}
        for line in res.strip().split('\n'):
            key, _, val = line.partition(': ')
            parsed_data[key.strip()] = val.strip()

        raw_charge = parsed_data.get('BCHARGE', '0')
        try:
            clean_charge = ''.join(filter(lambda x: x.isdigit() or x=='.', raw_charge))
            batt_level = int(float(clean_charge))
        except:
            batt_level = 100

        for key, config in values.items():
            if key in parsed_data:
                raw_val = parsed_data[key]
                if raw_val.upper() in ('N/A', 'NONE', ''):
                    continue
                UpdateDevice(config['dunit'], 0, raw_val, BatteryLevel=batt_level)

    except subprocess.TimeoutExpired:
        Domoticz.Error("APC UPS plugin: Timeout (UPS onbereikbaar?)")
    except Exception as err:
        Domoticz.Error(f"APC UPS Error: {err}")

def onStop():
    Domoticz.Log("APC UPS Plugin gestopt.")
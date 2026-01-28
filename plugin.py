#!/usr/bin/env python
# ORIGINAL AUTHOR Joerek van Gaalen
# Modified by MadPatrick
# Version 1.3 - Added Icon support

"""
<plugin key="APCUPS" name="APC UPS" author="MadPatrick" version="1.3" externallink="https://github.com/MadPatrick/APCUPS">
    <description>
        <br/><h2>APC UPS plugin</h2>
        version: 1.3
        <br/>
        <br/>ORIGINAL AUTHOR : Joerek van Gaalen
        <br/>https://github.com/jgaalen/domoticz-apc-ups-plugin
        <br/>----------------------------------------------------------------------------------
        <br/>
        <br/><h2>= Configuration =</h2>
        <br/>
        <b style="padding-right:91px;">Address</b>: Fill in the IP address<br/>
        <b style="padding-right:115px;">Port</b>: Fill in the port address of the UPS<br/>
        <b style="padding-right:40px;">Reading Interval </b>: Time for the next refresh<br/>
        <b style="padding-right:40px;">APC access path </b>: location of the APC software<br/>
        <b style="padding-right:73px;">Debug Log </b>: do you want Debug loggig On or Off<br/>
        <br/>
        <br/>
    </description>
    <params>
        <param field="Address" label="Your APC UPS Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="40px" required="true" default="3551"/>
        <param field="Mode1" label="Reading Interval (sec)" width="40px" required="true" default="10" />
        <param field="Mode2" label="apcaccess path" width="200px" required="true" default="/sbin/apcaccess" />
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
import subprocess  # For OS calls

# Global voor de afbeelding ID
imageID = 0

# ----------------------------
# Helper functie voor debug logging
# ----------------------------
def DebugLog(message):
    if Parameters.get("Mode3") == "1":
        Domoticz.Debug(message)
        Domoticz.Log("[DEBUG] " + message)

# ----------------------------
# Values dictionary
# ----------------------------
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

# ----------------------------
# Helper functie om devices bij te werken
# ----------------------------
def UpdateDevice(Unit, nValue, sValue, BatteryLevel=None):
    if Unit in Devices:
        dev = Devices[Unit]
        update_needed = False

        if dev.nValue != nValue:
            update_needed = True
        if dev.sValue != str(sValue):
            update_needed = True
        if BatteryLevel is not None and dev.BatteryLevel != BatteryLevel:
            update_needed = True

        if update_needed:
            kwargs = {"nValue": nValue, "sValue": str(sValue)}
            if BatteryLevel is not None:
                kwargs["BatteryLevel"] = BatteryLevel
            
            # Voeg het icoon toe aan de update als het device hiervoor gemarkeerd is
            for key, val in values.items():
                if val['dunit'] == Unit and val.get('Image') and imageID != 0:
                    kwargs["Image"] = imageID

            dev.Update(**kwargs)
            DebugLog(f"Updated device {dev.Name}: {kwargs}")

# ----------------------------
# onStart functie
# ----------------------------
def onStart():
    global imageID
    Domoticz.Log("Domoticz APC UPS plugin start")
    
    # --- Icon Management ---
    _IMAGE = "UPS"
    if _IMAGE not in Images:
        Domoticz.Image(_IMAGE + ".zip").Create()
    if _IMAGE in Images:
        imageID = Images[_IMAGE].ID
        DebugLog(f"Icon pack geladen. ID: {imageID}")
    # -----------------------

    for key, val in values.items():
        iUnit = val['dunit']
        if iUnit not in Devices:
            try:
                UsedFlag = 1 if val.get('Used', True) else 0
                img = imageID if (val.get('Image') and imageID != 0) else 0
                
                Domoticz.Device(
                    Name=val['dname'],
                    Unit=iUnit,
                    Type=val['dtype'],
                    Subtype=val['dsubtype'],
                    Used=UsedFlag,
                    Options=val.get('options'),
                    Image=img
                ).Create()
                DebugLog(f"Created device {val['dname']} (Unit {iUnit})")
            except Exception as e:
                Domoticz.Error(f"Failed to create device {val['dname']}: {e}")

    Domoticz.Heartbeat(int(Parameters["Mode1"]))
    DebugLog(f"Heartbeat set to {Parameters['Mode1']} seconds")

# ----------------------------
# onHeartbeat functie
# ----------------------------
def onHeartbeat():
    DebugLog("onHeartbeat: Fetching UPS data")
    try:
        res = subprocess.check_output(
            [Parameters["Mode2"], '-u', '-h', f"{Parameters['Address']}:{Parameters['Port']}"],
            text=True
        )
        DebugLog(f"Raw UPS data received:\n{res}")

        battery_values = {}
        for line in res.strip().split('\n'):
            key, _, val = line.partition(': ')
            key = key.strip()
            val = val.strip()

            if val in ('', 'N/A', 'None'):
                battery_values[key] = ''
                DebugLog(f"{key} is empty or N/A")
                continue

            try:
                battery_values[key] = float(val)
                DebugLog(f"{key} parsed as float: {battery_values[key]}")
            except ValueError:
                battery_values[key] = val
                DebugLog(f"{key} kept as string: {val}")

        # Batterijniveau berekenen
        bcharge_val = battery_values.get('BCHARGE', -1)
        batterylevel = -1
        if bcharge_val != '' and bcharge_val != -1:
            try:
                batterylevel = int(float(bcharge_val))
            except:
                batterylevel = -1
        
        DebugLog(f"Battery level calculated: {batterylevel}")

        # Update devices en log alle veldwaarden
        for key, val in battery_values.items():
            if key in values:
                iUnit = values[key]['dunit']
                sValue = str(val) if val != '' else ''
                nValue = 0
                
                if batterylevel >= 0:
                    UpdateDevice(iUnit, nValue, sValue, BatteryLevel=batterylevel)
                else:
                    UpdateDevice(iUnit, nValue, sValue)

                DebugLog(f"Field: {key}, Value: {sValue}, Unit: {iUnit}, BatteryLevel: {batterylevel}")

    except Exception as err:
        Domoticz.Error("APC UPS Error: " + str(err))

def onStop():
    Domoticz.Log("APC UPS Plugin gestopt.")

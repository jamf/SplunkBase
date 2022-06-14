# encoding = utf-8

import json
from datetime import datetime, timedelta, timezone
import logging
import requests
import base64

import time

try:
    from uapiModels import devices, jamfpro
except:
    from .uapiModels import devices, jamfpro


# Static Variables
def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # name_of_the_modular_input = definition.parameters.get('name_of_the_modular_input', None)
    # jss_url = definition.parameters.get('jss_url', None)
    # username = definition.parameters.get('username', None)
    # password = definition.parameters.get('password', None)
    # multiple_dropdown = definition.parameters.get('multiple_dropdown', None)
    # radio_buttons = definition.parameters.get('radio_buttons', None)
    # run_time = definition.parameters.get('run_time', None)
    # write_computer_diffs = definition.parameters.get('write_computer_diffs', None)
    pass


def collect_events(helper, ew):
    """
    This is the main execution function
    """
    headers = {
        'User-Agent': 'splunkbase_ta-jamf-addon/2.10.5 modular/jamfdevices'
    }
    errors = []
    settings = {
        "jamfSettings": {
            "jssUrl": helper.get_arg('jssUrl', None),
            "jssUsername": helper.get_arg('jssUsername', None),
            "jssPassword": helper.get_arg('jssPassword', None),
        },
        "devicesCollection": {
            "details": helper.get_arg('device_collection_details', None),
            "daysSinceContact": helper.get_arg('daysSinceContact', None),
            "excludeNoneManaged": helper.get_arg('excludeNoneManaged', False),
            "platforms": helper.get_arg('platforms', None),
            "sections": helper.get_arg('sections', None)
        },
        "eventWriter": {
            "hostAsDeviceName": helper.get_arg('host_as_device_name', None),
            "eventTimeFormat": helper.get_arg('event_time_format', None)
        },
        "outbound": {
            "use_proxy": False,
            "verifyTLS": True,
            "retryCount": 3,
            "timeOut": 60
        }
    }
    # functions:

    def writeEvent(thisEvent=None):
        #
        #   This class is to help with the writing to the Splunk Event writer
        #
        #

        if "index" in thisEvent:
            index = thisEvent['index']
            del thisEvent['index']
        else:
            index = helper.get_output_index()

        if "host" in thisEvent:
            host = thisEvent['host']
            del thisEvent['host']
        else:
            host = "Jamf-TA-AddOn"

        if "sourcetype" in thisEvent:
            sourcetype = thisEvent['sourcetype']
            del thisEvent['sourcetype']
        else:
            sourcetype = "_json"

        if "time" in thisEvent:
            eventTime = thisEvent['time']
            del thisEvent['time']
        else:
            eventTime = time.time()

        if "source" in thisEvent:
            source = thisEvent['source']
            del thisEvent['source']
        else:
            source = "jssInventory"

        if index is not None:
            event = helper.new_event(data=json.dumps(thisEvent, ensure_ascii=False), source=source, time=eventTime,
                                     host=host,
                                     sourcetype=sourcetype)
        else:
            event = helper.new_event(data=json.dumps(thisEvent, ensure_ascii=False), source=source, time=eventTime,
                                     host=host,
                                     sourcetype=sourcetype)
        ew.write_event(event)
        return True

    # Jamf URL
    if str(settings['jamfSettings']['jssUrl'])[-1] != '/':
        settings['jamfSettings']['jssUrl'] = settings['jamfSettings']['jssUrl'] + '/'

    if str(settings['jamfSettings']['jssUrl']).__contains__("http://"):
        settings['jamfSettings']['jssUrl'] = settings['jamfSettings']['jssUrl'].replace("http://", "")

    if str(settings['jamfSettings']['jssUrl']).__contains__("https://"):
        settings['jamfSettings']['jssUrl'] = settings['jamfSettings']['jssUrl'].replace("https://", "")

    #
    # Functions:
    #
    jpro = jamfpro.JamfPro(jamf_url=settings['jamfSettings']['jssUrl'], jamf_username=settings['jamfSettings']['jssUsername'], jamf_password=settings['jamfSettings']['jssPassword'], helper=helper, headers=headers)
    mobile_devices = jpro.getMobileDevices()
    # Collect Computers Process each time
    
    metaChecker = devices.filterMobileDeviceMeta()
    if int(settings['devicesCollection']['daysSinceContact']) == 0:
        endEpoch = 0
    else:
        endEpoch = int(str(time.time()).split(".")[0]) - int(settings['devicesCollection']['daysSinceContact']) * 86400

    #endEpoch = 0
    
    countProcess = 0
    
    countPass = 0
    
    for mobile_device in mobile_devices:
        process, reason = metaChecker.keepDevice(deviceMeta=mobile_device,
                                     endEpoch=endEpoch,
                                     excludeNoneManaged=settings['devicesCollection']['excludeNoneManaged'],
                                     platformIn=settings['devicesCollection']['platforms'])
        if process:
            try:
                deviceDetails = jpro.getMobileDevicesDetails(id=mobile_device['id'], apiVersion="JSSResource")
                thisDevice = devices.mobileDeviceJSSResource(uapiModel=deviceDetails['mobile_device'])
                events = thisDevice.getSplunkEvents(sections=settings['devicesCollection']['sections'], buildings={}, departments={})
                for event in events:
                    writeEvent(thisEvent=event)
                countProcess += 1
            except Exception as e:
                errors.append(f"Error with Device {str(e)}")
        else:
            countPass += 1

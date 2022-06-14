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
        'User-Agent': 'splunkbase_ta-jamf-addon/2.10.5 modular/jamfcomputers'
    }
    errors = []
    errors = []
    settings = {
        "jamfSettings": {
            "jssUrl": helper.get_arg('jss_url', None),
            "jssUsername": helper.get_arg('jss_username', None),
            "jssPassword": helper.get_arg('jss_password', None),
        },
        "computerCollection": {
            "details": helper.get_arg('computer_collection_details', None),
            "daysSinceContact": helper.get_arg('days_since_contact', None),
            "excludeNoneManaged": helper.get_arg('excludeNoneManaged', None),
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
    # Clean Up Checks

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

    def writeEvent(thisEvent=None):
        """
        """
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
                                     index=index,
                                     host=host,
                                     sourcetype=sourcetype)
        else:
            event = helper.new_event(data=json.dumps(thisEvent, ensure_ascii=False), source=source, time=eventTime,
                                     host=host,
                                     sourcetype=sourcetype)
        ew.write_event(event)
        return True

    def getComputersPage(pageNumber=0, jss=None):

        FILTERS = {}
        if settings['computerCollection']['excludeNoneManaged']:
            FILTERS['managed'] = {'value': True}
        if settings['computerCollection']['daysSinceContact'] != str(0):
            try:
                time_s = datetime.now(timezone.utc) - timedelta(
                    days=int(settings['computerCollection']['daysSinceContact']))
                FILTERS['lastContactTime'] = {
                    'value': time_s.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'operator': '>'
                }
            except:
                helper.log_error("Error applying filter=daysSinceContact with value=%s please check TA configuration and ensure that daysSinceContact is configured with a positive integer value" % settings['computerCollection']['daysSinceContact'])

        sections = settings['computerCollection']['sections']

        requiredSections = ['GENERAL', 'USER_AND_LOCATION', 'HARDWARE']

        for requiredSection in requiredSections:
            if requiredSection not in sections:
                sections.append(requiredSection)

        computers = jss.getComputersPageNumber(filters=FILTERS, sections=sections,
                                               sortKey="&sort=general.reportDate%3Adesc", pageNumber=pageNumber)
        return computers
        pass

    # Collect Computers Process each time
    notDone = True
    pageCount = 0
    meta_keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user', 'department',
                 'building', 'room', 'eventID', 'reportDate']

    if settings['eventWriter']['eventTimeFormat'] == "timeAsScript":
        timeAs = "script"
    if settings['eventWriter']['eventTimeFormat'] == "timeAsReport":
        timeAs = "report"

    jamfPro = jamfpro.JamfPro(jamf_url=settings['jamfSettings']['jssUrl'],
                                jamf_username=settings['jamfSettings']['jssUsername'],
                                jamf_password=settings['jamfSettings']['jssPassword'],
                                helper=helper, headers=headers)

    while notDone:
        theseComputers = getComputersPage(pageNumber=pageCount, jss=jamfPro)
        if theseComputers.__len__() == 0:
            return None
        else:
            pageCount += 1
            for computer in theseComputers:
                try:
                    newComputer = devices.JamfComputer(computerDetails=computer, source="uapi")
                    events = newComputer.splunk_hec_events(meta_keys=meta_keys,
                                                           nameAsHost=settings['eventWriter']['hostAsDeviceName'],
                                                           timeAs=timeAs)

                    for event in events:
                        writeEvent(event)
                except:
                    error_event = {
                        "messages": "An error occured while processing a computer",
                        "jss_id": computer['id'],
                        "jss": settings['jamfSettings']['jssUrl'],
                        "sourcetype": "jamf:jssInventory:errorCode"
                    }

                    helper.log_error("An error occured while processing a jamf computer object with jss_id=%s from jss_url=%s" % (computer['id'], settings['jamfSettings']['jssUrl']))

import copy
import json
import time
from abc import ABC, abstractmethod
import uuid
import datetime

class mobileDevice():

    def __init__(self, uapiModel:dict):
        self.device = uapiModel
        print(json.dumps(self.device, indent=2))

    def buildMeta(self, buildings={}, departments={}):
        meta_keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user', 'department',
                     'building', 'room', 'eventID', 'reportDate']
        ioskeys = [
            {
                'name': 'managed',
                'location': 'general:managed'
            },{
                'name': 'name',
                'location': 'general:device_name'
            },{
                'name': 'serial_number',
                'location': 'general:serial_number'
            },{
                'name': 'udid',
                'location': 'general:udid'
            },{
                'name': 'id',
                'location': 'general:id'
            },{
                'name': 'assigned_user',
                'location': 'location:username'
            },{
                'name': 'reportDateEpoch',
                'location': 'general:last_inventory_update_epoch'
            },{
                'name': 'site',
                'location': 'general:site:name'
            },{
                'name': 'deviceType',
                'location': 'type'
            },{
                'name': 'platform',
                'location': 'general:os_type'
            }
        ]

        metaDef = {}
        for ioskey in ioskeys:
            split = ioskey['location'].split(":")
            if split.__len__() == 1:
                metaDef[ioskey['name']] = self.device[split[0]]
            if split.__len__() == 2:
                metaDef[ioskey['name']] = self.device[split[0]][split[1]]
            if split.__len__() == 3:
                metaDef[ioskey['name']] = self.device[split[0]][split[1]][split[2]]

        # Building and Department ID Conversion

        if self.device['location']['departmentId'] is not None:
            metaDef['department'] = departments[self.device['location']['departmentId']]
        else:
            metaDef['department'] = "None"

        if self.device['location']['buildingId'] is not None:
            metaDef['building'] = departments[self.device['location']['buildingId']]
        else:
            metaDef['building'] = "None"
        return metaDef

    def getSplunkEvents(self, sections:list, buildings:dict, departments:dict):
        thisMeta = self.buildMeta(buildings, departments)
        if thisMeta['deviceType'] == "ios":
            evnets = self._getSplunkEventsiOS(sections)

        if thisMeta['deviceType'] == "tvos":
            evnets = self._getSplunkEventstvOS(sections)

    def _getSplunkEventstvOS(self, sections):
        events = []
        print("ios events")
        return events

    def _getSplunkEventsiOS(self, sections):
        events = []
        print("tvos events")
        return events


class mobileDeviceJSSResource():
    eventId = str(uuid.uuid4())
    def __init__(self, uapiModel: dict):
        self.device = uapiModel
        self.eventId = str(uuid.uuid4())

    def buildMeta(self, buildings={}, departments={}):
        meta_keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user', 'department',
                     'building', 'room', 'eventID', 'reportDate']
        ioskeys = [
            {
                'name': 'managed',
                'location': 'general:managed'
            }, {
                'name': 'name',
                'location': 'general:device_name'
            }, {
                'name': 'serial_number',
                'location': 'general:serial_number'
            }, {
                'name': 'udid',
                'location': 'general:udid'
            }, {
                'name': 'id',
                'location': 'general:id'
            }, {
                'name': 'assigned_user',
                'location': 'location:username'
            }, {
                'name': 'reportDateEpoch',
                'location': 'general:last_inventory_update_epoch'
            }, {
                'name': 'site',
                'location': 'general:site:name'
            },{
                'name': 'platform',
                'location': 'general:os_type'
            },{
                'name': 'department',
                'location': 'location:department'
            },{
                'name': 'building',
                'location': 'location:building'
            }
        ]

        metaDef = {}
        for ioskey in ioskeys:
            split = ioskey['location'].split(":")
            if split.__len__() == 1:
                metaDef[ioskey['name']] = self.device[split[0]]
            if split.__len__() == 2:
                metaDef[ioskey['name']] = self.device[split[0]][split[1]]
            if split.__len__() == 3:
                metaDef[ioskey['name']] = self.device[split[0]][split[1]][split[2]]
        metaDef['eventId'] = self.eventId
        return metaDef

    def getSplunkEvents(self, sections: list, buildings: dict, departments: dict):
        thisMeta = self.buildMeta(buildings, departments)

        thisDevice = copy.deepcopy(self.device)

        events = []
        # General
        if 'general' in sections:
            newEvent = {
                'general': thisDevice['general'],
                'sourcetype': "jssMobileDevice:general",
                'deviceMeta': thisMeta,
                'host': thisMeta['name']
            }
            events.append(copy.deepcopy(newEvent))
        # Location
        if 'location' in sections:
            newEvent = {
                'location': thisDevice['location'],
                'sourcetype': "jssMobileDevice:location",
                'deviceMeta': thisMeta,
                'host': thisMeta['name']
            }
            events.append(copy.deepcopy(newEvent))
        # Purchasing
        if 'purchasing' in sections:
            newEvent = {
                'purchasing': thisDevice['purchasing'],
                'sourcetype': "jssMobileDevice:purchasing",
                'deviceMeta': thisMeta,
                'host': thisMeta['name']

            }
            events.append(copy.deepcopy(newEvent))
        # Applications
        if "applications" in thisDevice:
            for application in thisDevice['applications']:
                newEvent = {
                    'application': application,
                    'sourcetype': "jssMobileDevice:application",
                    'deviceMeta': thisMeta,
                    'host': thisMeta['name']
                }
                events.append(copy.deepcopy(newEvent))
        # Security
        if 'security' in sections:
            newEvent = {
                'security': thisDevice['security'],
                'sourcetype': "jssMobileDevice:security",
                'deviceMeta': thisMeta,
                'host': thisMeta['name']
            }
            events.append(copy.deepcopy(newEvent))
        # Network
        if 'network' in sections:
            newEvent = {
                'network': thisDevice['network'],
                'sourcetype': "jssMobileDevice:network",
                'deviceMeta': thisMeta,
                'host': thisMeta['name']
            }
            events.append(copy.deepcopy(newEvent))
        # Certificates
        if 'certificates':
            for certificate in thisDevice['certificates']:
                newEvent = {
                    'mobileDeviceCertificate': certificate,
                    'sourcetype': "jssMobileDevice:certificate",
                    'deviceMeta': thisMeta,
                    'host': thisMeta['name']
                }
                events.append(copy.deepcopy(newEvent))
        # Configuration Profiles
        if 'configuration_profiles' in thisDevice:
            for certificate in thisDevice['configuration_profiles']:
                newEvent = {
                    'mobileDeviceConfigProfile': certificate,
                    'sourcetype': "jssMobileDevice:configurationProfile",
                    'deviceMeta': thisMeta,
                    'host': thisMeta['name']
                }
                events.append(copy.deepcopy(newEvent))
        # Provisioning Profiles
        if "provisioning_profiles" in thisDevice:
            for certificate in thisDevice['provisioning_profiles']:
                newEvent = {
                    'mobileDeviceProvisioningProfile': certificate,
                    'sourcetype': "jssMobileDevice:provisioningProfile",
                    'deviceMeta': thisMeta,
                    'host': thisMeta['name']
                }
                events.append(copy.deepcopy(newEvent))
        # Mobile Device Groups
        if "mobile_device_groups" in thisDevice:
            for group in thisDevice['mobile_device_groups']:
                newEvent = {
                    'mobileDeviceGroup': group,
                    'sourcetype': "jssMobileDevice:deviceGroup",
                    'deviceMeta': thisMeta,
                    'host': thisMeta['name']
                }
                events.append(copy.deepcopy(newEvent))
        # Extension Attributes
        if "extension_attributes" in thisDevice:
            for ea in thisDevice['extension_attributes']:
                newEvent = {
                    'mobileDeviceEA': ea,
                    'sourcetype': "jssMobileDevice:extensionAttribute",
                    'deviceMeta': thisMeta,
                    'host': thisMeta['name']
                }
                events.append(copy.deepcopy(newEvent))
        return events

class filterMobileDeviceMeta():

    def __init__(self):
        pass

    def keepDevice(self, deviceMeta={},
                   endEpoch=0,
                   excludeNoneManaged= False,
                   platformIn=["iphone", "ipad","ipod","appletv","other"]
                   ) -> (bool, str):

        if excludeNoneManaged:
            if not self._excludeManaged(deviceMeta):
                return False, "not manaaged"


        if not self._platFormIn(deviceMeta, platformIn):
            return False, "not in platform type"

        if not self._daysSinceContact(deviceMeta, endEpoch):
            return False, "outside collection window"

        return True, ""

    def _excludeManaged(self, device: dict):
        if device['managed']:
            return True
        else:
            return False

    def _platFormIn(self, device: dict, platformList: list):
        devicePlatform = device['model_identifier'].lower()
        for platform in platformList:
            if devicePlatform.__contains__(platform):
                return True
        if 'other' in platformList:
            return True
        return False

    def _daysSinceContact(self, device:dict, endEpoch:int):
        if endEpoch == 0:
            return True
        else:
            return int(device['last_inventory_update_epoch']/1000) > endEpoch



class device(ABC):
    @abstractmethod
    def set_from_uapi(self, details):
        pass

    @abstractmethod
    def splunk_hec_events(self):
        pass


class JamfComputer(device):
    """
    This is a model for a Jamf Computer
    """
    details = {}
    computer_meta = {}

    def __init__(self, computerDetails={}, source="uapi"):
        """
        Init function:
        :param computerDetails: Dictionary or XML of computer from JSS API
        :param source: UAPI
        """
        self.details = {}
        self.computer_meta = {}
        if computerDetails != {} and source == "uapi":
            self.set_from_uapi(details=computerDetails)

    def set_from_uapi(self, details):
        self.details = details
        self.computer_meta = self.get_computer_meta()

    def splunk_hec_events(self, meta_keys=[], nameAsHost=True, timeAs="report"):
        thisDevice = self.details.copy()
        baseSourceType = "jssUapiComputer"
        del_keys = ['fonts', 'services', 'packageReceipts', 'contentCaching', 'ibeacons', 'plugins', 'attachments']


        computer_meta = self.__build_splunk_meta(meta_keys=meta_keys)

        baseEvent = self.__extract_base_event(computer=thisDevice,
                                              timeAs=timeAs,
                                              nameAsHost=nameAsHost,
                                              source="jss_inventory")

        for key in del_keys:
            if key in thisDevice:
                del thisDevice[key]

        splunk_events = []

        # Extension Attributes
        eas, thisDevice = self.__extract_EAs(computer=thisDevice)

        for ea in eas:
            event = {
                'extensionAttribute': ea,
                'computer_meta': computer_meta,
                'sourcetype': f'{baseSourceType}:extensionAttribute'
            }
            splunk_events.append(event)

        # Applications
        if thisDevice['applications'] is not None:
            apps = self.__extract_applications(computer=thisDevice)
            del thisDevice['applications']
            for app in apps:
                event = {
                    'app': app,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:app'
                }
                splunk_events.append(event)
        else:
            del thisDevice['applications']

        # Configuration Profiles
        if thisDevice['configurationProfiles'] is not None:
            configProfiles = self.__extract_configProfiles(computer=thisDevice)
            del thisDevice['configurationProfiles']
            for configProfile in configProfiles:
                event = {
                    'configProfile': configProfile,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:configProfile'
                }
                splunk_events.append(event)
        else:
            del thisDevice['configurationProfiles']

        # Local User Accounts
        if thisDevice['localUserAccounts'] is not None:
            localAccounts = self.__extract_local_accounts(computer=thisDevice)
            del thisDevice['localUserAccounts']
            for localAccount in localAccounts:
                event = {
                    'localAccount': localAccount,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:localAccount'
                }
                splunk_events.append(event)
        else:
            del thisDevice['localUserAccounts']

        # Groups
        if thisDevice['groupMemberships'] is not None:
            groupMemberships = self.__extract_groups(computer=thisDevice)
            del thisDevice['groupMemberships']
            for groupMembership in groupMemberships:
                event = {
                    'groupMembership': groupMembership,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:groupMembership'
                }
                splunk_events.append(event)
        else:
            del thisDevice['groupMemberships']
        # Certificates

        if thisDevice['certificates'] is not None:
            certificates = self.__extract_certificates(computer=thisDevice)
            del thisDevice['certificates']
            for certificate in certificates:
                event = {
                    'certificate': certificate,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:certificate'
                }
                splunk_events.append(event)
        else:
            del thisDevice['certificates']

        # Storage Drives
        if thisDevice['storage'] is not None:
            partitions = self.__extract_storage(computer=thisDevice)
            del thisDevice['storage']
            for partition in partitions:
                event = {
                    'diskPartition': partition,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:diskPart'
                }
                splunk_events.append(event)
        else:
            del thisDevice['storage']

        # Printers
        if thisDevice['printers'] is not None:
            printers = self.__extract_printers(computer=thisDevice)
            del thisDevice['printers']

            for printer in printers:
                event = {
                    'printer': printer,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:printer'
                }
                splunk_events.append(event)
        else:
            del thisDevice['printers']

        # Licensed Software
        if thisDevice['licensedSoftware'] is not None:
            licensedSoftware = self.__extract_licensed_software(computer=thisDevice)
            del thisDevice['licensedSoftware']

            for licensedSoftwareTitle in licensedSoftware:
                event = {
                    'licensedSoftware': licensedSoftwareTitle,
                    'computer_meta': computer_meta,
                    'sourcetype': f'{baseSourceType}:licensedSoftwareTitle'
                }
                splunk_events.append(event)
        else:
            del thisDevice['licensedSoftware']
        # Final Processing

        ## General
        if thisDevice['general'] is not None:
            event = {
                "computerGeneral": thisDevice['general'],
                'computer_meta': computer_meta,
                'sourcetype': f'{baseSourceType}:computerGeneral'
            }
            del thisDevice['general']
            splunk_events.append(event)
        else:
            del thisDevice['general']

        ## DiskEncryption
        if thisDevice['diskEncryption'] is not None:
            event = {
                "computerDiskEncryption": thisDevice['diskEncryption'],
                'computer_meta': computer_meta,
                'sourcetype': f'{baseSourceType}:diskEncryption'
            }
            del thisDevice['diskEncryption']
            splunk_events.append(event)
        else:
            del thisDevice['diskEncryption']

        ## Purchasing
        if thisDevice['purchasing'] is not None:
            event = {
                'purchasing': thisDevice['purchasing'],
                'computer_meta': computer_meta,
                'sourcetype': f'{baseSourceType}:purchasing'
            }
            del thisDevice['purchasing']
            splunk_events.append(event)
        else:
            del thisDevice['purchasing']

        ## userAndLocation
        if thisDevice['userAndLocation'] is not None:
            event = {
                'userAndLocation': thisDevice['userAndLocation'],
                'computer_meta': computer_meta,
                'sourcetype': f'{baseSourceType}:userAndLocation'
            }
            del thisDevice['userAndLocation']
            splunk_events.append(event)
        else:
            del thisDevice['userAndLocation']

        ## hardware
        if thisDevice['hardware'] is not None:
            event = {
                "computerHardware": thisDevice['hardware'],
                "computer_meta": computer_meta,
                'sourcetype': f'{baseSourceType}:computerHardware'
            }
            del thisDevice['hardware']
            splunk_events.append(event)
        else:
            del thisDevice['hardware']

        ## security
        if thisDevice['security'] is not None:
            event = {
                "computerSecurity": thisDevice['security'],
                "computer_meta": computer_meta,
                'sourcetype': f'{baseSourceType}:computerSecurity'
            }
            del thisDevice['security']
            splunk_events.append(event)
        else:
            del thisDevice['security']

        ## operatingSystem
        if thisDevice['operatingSystem'] is not None:
            event = {
                'computerOS': thisDevice['operatingSystem'],
                "computer_meta": computer_meta,
                'sourcetype': f'{baseSourceType}:operatingSystem'
            }
            del thisDevice['operatingSystem']
            splunk_events.append(event)
        else:
            del thisDevice['operatingSystem']

        if thisDevice['softwareUpdates'] is not None:
            ## softwareUpdates
            event = {
                'computerSoftwareUpdates': thisDevice['softwareUpdates'],
                'computer_meta': computer_meta,
                'sourcetype': f'{baseSourceType}:softwareUpdates'
            }
            del thisDevice['softwareUpdates']
            splunk_events.append(event)
        else:
            del thisDevice['softwareUpdates']

        # Final Cleanup
        del thisDevice
        final_events = []
        for event in splunk_events:
            for key in baseEvent:
                if key not in event:
                    event[key] = baseEvent[key]
            final_events.append(event)
            pass
        return final_events

    def get_computer_meta(self):
        """
        Returns the Computer Meta
        :return:
        """
        # ToDo Set this up to be configurable
        keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user', 'department',
                'building', 'room', 'eventID', 'reportDate']
        meta = self.__build_splunk_meta(meta_keys=keys)

        if 'lastContactTime' in self.details['general']:
            if self.details['general']['lastContactTime']:
                try:
                    time = datetime.datetime.strptime(self.details['general']['lastContactTime'],
                                                      "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                        tzinfo=datetime.timezone.utc)
                except:
                    time = datetime.datetime.strptime(self.details['general']['lastContactTime'],
                                                      "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=datetime.timezone.utc)
                meta['lastContactEpoch'] = time.timestamp()

        if 'reportDate' in self.details['general']:
            if self.details['general']['reportDate']:
                try:
                    time = datetime.datetime.strptime(self.details['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                        tzinfo=datetime.timezone.utc)
                except ValueError:
                    time = datetime.datetime.strptime(self.details['general']['reportDate'], "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=datetime.timezone.utc)
                meta['lastReportEpoch'] = time.timestamp()

        return meta

    def __extract_contact_event(self, computer):
        time = datetime.datetime.strptime(computer['general']['lastContactTime'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=datetime.timezone.utc)
        event = {
            "source": "jssContact",
            "time": time.timestamp(),
            "event": "Device Contact Jamf Pro Server"
        }

        return event

    def __extract_base_event(self, computer, timeAs, nameAsHost, source):
        base_event = {
            'source': source,
        }
        if nameAsHost:
            base_event['host'] = computer['general']['name']
        if timeAs == "report":
            try:
                eventTime = datetime.datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                    tzinfo=datetime.timezone.utc)
            except ValueError:
                eventTime = datetime.datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=datetime.timezone.utc)
            base_event['time'] = eventTime.timestamp()
        if timeAs == "contact":
            try:
                eventTime = datetime.datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                    tzinfo=datetime.timezone.utc)
            except ValueError:
                eventTime = datetime.datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=datetime.timezone.utc)
            base_event['time'] = eventTime.time()
        if timeAs == "script":
            base_event['time'] = time.time()
        return base_event

    def __extract_applications(self, computer):
        applications = computer['applications']
        delete_keys = ['sizeMegabytes', 'externalVersionId', 'updateAvailable']
        parsed_app_l = []
        for app in applications:
            for delete_key in delete_keys:
                if delete_key in app:
                    del app[delete_key]

            parsed_app_l.append(app)

        return parsed_app_l

    def __extract_printers(self, computer):
        printers = computer['printers']
        delete_keys = []
        parsed_printers_l = []
        for printer in printers:
            for delete_key in delete_keys:
                if delete_key in printer:
                    del printer[delete_key]

            parsed_printers_l.append(printer)

        return parsed_printers_l

    def __extract_licensed_software(self, computer):
        softwareTitle = computer['licensedSoftware']
        delete_keys = []
        parsed_titles_l = []
        for title in softwareTitle:
            for delete_key in delete_keys:
                if delete_key in title:
                    del title[delete_key]

            parsed_titles_l.append(title)

        return parsed_titles_l

    def __extract_configProfiles(self, computer):
        config_profiles = computer['configurationProfiles']
        del_keys = ["profileIdentifier", ]
        config_profile_l = []
        if config_profiles is None:
            return config_profile_l

        for config_profile in config_profiles:
            # Delete Keys not needed
            for key in del_keys:
                if key in config_profile:
                    del config_profile[key]

            config_profile_l.append(config_profile)

        return config_profile_l

    def __extract_certificates(self, computer):
        certificates = computer['certificates']
        del_keys = []
        certificates_l = []
        for cert in certificates:
            # Delete Keys not needed
            for key in del_keys:
                if key in cert:
                    del cert[key]

            certificates_l.append(cert)

        return certificates_l

    def __extract_EAs(self, computer):
        ea_sub_keys = ['purchasing', 'general', 'userAndLocation', 'hardware', 'operatingSystem']
        del_keys = ['options', 'inputType', 'multiValue']
        extension_attribute_l = []
        for ea_key in ea_sub_keys:
            if computer[ea_key] is not None:
                for EA in computer[ea_key]['extensionAttributes']:
                    if EA['multiValue'] == False and EA['values'].__len__() == 1:
                        EA['value'] = EA['values'][0]
                        del EA['values']
                    for key in del_keys:
                        if key in EA:
                            del EA[key]
                    extension_attribute_l.append(EA)
                del computer[ea_key]['extensionAttributes']

        if computer['extensionAttributes'] is not None:
            for EA in computer['extensionAttributes']:
                if EA['multiValue'] == False and EA['values'].__len__() == 1:
                    EA['value'] = EA['values'][0]
                    del EA['values']
                for key in del_keys:
                    if key in EA:
                        del EA[key]
                extension_attribute_l.append(EA)
        del computer['extensionAttributes']
        return extension_attribute_l, computer

    def __extract_groups(self, computer):
        groups = computer['groupMemberships']
        delete_keys = ['']
        parsed_groups_l = []
        for group in groups:
            for delete_key in delete_keys:
                if delete_key in group:
                    del group[delete_key]

            parsed_groups_l.append(group)

        return parsed_groups_l

    def __extract_local_accounts(self, computer):
        localAccounts = computer['localUserAccounts']
        delete_keys = ['']
        parsed_accounts_l = []
        for localAccount in localAccounts:
            for delete_key in delete_keys:
                if delete_key in localAccount:
                    del localAccount[delete_key]

            parsed_accounts_l.append(localAccount)

        return parsed_accounts_l

    def __extract_storage(self, computer):
        disks = computer['storage']['disks']
        partitions_l = []
        for disk in disks:
            keys = disk.keys()
            keys_l = []
            for key in keys:
                if key != "partitions":
                    keys_l.append(key)
            for partition in disk['partitions']:
                for key in keys_l:
                    partition[key] = disk[key]
                partitions_l.append(partition)
        return partitions_l

    def __build_splunk_meta(self, meta_keys=[]):

        keys = meta_keys.copy()
        computer_meta = {}
        if 'supervised' in keys:
            computer_meta['supervised'] = self.details['general']['supervised']
        if 'managed' in keys:
            computer_meta['managed'] = self.details['general']['remoteManagement']['managed']
        if 'name' in keys:
            computer_meta['name'] = self.details['general']['name']
        if 'serial_number' in keys:
            computer_meta['serial'] = self.details['hardware']['serialNumber']
        if 'udid' in keys:
            computer_meta['udid'] = self.details['udid']
        if 'id' in keys:
            computer_meta['id'] = self.details['id']
        if 'assigned_user' in keys:
            computer_meta['assignedUser'] = self.details['userAndLocation']['username']
        if 'reportDate' in keys:
            computer_meta['reportDate'] = self.details['general']['reportDate']
        if 'department' in keys:
            pass
        if 'building' in keys:
            pass
        if 'room' in keys:
            pass

        if 'eventID' in keys:
            computer_meta['eventID'] = str(uuid.uuid4())
        """
        Splunk Specific values
        """
        # Time
        if 'timeAsReport' in keys:
            pass

        if 'timeAsContact' in keys:
            # Write Splunks Time Values
            pass

        return computer_meta

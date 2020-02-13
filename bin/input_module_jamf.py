
# encoding = utf-8

import os
import sys
import time
import datetime
import requests
import json
import math
from splunklib.modularinput import *
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
import uuid
import time


'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # name_of_the_modular_input = definition.parameters.get('name_of_the_modular_input', None)
    # jss_url = definition.parameters.get('jss_url', None)
    # api_call = definition.parameters.get('api_call', None)
    # search_name = definition.parameters.get('search_name', None)
    # custom_index_name = definition.parameters.get('custom_index_name', None)
    # custom_host_name = definition.parameters.get('custom_host_name', None)
    # username = definition.parameters.get('username', None)
    # password = definition.parameters.get('password', None)
    pass

def collect_events(helper, ew):
    name_of_the_modular_input = helper.get_arg('name_of_the_modular_input', None)
    url = helper.get_arg('jss_url', None)
    api_call = helper.get_arg('api_call', None)
    search_name = helper.get_arg('search_name', None)
    username = helper.get_arg('username',None)
    password = helper.get_arg('password',None)
    index = helper.get_arg('custom_index_name','main')
    host = helper.get_arg('custom_host_name','localhost')
    maxCharLength = 10000
    call_uuid = uuid.uuid4()
    
    #
    #   Verify JSS URL
    #
    if url.__contains__("http://"):
        url = url.replace("http://","")
    if url.__contains__("https://"):
        url = url.replace("https://","")
    if not url.endswith("/"):
        url = url + "/"
    url = "https://" + url
    
    
    def writeComputerDevice (DATA): 
        #
        #   List of things that will be written by themselves
        #
        chunk_list = list()
        chunk_list.append("computer_groups")
        chunk_list.append("configuration_profiles")
        chunk_list.append("software")
        chunk_list.append("extension_attributes")
        chunk_list.append("hardware")
        chunk_list.append("running_services")
        chunk_list.append("certificates")
        chunk_list.append("location")
        chunk_list.append("purchasing")
        chunk_list.append("groups_accounts")
        chunk_list.append("general")
        
        computer = ElementTree.fromstring(DATA)
        
        self = ElementTree.Element("self")
        gen = computer.find("general")
        #inventory_time =int(int(gen.find("report_date_epoch").text)/1000.)
        inventory_time = time.strftime('%Y-%m-%d %H:%M:%S',  time.gmtime(int(gen.find("report_date_epoch").text)/1000.))
        jss_id = gen.find("id").text
        ElementTree.SubElement(self, 'inventory_time').text = inventory_time
        ElementTree.SubElement(self, 'id').text = jss_id
        ElementTree.SubElement(self, 'link').text = url+"JSSResource/computerdevices/"+jss_id
        ElementTree.SubElement(self, 'udid').text = gen.find('udid').text
        pagination = ElementTree.Element("pagination")  
        
        
        for keyValue in chunk_list:
            
            if computer.find(keyValue):

                    
                #
                #   Split Running Services Off
                #
                
                keyXML = computer.find(keyValue)
                
                # Get the lenght of the string representation of the XML document
                key_char_length = ElementTree.tostring(keyXML).__len__()
                if key_char_length < maxCharLength:
                    #
                    #   If this is under 10k just go ahead and write to the event reader
                    #
                    root = ElementTree.Element("computer")
                    
                    chunk_ID = str(uuid.uuid4())
                    chunk_uuid = ElementTree.Element("sub_pagination")
                    ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                    ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(1)
                    ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(1)
                    root.append(chunk_uuid)
                    pagination.append(chunk_uuid)
                    root.append(keyXML)
                    root.append(self)

                    writeStringTo_Event( ElementTree.tostring(root) )
                else:
                    #
                    #   This is the area for if the already seperated XML is still too large. It will take the Length and use MOD to give the number of XML files it would need to be cut into. I add an additional one just in c
                    #
                    
                    
                    chunk_ID = str(uuid.uuid4())
                    num_XML = math.ceil(key_char_length / maxCharLength) + 1
                    #
                    #   Create an array of XML documents
                    #
                    
                    if keyValue == "software":
                    #
                    #   Remove Running Services
                    #
                        remove_from_software = list()
                        remove_from_software.append("unix_executables")
                        remove_from_software.append("installed_by_casper")
                        remove_from_software.append("installed_by_installer_swu")
                        remove_from_software.append("cached_by_casper")
                        remove_from_software.append("available_software_updates")
                        remove_from_software.append("available_updates")
                        remove_from_software.append("fonts")
                        chunk_from_software = list()
                        
                        chunk_from_software.append('chunk_from_software')
                        chunk_from_software.append('applications')
                        chunk_from_software.append('running_services')
                        
                        for remove in remove_from_software:
                            if keyXML.find(remove):
                                keyXML.remove((keyXML.find(remove)))
                        
                        
                        run_service = keyXML.find("running_services")
                        run_serv_lengt = ElementTree.tostring(run_service).__len__()
                        run_serv_count = math.ceil(run_serv_lengt / maxCharLength) + 2
                        root_list = []
                        for i in range(0, int(run_serv_count)):
                            run_root = ElementTree.Element("running_services")
                            root_list.append(run_root)
                        #
                        #   Get a list of the 1st level children in the XML document keeping the same structure
                        #
        
                        #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                        key_chield = run_service.getchildren()
                        i = 0
                        for child in key_chield:
                            # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                            root_list[int(math.fmod(i, run_serv_count))].append(child)
                            i = i + 1
                        #
                        #   Iterate through the finished XML documents and write to the event writer.
                        #
        
                        for fin_xml in root_list:
                            root = ElementTree.Element("computer")
                            gen = computer.find("general")
                            jss_id = gen.find("id").text
                            ElementTree.SubElement(root, 'id').text = jss_id
        
                            root.append(fin_xml)
                            chunk_uuid = ElementTree.Element("sub_pagination")
                            ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                            ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i)
                            ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(root_list.__len__())
                            root.append(chunk_uuid)
                            #writeStringTo_Event( ElementTree.tostring(root) )
                            writeStringTo_Event_wTime( ElementTree.tostring(root), inventory_time )
                        chunk_uuid = ElementTree.Element("sub_pagination")
                        ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                        ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i)
                        ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(root_list.__len__())
                        pagination.append(chunk_uuid)
                        
                        keyXML.remove(run_service)
                    #
                    #   End Removing Running Services
                    #
                    
                    
                    
                    root_list = []
                    for i in range(0, int(num_XML)):
                        root = ElementTree.Element(keyValue)
                        root_list.append(root)
                    #
                    #   Get a list of the 1st level children in the XML document keeping the same structure
                    #
    
                    #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                    key_chield = keyXML.getchildren()
                    i = 0
                    for child in key_chield:
                        # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                        root_list[int(math.fmod(i, num_XML))].append(child)
                        i = i + 1
                    #
                    #   Iterate through the finished XML documents and write to the event writer.
                    #
    
                    for fin_xml in root_list:
                        root = ElementTree.Element("computer")
                        gen = computer.find("general")
                        jss_id = gen.find("id").text
                        ElementTree.SubElement(root, 'id').text = jss_id

                        root.append(fin_xml)
                        chunk_uuid = ElementTree.Element("sub_pagination")
                        ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID

                        root.append(chunk_uuid)
                        #writeStringTo_Event( ElementTree.tostring(root) )
                        writeStringTo_Event_wTime( ElementTree.tostring(root), inventory_time )
                    chunk_uuid = ElementTree.Element("sub_pagination")
                    ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID

                    pagination.append(chunk_uuid)
                    

                #
                #   Remove the Key Index field from the XML
                #
                
                computer.remove(keyXML)
        #
        # What's Left
        #
        self.append(pagination)
        computer.append(self)
        #writeStringTo_Event( ElementTree.tostring(computer) )
        writeStringTo_Event_wTime( ElementTree.tostring(computer), inventory_time )
    #
    #   Done with Parsing computer Devices
    #
    
    
    def writeMobileDevice (DATA): 
        #
        #   List of things that will be written by themselves
        #
        chunk_list = list()
        chunk_list.append("mobile_device_groups")
        chunk_list.append("configuration_profiles")
        chunk_list.append("applications")
        chunk_list.append("extension_attributes")
        
        mobile_device = ElementTree.fromstring(DATA)
        self = ElementTree.Element("self")
        gen = mobile_device.find("general")
        jss_id = gen.find("id").text
        ElementTree.SubElement(self, 'id').text = jss_id
        ElementTree.SubElement(self, 'link').text = url+"/JSSResource/mobiledevices/"+jss_id
        pagination = ElementTree.Element("pagination")  
    
        
        for keyValue in chunk_list:

            if mobile_device.find(keyValue):
                keyXML = mobile_device.find(keyValue)
                # Get the lenght of the string representation of the XML document
                key_char_length = ElementTree.tostring(keyXML).__len__()
                if key_char_length < maxCharLength:
                    #
                    #   If this is under 10k just go ahead and write to the event reader
                    #
                    root = ElementTree.Element("mobile_device")
                    
                    chunk_ID = str(uuid.uuid4())
                    chunk_uuid = ElementTree.Element("sub_pagination")
                    ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                    ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(1)
                    ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(1)
                    root.append(chunk_uuid)
                    pagination.append(chunk_uuid)
                    root.append(keyXML)
                    root.append(self)

                    writeStringTo_Event( ElementTree.tostring(root) )
                else:
                    #
                    #   This is the area for if the already seperated XML is still too large. It will take the Length and use MOD to give the number of XML files it would need to be cut into. I add an additional one just in c
                    #
                    chunk_ID = str(uuid.uuid4())
                    num_XML = math.ceil(key_char_length / maxCharLength) + 1
                    #
                    #   Create an array of XML documents
                    #
                    root_list = []
                    for i in range(0, int(num_XML)):
                        root = ElementTree.Element(keyValue)
                        root_list.append(root)
                    #
                    #   Get a list of the 1st level children in the XML document keeping the same structure
                    #
    
                    #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                    key_chield = keyXML.getchildren()
                    i = 0
                    for child in key_chield:
                        # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                        root_list[int(math.fmod(i, num_XML))].append(child)
                        i = i + 1
                    #
                    #   Iterate through the finished XML documents and write to the event writer.
                    #
    
                    for fin_xml in root_list:
                        root = ElementTree.Element("mobile_device")
                        gen = mobile_device.find("general")
                        jss_id = gen.find("id").text
                        ElementTree.SubElement(root, 'id').text = jss_id

                        root.append(fin_xml)
                        chunk_uuid = ElementTree.Element("sub_pagination")
                        ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                        ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i)
                        ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(root_list.__len__())
                        root.append(chunk_uuid)
                        writeStringTo_Event( ElementTree.tostring(root) )
                    chunk_uuid = ElementTree.Element("sub_pagination")
                    ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                    ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i)
                    ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(root_list.__len__())
                    pagination.append(chunk_uuid)
                    

                #
                #   Remove the Key Index field from the XML
                #
                
                mobile_device.remove(keyXML)
        #
        # What's Left
        #
        self.append(pagination)
        mobile_device.append(self)
        writeStringTo_Event(ElementTree.tostring(mobile_device))
    #
    #   Done with Parsing Mobile Devices
    #
        
    def writeStringTo_Event_withParsing (DATA):
        if DATA.__len__() <maxCharLength:
            writeStringTo_Event( DATA )
        else:
            if DATA.__contains__("<mobile_device>"):
                writeMobileDevice(DATA)
            if DATA.__contains__("<computer>"):
                writeComputerDevice (DATA)
            
    
    def writeStringTo_Event( event_string ):
        #
        #   This class is to help with the writing to the Splunk Event writer
        #   
        #
        if event_string.__len__() < maxCharLength:
                event = helper.new_event(data=event_string, index=index, host=host)
                ew.write_event(event)
                return True
        else:
            root = ElementTree.Element("XML_TooLong")
            ElementTree.SubElement(root, 'error').text = "The XML was too long"
            writeStringTo_Event( ElementTree.tostring(root) )
            
            
            root = ElementTree.fromstring(event_string)
            children = root.getchildren
            
            debug = True
            if debug:
                event = helper.new_event(data=str(event_string.__len__()), index=index, host=host)
                ew.write_event(event)
            
            #for n in children
            #    writeStringTo_Event(ElementTree.tostring(n))
            #for self in root.find('self'):
                #writeStringTo_Event( ElementTree.tostring(self))

        return False
        
    def writeStringTo_Event_wTime( event_string, event_time ):
        #
        #   This class is to help with the writing to the Splunk Event writer
        #   
        #
        if event_string.__len__() < maxCharLength:
                event = helper.new_event(data=event_string, index=index, host=host, time = event_time)
                ew.write_event(event)
                return True
        else:
            root = ElementTree.Element("XML_TooLong")
            ElementTree.SubElement(root, 'error').text = "The XML was too long"
            writeStringTo_Event( ElementTree.tostring(root) )
            
            
            root = ElementTree.fromstring(event_string)
            children = root.getchildren
            
            debug = True
            if debug:
                event = helper.new_event(data=str(event_string.__len__()), index=index, host=host)
                ew.write_event(event)
            
            #for n in children
            #    writeStringTo_Event(ElementTree.tostring(n))
            #for self in root.find('self'):
                #writeStringTo_Event( ElementTree.tostring(self))

        return False
    
    api_retries = 0
    
    def api_get_Call(endPoint):

        #
        #   JSSResources API Call
        #
        
        api_family = ""
        if endPoint.__contains__("uapi/"):
            api_family = "uapi"
        if endPoint.__contains__("JSSResource/"):
            api_family = "classic"
        
        if api_family == "classic":  
            context = None
            isDone = False
            tryCount = 0
            while not isDone:
                try:
                    
                    r =  requests.get(endPoint, auth=(username, password), headers={'Accept': 'application/xml'}, verify=False)
                    status_code = r.status_code
                    resp = r.content
                    # https://developer.jamf.com/documentation for status code information
                    if (status_code == 200):
                        #   Request successful
                        isDone = True
                        context = r.content
                    if (status_code == 201):
                        #   Request to create or update object successful
                        context = r.content
                    if (status_code == 400):
                        #   Bad request. Verify the syntax of the request specifically the XML body.
                        pass
                    if (status_code == 401):
                        root = ElementTree.Element("XML_TooLong")
                        ElementTree.SubElement(root, 'error').text = "API Auth Error"
                        writeStringTo_Event( ElementTree.tostring(root) )
                        context = ElementTree.Element("error")
                        isDone = True
                        pass
                    if (status_code == 403):
                        #   Invalid permissions. Verify the account being used has the proper permissions for the object/resource you are trying to access.
                        pass
                    if (status_code == 404):
                        #   Object or resouce is not found
                        pass
                    if (status_code == 409):
                        #   Conflict
                        pass
                    if (status_code == 500):
                        #   Internal server error. Retry the request or contact Jamf support if the error is persistent.
                        pass
                    
                except requests.exceptions.Timeout:
                    isDone = isDone + 1
                    if isDone > 3:
                        root = ElementTree.Element("XML_TooLong")
                        ElementTree.SubElement(root, 'error').text = "Too Many Timeouts"
                        writeStringTo_Event( ElementTree.tostring(root) )
                        context = ElementTree.Element("error")
                    pass
                except requests.exceptions.TooManyRedirects:
                    root = ElementTree.Element("XML_TooLong")
                    ElementTree.SubElement(root, 'error').text = "Too Many Redirects"
                    writeStringTo_Event( ElementTree.tostring(root) )
                    context = ElementTree.Element("error")
                    pass
        
                except requests.exceptions.RequestException as e:
                    root = ElementTree.Element("XML_TooLong")
                    ElementTree.SubElement(root, 'error').text = "API Error Request Exception"
                    writeStringTo_Event( ElementTree.tostring(root) )
                    context = ElementTree.Element("error")
                    pass
                finally:
                    pass
    
        
        
        return context
        #
        #   End of the API Call Function
        #
        
        

    # Log that we are beginning to retrieve data.
    helper.log_debug("Started retrieving data for user %s" % username)
    
    #helper.log_debug(response.content)
    if api_call == "computer":
        #
        #   make the API Call
        #
        jss_url = "%sJSSResource/advancedcomputersearches/name/%s" % (url, search_name)
        response = requests.get(jss_url, auth=(username, password), headers={'Accept': 'application/xml'},verify=False)
        tree = ElementTree.fromstring(response.content)
        #
        #   Start Advanced Computer
        #
        
        #
        #   Chunk list is a list of the XML fields that we want to farm out to their own XML data sets
        #
        chunk_list = list()
        #chunk_list.append("Applications")
        #chunk_list.append("Computer_Group")
        chunk_list.append("Running_Services")
        
        #
        #   Pull the computers out of the Advanced Computer Search
        #
        
        computers_list = tree.find('computers')
        computers = computers_list.findall('computer')
        for computer in computers:
            
            #
            #   keyValue is an Abstract name for the values in Chunk List it will pull it out of the primary XML
            #
            for keyValue in chunk_list:
                if computer.find(keyValue):
                    keyXML = computer.find(keyValue)
                    # Get the lenght of the string representation of the XML document
                    key_char_length = ElementTree.tostring(keyXML).__len__()
                    if key_char_length < maxCharLength:
                        #
                        #   If this is under 10k just go ahead and write to the event reader
                        #
                        root = ElementTree.Element("computer")
                        ElementTree.SubElement(root, 'id').text = computer.find("id").text
                        root.append(keyXML)
                        writeStringTo_Event( ElementTree.tostring(root) )
                    else:
                        #
                        #   This is the area for if the already seperated XML is still too large. It will take the Length and use MOD to give the number of XML files it would need to be cut into. I add an additional one just in c
                        #
                        chunk_ID = str(uuid.uuid4())
                        num_XML = math.ceil(key_char_length / maxCharLength) + 1
                        #
                        #   Create an array of XML documents
                        #
                        root_list = []
                        for i in range(0, int(num_XML)):
                            root = ElementTree.Element(keyValue)
                            root_list.append(root)
                        #
                        #   Get a list of the 1st level children in the XML document keeping the same structure
                        #
        
                        #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                        key_chield = keyXML.getchildren()
                        i = 0
                        for child in key_chield:
                            # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                            root_list[int(math.fmod(i, num_XML))].append(child)
                            i = i + 1
                        #
                        #   Iterate through the finished XML documents and write to the event writer.
                        #
        
                        for fin_xml in root_list:
                            root = ElementTree.Element("computer")
                            ElementTree.SubElement(root, 'id').text = computer.find("id").text
                            root.append(fin_xml)
                            chunk_uuid = ElementTree.Element("sub_pagination")
                            ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                            ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i)
                            ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(root_list.__len__())
                            root.append(chunk_uuid)
                            
                            #writeStringTo_Event( ElementTree.tostring(chunk_uuid) )
                            
                            writeStringTo_Event( ElementTree.tostring(root) )

                    #
                    #   Remove the Key Index field from the XML
                    #
                    computer.remove(keyXML)
            #
            #   Post Data chunking... This *should* be under 10k char now, tune it with chunk list
            #
        
            data = ElementTree.tostring(computer)
        
            #
            #   Check to see if it needs chunking and if it still needs it chunk it on childs
            #
            if data.__len__() < maxCharLength:
                #print (data)
                writeStringTo_Event( data )
                
            else:
                num_XML = math.ceil(data.__len__() / maxCharLength) + 1
                #
                #   Create an array of XML documents
                #
                root_list = []
                chunk_ID = str(uuid.uuid4())
                for i in range(0, int(num_XML)):
                    root = ElementTree.Element("computer")
                    ElementTree.SubElement(root, 'id').text = computer.find("id").text
                    chunk_uuid = ElementTree.Element("pagination")
                    ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                    ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i+1)
                    ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(int(num_XML))
                    root.append(chunk_uuid)
                    
                    root_list.append(root)
                    
                #
                #   Get a list of the 1st level children in the XML document keeping the same structure
                #
        
                #
                #   Need to remove ID from XML since it will be a duplicate in 1 of them.
                #
                
                computer.remove(computer.find("id"))
                #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                key_chield = computer.getchildren()
                i = 0
                for child in key_chield:
                    # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                    root_list[int(math.fmod(i, num_XML))].append(child)
                    i = i + 1
                #
                #   Iterate through the finished XML documents and write to the event writer.
                #
        
                for fin_xml in root_list:
                    writeStringTo_Event( ElementTree.tostring(fin_xml))
        
            #
            # End of Computers For Loop
            #
        #
        # End of Advanced Computers Section
        #

    elif api_call == "mobile_device":
        jss_url = "%sJSSResource/advancedmobiledevicesearches/name/%s" % (url, search_name)
        response = requests.get(jss_url, auth=(username, password), headers={'Accept': 'application/xml'},verify=False)
        tree = ElementTree.fromstring(response.content)
        
        #
        #   Chunk list is a list of the XML fields that we want to farm out to their own XML data sets
        #
        chunk_list = list()
        chunk_list.append("Display_Name")
        chunk_list.append("Capacity_MB")
        chunk_list.append("Device_Locator_Service_Enabled")
        
        
        mobile_devices_list = tree.find('mobile_devices')
        mobile_devices = mobile_devices_list.findall('mobile_device')
        for mobile_device in mobile_devices:
            #
            #   keyValue is an Abstract name for the values in Chunk List it will pull it out of the primary XML
            #
            for keyValue in chunk_list:
                if mobile_device.findall(keyValue):
                    #event = helper.new_event(data=keyValue, index=index, host=host)
                    #ew.write_event(event)
                    keyXML = mobile_device.find(keyValue)
                    # Get the lenght of the string representation of the XML document
                    key_char_length = ElementTree.tostring(keyXML).__len__()
                    if key_char_length < maxCharLength:
                        #
                        #   If this is under 10k just go ahead and write to the event reader
                        #
        
                        root = ElementTree.Element("mobile_device")
                        ElementTree.SubElement(root, 'id').text = mobile_device.find("id").text
                        sub_root =  ElementTree.Element(keyValue)
                        root.append(keyXML)
                        #print(ElementTree.tostring(root))
                        writeStringTo_Event( ElementTree.tostring(root) )
                    else:
                        #
                        #   This is the area for if the already seperated XML is still too large. It will take the Length and use MOD to give the number of XML files it would need to be cut into. I add an additional one just in c
                        #
                        
                        num_XML = math.ceil(key_char_length / maxCharLength) + 1
                        
                        
                        
                        #
                        #   Create an array of XML documents
                        #
                        chunk_ID = uuid.uuid4()
                        root_list = []
                        for i in range(0, int(num_XML)):
                            root = ElementTree.Element(keyValue)
                            root_list.append(root)
                            
                        #
                        #   Get a list of the 1st level children in the XML document keeping the same structure
                        #
        
                        #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                        key_chield = keyXML.getchildren()
                        i = 0
                        for child in key_chield:
                            # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                            root_list[int(math.fmod(i, num_XML))].append(child)
                            i = i + 1
                        #
                        #   Iterate through the finished XML documents and write to the event writer.
                        #
        
                        for fin_xml in root_list:
                            root = ElementTree.Element("mobile_device")
                            ElementTree.SubElement(root, 'id').text = mobile_device.find("id").text
                            root.append(fin_xml)
                            event = helper.new_event(data=ElementTree.tostring(fin_xml), index=index, host=host)
                
                            chunk_uuid = ElementTree.Element("sub_pagination")
                            ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                            ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i+1)
                            ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(int(num_XML))
                            
                            #Finally Write it
                            writeStringTo_Event( ElementTree.tostring(fin_xml) )
                    #
                    #   Remove the Key Index field from the XML
                    #
                    mobile_device.remove(keyXML)
            #
            #   Post Data chunking... This *should* be under 10k char now, tune it with chunk list
            #
        
            data = ElementTree.tostring(mobile_device)
        
            #
            #   Check to see if it needs chunking and if it still needs it chunk it on childs
            #
            if data.__len__() < maxCharLength:
                writeStringTo_Event( data )
            else:
                num_XML = math.ceil(data.__len__() / maxCharLength) + 1
                #
                #   Create an array of XML documents
                #
                chunk_ID = str(uuid.uuid4())
                root_list = []
                for i in range(0, int(num_XML)):
                    root = ElementTree.Element("mobile_device")
                    ElementTree.SubElement(root, 'id').text = mobile_device.find("id").text
                    chunk_uuid = ElementTree.Element("pagination")
                    ElementTree.SubElement(chunk_uuid, 'uuid').text = chunk_ID
                    ElementTree.SubElement(chunk_uuid, 'chunk_number').text = str(i+1)
                    ElementTree.SubElement(chunk_uuid, 'chunk_size').text = str(int(num_XML))
                    root.append(chunk_uuid)
                    root_list.append(root)
                #
                #   Get a list of the 1st level children in the XML document keeping the same structure
                #
        
                #
                #   Need to remove ID from XML since it will be a duplicate in 1 of them.
                #
                mobile_device.remove(mobile_device.find("id"))
                #   Careful about the below call it is gone after 3.7 python new list function from 3.1 was introduced need to swith the call type
                key_chield = mobile_device.getchildren()
                i = 0
                for child in key_chield:
                    # print("inserting into array number: "+str(int(math.fmod(i,num_XML))))
                    root_list[int(math.fmod(i, num_XML))].append(child)
                    i = i + 1
                #
                #   Iterate through the finished XML documents and write to the event writer.
                #
        
                for fin_xml in root_list:
                    #print(ElementTree.tostring(fin_xml))
                    event = helper.new_event(data=ElementTree.tostring(fin_xml), index=index, host=host)
                    writeStringTo_Event( ElementTree.tostring(fin_xml) )
        
            #
            # End of mobile_devices For Loop
            #
        #
        # End of Advanced mobile_devices Section
        #
        

        
    elif api_call == "custom":
        #
        #   is By ITER or by single call
        #
        
        #
        #   URL Clean up stuff
        #
        
        if search_name.startswith("/"):
            search_name = search_name.replace("/","",1)
            
        if search_name.endswith("/"):
            search_name = search_name[:-1]
            
        jss_url = url + search_name
        
        resp_string = api_get_Call(jss_url)
        resp_xml = ElementTree.fromstring(api_get_Call(jss_url))
        
        if search_name.__contains__("/name/"):
            writeStringTo_Event( resp_string )
            return
        elif search_name.__contains__("/id/"):
            if search_name.__contains__("/computers/"):
                writeComputerDevice( resp_string )
            else:
                writeStringTo_Event( resp_string )
            return
        else:
            children = resp_xml.getchildren()
            for name in children:
                if name.findall("id"):
                    newCall = jss_url +"/id/"+name.find("id").text
                    data = api_get_Call(newCall)
                    writeStringTo_Event_withParsing( data )
                    
    #
    #   Start Here For Async Tests
    #
    


    
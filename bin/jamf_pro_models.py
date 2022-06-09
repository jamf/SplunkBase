""" This class is a models set for the Splunk Application."""
#
#
#
import uuid
import copy
import math
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

class jamf_pro_computer:
    """
    This class is used for a Jamf Pro Computer
    """
    # @description: This class is a computer model used to convert and use the tools for Splunk
    # @author: kpazandak:
    # @init : 1.0.6

    computer_record = ElementTree.fromstring("<computer></computer>")
    record_type = ""

    def __init__(self):
        """
        This is the init, nothing is done, reserved
        """

    def build_from_string(self, computer, source_type):
        """
        This builds the object from the string
        :param computer: String XML from a Jamf Pro
        :param source_type: JSSResource or UAPI, Source of the computer
        :return: None
        """
        self.computer_record = ElementTree.fromstring(computer)
        self.record_type = source_type

    def get_computer_xml(self):
        """
        Returns the XML of a computer record
        :return: Element Tree object of a computer record
        """
        return self.computer_record

    def paginate(self, *args, **kwargs):
        """
        This function is used in the Splunk Event writer to ensure you don't over runt he Max Char limit
        :param args:
        :param kwargs:
        :param max_char_length int. This is the max length the event writer can write to.
        :param create_event_id boolean. Creates a unique event ID to rebuild the string after the event writer
        :param remove_lsit list of XML Keywords. Removes the Keywords from the Event List
        :return a list of string objects that can be sent to the event writer
        """

        #Setup and Kwargs
        computer = copy.deepcopy(self.computer_record)
        pagination_list = list()
        max_char = kwargs.get("max_char_length", 9980)
        chunk_list = kwargs.get("chunk_list", None)

        #Setup the Chunking and remove Lists
        if chunk_list == None:
            chunk_list = list()
            chunk_list.append("running_services")
            chunk_list.append("applications")

        remove_list = kwargs.get("remove_list", None)

        if remove_list == None:
            remove_list = list()
            remove_list.append("unix_executables")
            remove_list.append("installed_by_casper")
            remove_list.append("installed_by_installer_swu")
            remove_list.append("cached_by_casper")
            remove_list.append("available_software_updates")
            remove_list.append("available_updates")
            remove_list.append("fonts")

        if kwargs.get("create_event_id", False):
            event_id = ElementTree.Element("pagination")
            ElementTree.SubElement(event_id, 'event_id').text = str(uuid.uuid4())
            ElementTree.SubElement(event_id, 'id').text = self.computer_record.find('./general/id').text
            ElementTree.SubElement(event_id, 'username').text = self.computer_record.find('./location/username').text
            ElementTree.SubElement(event_id, 'is_managed').text = self.computer_record.find('./general/remote_management/managed').text
            ElementTree.SubElement(event_id, 'is_supervised').text = self.computer_record.find('./general/supervised').text
            ElementTree.SubElement(event_id, 'department').text = self.computer_record.find('./location/department').text
            ElementTree.SubElement(event_id, 'building').text = self.computer_record.find('./location/building').text
            ElementTree.SubElement(event_id, 'serial_number').text = self.computer_record.find('./general/serial_number').text
            ElementTree.SubElement(event_id, 'report_date_epoch').text = str(int(int(self.computer_record.find('./general/report_date_epoch').text)/1000))
            ElementTree.SubElement(event_id, 'site_name').text = self.computer_record.find('./general/site/name').text
            max_char = max_char - ElementTree.tostring(event_id).__len__()

        computer_strings = list()
        for elem in computer.iter():
            for child in list(elem):
                if child.tag in remove_list:
                    elem.remove(child)
                    remove_list.remove(child.tag)
                if child.tag in chunk_list:
                    pagination_list.append(copy.deepcopy(child))
                    elem.remove(child)
                    chunk_list.remove(child.tag)
        fin_xml = list()
        for child in computer.getchildren():
            for i in self.paginate_xml(child, max_char):
                fin_xml.append(copy.deepcopy(i))
        for line in pagination_list:
            for i in self.paginate_xml(line, max_char):
                fin_xml.append(copy.deepcopy(i))

        for item in fin_xml:
            final_xml = ElementTree.Element("computer")
            final_xml.append(item)
            final_xml.append(event_id)
            computer_strings.append(ElementTree.tostring(final_xml))
        return computer_strings

    def paginate_xml(self, source_xml, max_char):
        """

        :param source_xml This is a source XML object :
        :param max_char This is max length the string object may be:
        :return:
        """
        source = copy.deepcopy(source_xml)

        if ElementTree.tostring(source).__len__() < max_char:
            return [source]
        else:
            num_xml = math.ceil(ElementTree.tostring(source).__len__()/ max_char)+1
            xml_list = list()
            for i in range(0, int(num_xml)):
                xml_list.append(ElementTree.Element(source.tag))
            i = 0
            for child in source.getchildren():
                xml_list[int(math.fmod(i, xml_list.__len__()))].append(child)
                i = i + 1
            #or item in xml_list:
            #    print(item)
            return xml_list

class jamf_pro_mobile_device:
    """
    This is a Jamf Pro Mobile Device as reported by the API in Jamf Pro
    """
    # @description: This class is a computer model used to convert and use the tools for Splunk
    # @author: kpazandak:
    # @init : 1.0.6

    mobile_record = ElementTree.fromstring("<mobile_device></mobile_device>")
    def __init__(self):
        """
        Reserved initialization function.
        """

    def build_from_string(self, mobile_device, source_type):
        """
        This funciton builds the object from a String Representation of the object
        :param mobile_device: The STR reprsentation of the object
        :param source_type: mobile_device
        :return: None
        """
        if source_type == "mobile_device":
            self.mobile_record = ElementTree.fromstring(mobile_device)

    def build_from_xml(self, mobile_device, source_type):
        """
        Builds the Object from an XML Object
        :param mobile_device: STR of a mobile_device
        :param source_type: JSSResource or UAPI
        :return: None
        """
        try:
            self.mobile_record = ElementTree.fromstring(mobile_device)
        except:
            pass
        pass

    def get_mobile_xml(self):
        """
        Returns the Element Tree Representation of the object
        :return: ElementTree record of a mobile_device
        """
        return self.mobile_record

    def paginate(self, *args, **kwargs):
        """
        This function is used in the Splunk Event writer to ensure you don't over runt he Max Char limit
        :param args:
        :param kwargs:
        :param max_char_length int. This is the max length the event writer can write to.
        :param create_event_id boolean. Creates a unique event ID to rebuild the string after the event writer
        :param remove_lsit list of XML Keywords. Removes the Keywords from the Event List
        :return a list of string objects that can be sent to the event writer
        """

        #Setup and Kwargs
        mobile_device = copy.deepcopy(self.mobile_record)
        pagination_list = list()
        max_char = kwargs.get("max_char_length", 9980)
        chunk_list = kwargs.get("chunk_list", None)

        #Setup the Chunking and remove Lists
        if chunk_list == None:
            chunk_list = list()
            # ToDo: Set the Mobile Devices Chunk List settings
        remove_list = kwargs.get("remove_list", None)

        if remove_list == None:
            remove_list = list()
            # ToDo: Set the Mobile Devices Chunk List settings
        if kwargs.get("create_event_id", False):
            event_id = ElementTree.Element("pagination")
            ElementTree.SubElement(event_id, 'event_id').text = str(uuid.uuid4())
            ElementTree.SubElement(event_id, 'id').text = self.mobile_record.find('./general/id').text
            ElementTree.SubElement(event_id, 'username').text = self.mobile_record.find('./location/username').text
            ElementTree.SubElement(event_id, 'name').text = self.mobile_record.find('./general/name').text
            ElementTree.SubElement(event_id, 'is_managed').text = self.mobile_record.find('./general/managed').text
            ElementTree.SubElement(event_id, 'is_supervised').text = self.mobile_record.find('./general/supervised').text
            ElementTree.SubElement(event_id, 'department').text = self.mobile_record.find('./location/department').text
            ElementTree.SubElement(event_id, 'building').text = self.mobile_record.find('./location/building').text
            ElementTree.SubElement(event_id, 'serial_number').text = self.mobile_record.find('./general/serial_number').text
            ElementTree.SubElement(event_id, 'report_date_epoch').text = str(int(int(self.mobile_record.find('./general/last_inventory_update_epoch').text)/1000))
            ElementTree.SubElement(event_id, 'site_name').text = self.mobile_record.find('./general/site/name').text
            max_char = max_char - ElementTree.tostring(event_id).__len__()

        mobile_strings = list()
        for elem in mobile_device.iter():
            for child in list(elem):
                if child.tag in remove_list:
                    elem.remove(child)
                    remove_list.remove(child.tag)
                if child.tag in chunk_list:
                    pagination_list.append(copy.deepcopy(child))
                    elem.remove(child)
                    chunk_list.remove(child.tag)
        fin_xml = list()

        for child in mobile_device.getchildren():
            for i in self.paginate_xml(child, max_char):
                fin_xml.append(copy.deepcopy(i))
        for line in pagination_list:
            for i in self.paginate_xml(line, max_char):
                fin_xml.append(copy.deepcopy(i))

        for item in fin_xml:
            final_xml = ElementTree.Element("mobile_device")
            final_xml.append(item)
            final_xml.append(event_id)
            mobile_strings.append(ElementTree.tostring(final_xml))
        return mobile_strings

    def paginate_xml(self, source_xml, max_char):
        """
        :param source_xml This is a source XML object :
        :param max_char This is max length the string object may be:
        :return:
        """
        source = copy.deepcopy(source_xml)

        if ElementTree.tostring(source).__len__() < max_char:
            return [source]
        else:
            num_xml = math.ceil(ElementTree.tostring(source).__len__()/ max_char)+1
            xml_list = list()
            for i in range(0, int(num_xml)):
                xml_list.append(ElementTree.Element(source.tag))
            i = 0
            for child in source.getchildren():
                xml_list[int(math.fmod(i, xml_list.__len__()))].append(child)
                i = i + 1
            return xml_list


class RestrictedSoftware:
    """
    This class is for Restricted Software. It can take in the record from JSSResource or UAPI
    and return it formated for Splunk
    """
    # @description: This class is a computer model used to convert and use the tools for Splunk
    # @author: kpazandak
    # @init : 1.0.7

    restricted_software = ElementTree.fromstring("<restricted_software></restricted_software>")

    def __init__(self):
        # Todo: Bulid the init with arguments to build a computer model used in other functions of this program.
        # ToDo: Recognize a AdvancedSearch Record vs a JSSResource Record vs a UAPI record.
        pass

    def build_from_string(self, restricted_software, source_type):
        """
        Builds the Restricted Software object from a JSSResource or UAPI call
        :param restricted_software:
        :param source_type:
        :return:
        """
        self.restricted_software = ElementTree.fromstring(restricted_software)

class MacApplication:
    """
    This class is for the /JSSResource/macapplications call.
    """
    source = ""
    mac_application = ElementTree.fromstring("<mac_applications></mac_applications>")
    def __init__(self, **kwargs):
        """
        Reserved for future use
        """
        self.max_char = kwargs.get("max_char_length", 9980)


    def build_from_string(self, mac_applications: str, source_type: str, *args, **kwargs):
        """
        This will build the XML object from a sting object from the JSS API
        :param mac_applications: a String Representation of the XML object
        :param source_type: JSSResource or UAPI (Beta)
        :param args: None
        :param kwargs: remove_icon:Bool
        :return: None
        """

        #Check Kargs
        remove_icon = kwargs.get("remove_icon", True)
        self.source = source_type

        context = ElementTree.fromstring(mac_applications)
        remove_list = list()

        if remove_icon:
            remove_list.append("self_service_icon")
        print(remove_list)
        for elem in context.iter():
            for child in list(elem):
                if child.tag in remove_list:
                    print("Found it")
                    elem.remove(child)
                    remove_list.remove(child.tag)

        self.mac_application = context

    def paginate(self):
        """
        Returns a paginated String Object for the class
        :return: A String Object of an XML.
        """
        pagination_list = list()
        if ElementTree.tostring(self.mac_application).__len__() < self.max_char:
            pagination_list.append(ElementTree.tostring(self.mac_application))
            return pagination_list

        return ElementTree.tostring(self.mac_application)


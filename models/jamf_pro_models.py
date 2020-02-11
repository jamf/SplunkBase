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
    # @descripition: This class is a computer model used to convert and use the tools for Splunk
    # @kpazandak:
    # @init : 1.0.6

    computer_record = ElementTree.fromstring("<computer></computer>")
    def __init__(self):
        # Todo: Bulid the init with arguments to build a computer model used in other functions of this program.
        # ToDo: Recognize a AdvancedSearch Record vs a JSSResource Record vs a UAPI record.
        pass

    def build_from_string(self, computer, source_type):
        if source_type == "computer_record":
            self.computer_record = ElementTree.fromstring(computer)
        pass

    def build_from_xml(self, computer, source_type):
        try:
            self.computer_record = ElementTree.fromstring(computer)
        except:
            pass
        pass

    def get_computer_xml(self):
        return self.computer_record

    def paginate(self,*args,**kwargs):
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
        remove_list = kwargs.get("remove_list",None)
        if remove_list == None:
            remove_list = list()
            remove_list.append("unix_executables")
            remove_list.append("installed_by_casper")
            remove_list.append("installed_by_installer_swu")
            remove_list.append("cached_by_casper")
            remove_list.append("available_software_updates")
            remove_list.append("available_updates")
            remove_list.append("fonts")

        if kwargs.get("create_event_id",False):
            event_id=ElementTree.Element("pagination")
            ElementTree.SubElement(event_id,'event_id').text =str(uuid.uuid4())
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
            for i in self.paginate_xml(child,max_char):
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
        pass
    def paginate_xml (self, source_xml, max_char):
        """

        :param source_xml This is a source XML object :
        :param max_char This is max length the string object may be:
        :return:
        """
        source = copy.deepcopy(source_xml)

        if ElementTree.tostring(source).__len__()<max_char:
            return [source]
        else:
            num_xml = math.ceil(ElementTree.tostring(source).__len__()/ max_char)+1
            xml_list = list()
            for i in range(0,int(num_xml)):
                xml_list.append(ElementTree.Element(source.tag))
            i = 0
            for child in source.getchildren():
                xml_list[int(math.fmod(i, xml_list.__len__()))].append(child)
                i = i + 1
            #or item in xml_list:
            #    print(item)
            return xml_list
    def _locate_key_value(self):
        pass

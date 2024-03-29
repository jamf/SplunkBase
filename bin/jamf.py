import jamf_pro_addon_for_splunk_declare

import os
import sys
import time
import datetime
import json

import modinput_wrapper.base_modinput
from splunklib import modularinput as smi



import input_module_jamf as input_module

bin_dir = os.path.basename(__file__)

'''
    Do not edit this file!!!
    This file is generated by Add-on builder automatically.
    Add your modular input logic to file input_module_jamf.py
'''
class ModInputjamf(modinput_wrapper.base_modinput.BaseModInput):

    def __init__(self):
        if 'use_single_instance_mode' in dir(input_module):
            use_single_instance = input_module.use_single_instance_mode()
        else:
            use_single_instance = False
        super(ModInputjamf, self).__init__("jamf_pro_addon_for_splunk", "jamf", use_single_instance)
        self.global_checkbox_fields = None

    def get_scheme(self):
        """overloaded splunklib modularinput method"""
        scheme = super(ModInputjamf, self).get_scheme()
        scheme.title = ("jamf")
        scheme.description = ("Go to the add-on\'s configuration UI and configure modular inputs under the Inputs menu.")
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True

        scheme.add_argument(smi.Argument("name", title="Name",
                                         description="",
                                         required_on_create=True))

        """
        For customized inputs, hard code the arguments here to hide argument detail from users.
        For other input types, arguments should be get from input_module. Defining new input types could be easier.
        """
        scheme.add_argument(smi.Argument("name_of_the_modular_input", title="Name of the Modular Input",
                                         description="Unique Input Name for the data",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("jss_url", title="JSS URL",
                                         description="Base URL for JAMF instance",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("username", title="Username",
                                         description="",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("password", title="Password",
                                         description="",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("api_call", title="API Call Name",
                                         description="API Call Name",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("search_name", title="Search Name",
                                         description="Preconfigured Advanced Search to call or Custom API call, refer to documentation",
                                         required_on_create=True,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("custom_host_name", title="Custom Host Name",
                                         description="",
                                         required_on_create=False,
                                         required_on_edit=False))
        scheme.add_argument(smi.Argument("custom_index_name", title="Custom Index Name",
                                         description="",
                                         required_on_create=False,
                                         required_on_edit=False))
        return scheme

    def get_app_name(self):
        return "JAMF-Pro-addon-for-splunk"

    def validate_input(self, definition):
        """validate the input stanza"""
        input_module.validate_input(self, definition)

    def collect_events(self, ew):
        """write out the events"""
        input_module.collect_events(self, ew)

    def get_account_fields(self):
        account_fields = []
        return account_fields

    def get_checkbox_fields(self):
        checkbox_fields = []
        return checkbox_fields

    def get_global_checkbox_fields(self):
        if self.global_checkbox_fields is None:
            checkbox_name_file = os.path.join(bin_dir, 'global_checkbox_param.json')
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, 'r') as fp:
                        self.global_checkbox_fields = json.load(fp)
                else:
                    self.global_checkbox_fields = []
            except Exception as e:
                self.log_error('Get exception when loading global checkbox parameter names. ' + str(e))
                self.global_checkbox_fields = []
        return self.global_checkbox_fields

if __name__ == "__main__":
    exitcode = ModInputjamf().run(sys.argv)
    sys.exit(exitcode)

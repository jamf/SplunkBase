import json
import time
from datetime import datetime, timedelta, timezone
import logging
import requests
import base64
from splunklib.modularinput import helper

class JamfPro:
    class JamfUAPIAuthToken(object):
        def __init__(self, jamf_url, username, password, helper, headers):
            """
            :param jamf_url: Jamf Pro URL
            :type jamf_url: str
            :param username: Username for authenticating to JSS
            :param password: Password for the provided user
            """
            self.helper = helper
            self.server_url = jamf_url
            self.extraHeaders = headers
            self._auth = (username, password)
            self._token = ''
            self._token_expires = float()
            if helper.get_proxy() == {}:
                self.useProxy = False
            else:
                self.useProxy = True
            self.useProxy = False
            self.get_token()

        @staticmethod
        def unix_timestamp():
            """Returns a UTC Unix timestamp for the current time"""
            epoch = datetime(1970, 1, 1)
            now = datetime.utcnow()
            return (now - epoch).total_seconds()

        def headers(self, add=None):
            """
            :param add: Dictionary of headers to add to the default header
            :type add: dict
            """
            header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            if hasattr(self, '_auth_token'):
                header.update(self._auth_token.header)

            if add:
                header.update(add)

            return header

        @property
        def token(self):
            if self._token_expires < self.unix_timestamp():
                logging.warning("JSSAuthToken has expired: Getting new token")
                self.get_token()

            return self._token

        @token.setter
        def token(self, new_token):
            self._token = new_token

        @property
        def header(self):
            return {'Authorization': 'Bearer {}'.format(self.token)}

        def __repr__(self):
            return "<JSSAuthToken(username='{}')>".format(self._auth[0])

        def get_token(self):
            url = self.server_url + 'api/v1/auth/token'
            logging.info("JSSAuthToken requesting new token")

            userpass = self._auth[0] + ':' + self._auth[1]
            encoded_u = base64.b64encode(userpass.encode()).decode()
            headers = {"Authorization": "Basic %s" % encoded_u}
            for key in self.extraHeaders:
                headers[key] = self.extraHeaders[key]

            response = self.helper.send_http_request(url="https://" + url,
                                                     method="POST",
                                                     headers=headers,
                                                     use_proxy=self.useProxy)
            if response.status_code != 200:
                raise Exception
            self.unix_timestamp() + 60
            self._set_token(response.json()['token'], self.unix_timestamp() + 60)

        def _set_token(self, token, expires):
            self.token = token
            self._token_expires = float(expires)


    def __init__(self, jamf_url="", jamf_username="", jamf_password="", helper=None, headers=None):
        self.helper = helper
        self.url = jamf_url

        self.username = jamf_username
        self.password = jamf_password
        self.extraHeaders = headers
        self._authToken = self.JamfUAPIAuthToken(jamf_url=jamf_url, username=jamf_username, password=jamf_password,
                                                 helper=helper, headers=headers)

        if helper.get_proxy() == {}:
            self.useProxy = False
        else:
            self.useProxy = True

    @property
    def getHeaders(self):
        headers = self._authToken.headers()
        auth = self._authToken.header
        headers['Authorization'] = auth['Authorization']
        for key in self.extraHeaders:
            headers[key] = self.extraHeaders[key]

        return headers

    @property
    def getXMLHeaders(self):
        headers = self._authToken.headers()
        auth = self._authToken.header
        headers['Authorization'] = auth['Authorization']
        headers['Accept'] = 'application/xml'
        for key in self.extraHeaders:
            headers[key] = self.extraHeaders[key]


        return headers

    def _url_get_call(self, URL=""):
        """
        :param URL:
        :return:
        """
        url = URL
        response_dict = None
        for i in range(0, 3):
            try:
                if response_dict is None:
                    response = self.helper.send_http_request(url="https://" + url,
                                                             method="GET", payload=None,
                                                             headers=self.getHeaders, verify=True,
                                                             use_proxy=self.useProxy, timeout=60)
                    response_dict = json.loads(response.content)
            except Exception as e:
                print(e)
                response_dict = None

        return response_dict

    def _url_get_xml_call(self, URL=""):
        """
        :param URL:
        :return:
        """
        url = URL
        request_successful = None
        for i in range(0, 3):
            try:
                if request_successful:
                    response = self.helper.send_http_request(url="https://" + url,
                                                             method="GET", payload=None,
                                                             headers=self.getXMLHeaders, verify=True,
                                                             use_proxy=self.useProxy, timeout=60)
                    if response.status_code == "200" or response.status_code == 200:
                        request_successful = True
                        return response
            except Exception as e:
                helper.log_error("Exception occured when making request to URL=%s\n%s" % (URL, e))
                request_successful = None

        return response

    def _filter_computer(self, filters={}, computer={}) -> bool:
        """
        Returns if to include the computer or not
        :param filters: Dictionary of the Filters for a Device
        :param computer: UAPI Computer Details
        :return: Boolean, Reason for False
        """
        # Device Managed
        if 'managed' in filters:
            if computer['general']['remoteManagement']['managed'] != filters['managed']['value']:
                return False, "notManaged"

        # Last Contact
        if 'lastContactTime' in filters:
            try:
                computerTime = datetime.strptime(computer['general']['lastContactTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                computerTime = datetime.strptime(computer['general']['lastContactTime'], "%Y-%m-%dT%H:%M:%SZ")
            except:
                return False, "no Contact Time"

            testTime = datetime.strptime(filters['lastContactTime']['value'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if filters['lastContactTime']['operator'] == '>':
                if computerTime > testTime:
                    pass
                else:
                    return False, "contactTimeBoundary"

        # Last Report
        if 'lastReportTime' in filters:
            try:
                if computer['general']['reportDate'] == None:
                    return False, "NoReportDate"
                computerTime = datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                computerTime = datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%SZ")

            testTime = datetime.strptime(filters['lastReportTime']['value'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if filters['lastReportTime']['operator'] == '>':
                if computerTime > testTime:
                    pass
                else:
                    return False, "reportTimeBoundary"

        # Base Case, Never got a False
        return True, None

    def _build_url(self, sections=[], page_number=1, page_size=200, endpoint="", sortKey=""):
        response = self.url
        response = response + endpoint
        section_s = "?"
        for section in sections:
            if section == sections[0]:
                section_s = section_s + f"section={section}"
            else:
                section_s = section_s + f"&section={section}"
        response = response + section_s
        response = response + f"&page={page_number}&page-size={page_size}"
        if sortKey != "":
            response = response + sortKey
        return response

    def getAllComputers(self, filters: dict, sections: list, sortKey: str):
        endpoint = "api/v1/computers-inventory"
        page_number = 0
        page_size = 200
        another_page = True
        computers = []

        while another_page:
            url = self._build_url(sections=sections, page_size=page_size, page_number=page_number, endpoint=endpoint,
                                  sortKey=sortKey)
            try:
                p_computers = self._url_get_call(URL=url)['results']
            except KeyError:
                p_computers = []

            if p_computers.__len__() == 0:
                another_page = False
            else:
                for computer in p_computers:
                    addComputer, reason = self._filter_computer(filters=filters, computer=computer)
                    if addComputer:
                        computers.append(computer)
                    else:
                        if reason == "contactTimeBoundary":
                            another_page = False
                        if reason == "reportTimeBoundary":
                            another_page = False
                page_number = page_number + 1
        return computers

    def getComputersPageNumber(self, filters: dict, sections: list, sortKey: str, pageNumber: int):
        endpoint = "uapi/v1/computers-inventory"
        page_number = pageNumber
        page_size = 200
        computers = []

        url = self._build_url(sections=sections, page_size=page_size, page_number=page_number, endpoint=endpoint,
                              sortKey=sortKey)
        try:
            p_computers = self._url_get_call(URL=url)['results']
        except KeyError:
            p_computers = []

        for computer in p_computers:
            addComputer, reason = self._filter_computer(filters=filters, computer=computer)
            if addComputer:
                computers.append(computer)

        return computers

    def getComputerDetails(self, jss_id=0, ssn=""):
        """
        This function will return Current Details about a computer
        :param jss_id: INT jss_ID
        :param ssn: String of the SSN
        :return: JSON/DICT of the Computer
        """

        if jss_id > 0 and ssn == "":
            endpoint = f"uapi/v1/computers-inventory-detail/{jss_id}"
            response = self._url_get_call(URL=self.url + endpoint)
            return response

    def getComputerApplicationUsage(self, jss_id=0, days=21, appName=""):
        tod = datetime.now()
        d = timedelta(days=days)
        a = tod - d
        start = a.strftime("%Y-%m-%d")
        end = tod.strftime("%Y-%m-%d")

        endpoint = f"JSSResource/computerapplicationusage/id/{jss_id}/{start}_{end}"
        response = self._url_get_call_JSSResource(URL=self.url + endpoint)
        if appName != "":
            # Strip out other Applications
            for appUsageDay in response['computer_application_usage']:
                appUsageDay['apps'] = list(filter(lambda i: i['name'].lower() == appName, appUsageDay['apps']))

        return response

    def getMobileDevicesSubsetBasic(self):
        """

        :return:
        """

    def getMobileDevices(self,):

        endpoint = "JSSResource/mobiledevices/subset/basic"
        response = self._url_get_call(URL=self.url + endpoint)
        return response['mobile_devices']

    def getMobileDevicesDetails(self, id, apiVersion):
        if apiVersion == "JSSResource":
            endpoint = f"JSSResource/mobiledevices/id/{id}"
        if apiVersion == "api/v2":
            endpoint = f"api/v2/mobile-devices/{id}/detail"
        if apiVersion == "api/v1":
            endpoint = f"api/v1/mobile-devices/{id}/detail"
        response = self._url_get_call(URL=self.url + endpoint)
        return response

    def getMobileDeviceGroups(self, details=False):
        endpoint = f"api/v1/mobile-device-groups"
        response = self._url_get_call(URL=self.url + endpoint)
        if details:
            for smartGroup in response:
                endpoint = f"JSSResource/mobiledevicegroups/id/{smartGroup['id']}"
                response2 = self._url_get_call(URL=self.url + endpoint)
                smartGroup['devices'] = response2['mobile_device_group']['mobile_devices']
        return response

    def getDepartments(self):
        endpoint = f"api/v1/departments?page=0&page-size=400&sort=id%3Aasc"
        response = self._url_get_call(URL=self.url + endpoint)
        departments = {}
        for dep in response['results']:
            departments[dep['id']] = dep['name']
        return departments

    def getBuildindgs(self):
        endpoint = f"api/v1/buildings?page=0&page-size=400&sort=id%3Aasc"
        response = self._url_get_call(URL=self.url + endpoint)
        buildings = {}
        for building in response['results']:
            buildings[building['id']] = building['name']
        return buildings

    def getJSSResourceXML(self, endpoint):
        url = f"{endpoint}"
        print(url)
        try:
            return self._url_get_xml_call(URL=url)
        except:
            print("Error With API call")
            return None

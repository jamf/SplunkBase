# SplunkBase
Jamf's Published Splunk Base Integration Version 1.0.5

Splunk turns machine data into answers with the leading platform for analytics, helping businesses gain insight into their data.

Use this modular input app to integrate Jamf Pro with Splunk to enable a deeper level of analytics for your Jamf Pro data. This easy to use integration utilizes the advanced search APIs in Jamf Pro with Splunk’s modular input framework.

The application also provides a framework for the development of additional API based integrations to further enable analysis of Jamf Pro in Splunk.

Features
- Import Computer and Mobile Device data from multiple Jamf Pro instances
- Import several system settings fields using the Custom API field
- Create and expand on visuals using tools in Splunks ecosystem


# New Features!

  - Added the ability to use a Custom API end point
  - Updated Computers API endpoint to exclude FONTS, to save data
  - Added the ability to conenct to Jamf Pro servers with invalid certs


# Advanced Computer and Mobile Search

The Computers tab and Mobile Devices tabs use a specific Jamf Pro endpoint referred to as Advanced Computer Searches. The power of these is you can use the Criteria section to narrow your selection of devices. For an example you can collect on only managed devices so you don't collect on devices you no longer are responsible for. You can also control the data that goes into the Splunk engine by using the Display section. Only Data fields that are checked will be ingested by the Splunk Event Writer. This allows you to reduce your logging to only values you want or can remove what you deem Personally  Identifiable Information.

To use these highlight the Computer or Mobile Device tab and then in the Custom URL field enter the Name of the Advanced Search.

Learn more here: 
 https://docs.jamf.com/10.16.0/jamf-pro/administrator-guide/Advanced_Computer_Searches.html
 
# Custom API End points

Custom API endpoints allows you to collect information from the Jamf Pro by integrating directly with the API. Below is a list of common endpoints that you may want to collect against. Copy paste these code paths into the custom fields to get the data described or go to the Jamf API page found here:

# Structure

The API endpoints work such that if you call any of the JSSResource endpoints if you call the base it will take call that and then iterate across all objects that return. As an example if you call ```/JSSResource/computers/``` it will call all computers. If you enter a NAME or ID field in the custom URL it will only call that object directly. Example would be ```/JSSResource/computers/id/10``` this would return only the computer with the ```JSS_ID``` equal to 10. If you use the ```name``` it will return the computer that last reported that has that system name. 

# Interesting Custom API strings

``` /JSSResource/computers```
This allows you to iterate across the computers and pull every computer. There is no restrictions and the only field that is dropped is the FONTS field.

``` /JSSResource/mobiledevices```
This allows you to iterate across the mobile devices and pull every iPad, iPhone, appleTV, and other mobile devices. It returns all fields

```/JSSResource/byoprofiles```
This collects the configuration profiles that would be applied to computers or mobile devices that are user enrolled, formerally Bring Your Own Device profiles

```/JSSResource/computerconfigurations```
This collects all of the Computer Configurations that could be applied to a computer. It also returns details related to what is controlled by the configuration profile

```/JSSResource/directorybindings```
This collects the User Direcotry Bindings and authentication that devices use for user lookup. Used with conditional access systems

```/JSSResource/licensedsoftware```
This collects the software that you are licensed to use from the Apple Store. You must be connected with Apple School or Business Manager to use this feature

```/JSSResource/macapplications```
This collects every application that the Jamf Pro server has seen on devices since it has started collecting. This is a high data usage endpoint

```/JSSResource/mobiledeviceapplications```
This collects every application installed on a mobile device that the Jamf Pro server has seen. This is a high data usage endpoint

```/JSSResource/restrictedsoftware```
This colelcts applications that have been marked restricted by the Jamf Pro administrator. These are applications that the Jamf Pro, if it has the ability, will remove from the device

```/JSSResource/scripts```
This collects the scripts that could be deployed to a computer. Combine this with Smart Groups to find all of the computers with these scripts installed

```/JSSResource/sites```
This collections the multi-tenancy information available with sites. Sites is less used feature that allows a hierarchical setup to your Jamf Pro server. This exposes those relationships

```/JSSResource/users```
This allows you to collect on users that the Jamf Pro server has seen. You can correlate assigned devices with this endpoint

```/JSSResource/vppassignments```
This shows the applications that were purchased through the Apple Volume Purchasing Program and either which user or which device it is deployed to.

# Installation and Setup

After acquiring and installing onto your instance this Modular Input you will be presented a form with the below 
Input Data fields 
```Name```: This is the unique name for the data search

```Interval```: This is the number of seconds it should wait between collecting. The suggestions are 3600 (1 hour) or 86400 (1 day)

```Name of Modular Input```: This is the name used for the search field it is suggested to be the same as ```Name```

```JSS URL``` : This is the FQDN endpoint for your Jamf Pro server. Your Splunk server must have either 443 or 8443 access to this port depending on your deployment. Valid inputs are https://yourserver.domain.com https://yourserver.domain.com:8443 yourserver.domain.com

```Search Name```: This is either the Advanced Search name used for the Computer or Mobile Device or it is the Custom API URI field to collect additional information from the Jamf Pro besides Computer or Mobile Device information

```Username```: Refer to your documentation on how to create read only accounts and ensuring that the account has the correct and appropriate access rights to your data

```Password```: The password for the user or service account that will be used to collect this information. 

```Custom Index Name and Custom Host Name```: These are data fields for advanced Splunk Users to allow multiple inputs or multiple hosts to appear as a single input.

```Index```: This is used if you split your data into different indexes. 

## Dashboards and Visuals

Coming soon with be example and included dashboard to show you what is possible with both Splunk and Jamf

## Help us make this better

Reach out on Jamf Nation https://www.jamf.com/jamf-nation/ to find users and interact with us on how to make this better. We are highly interested to see what people can build in Splunks environment with your data.

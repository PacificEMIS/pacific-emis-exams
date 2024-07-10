# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import requests
import urllib.parse
import xml.dom.minidom
import zipfile
import base64
import os
import json
import jsbeautifier

from IPython.display import display, Markdown

# Configuration (initial setup)
with open('config.json', 'r') as file:
     config = json.load(file)

username = config['tao_username']
password = config['tao_password']
tao_server_url = config['tao_server_url']

# The samples below will need to have URI adjusted for the server in use.
#sample_testtakerUri = 'http://pacifictest1-1.purltek.com/first.rdf#i66740de10b8c9256742627033f714db960'
#sample_deliveryUri = 'http://pacifictest1-1.purltek.com/first.rdf#i667426cc1074825386922c196a498596ce'
#sample_itemUri = 'http://pacifictest1-1.purltek.com/first.rdf#i6673eaa03ec8b25386eb74654e2440908b'
#sample_testUri = 'http://pacifictest1-1.purltek.com/first.rdf#i667428df5ead22567868a6df1e9751f57e'
#sample_testUri2 = 'http://pacifictest1-1.purltek.com/first.rdf#i667428b5718fc25487b7188603a736d3c5'
sample_testtakerUri = 'http://fedtests.nuzusys.com/FedTESTS.rdf#i16066442242141455'
sample_deliveryUri = 'http://fedtests.nuzusys.com/FedTESTS.rdf#i16066499465949598'
sample_itemUri = 'http://fedtests.nuzusys.com/FedTESTS.rdf#i16064432284408326'
sample_testUri = 'http://fedtests.nuzusys.com/FedTESTS.rdf#i16066493657445593'
sample_testUri2 = 'http://fedtests.nuzusys.com/FedTESTS.rdf#i16066498847989596'

# Setup some commonly used paths
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/TAO')
zip_file_path = os.path.join(local_path, 'qti_package.zip')
extract_path = os.path.join(local_path, 'extracted_qti_package')


# %%
################################################################################
# Utility functions
################################################################################

# Define a function to pretty print XML (from a file or XML string)
def pretty_print_xml(input):
    # Check if the input is a file path
    if os.path.isfile(input):
        # Read the content of the file
        with open(input, 'r') as file:
            xml_content = file.read()
    else:
        # Assume the input is an XML string
        xml_content = input
    
    # Parse the XML string
    dom = xml.dom.minidom.parseString(xml_content)
    # Pretty print the XML (without extra lines)
    pretty_xml_as_string = '\n'.join([line for line in dom.toprettyxml().split('\n') if line.strip()])
    # Display the pretty-printed XML as Markdown
    display(Markdown(f"```xml\n{pretty_xml_as_string}\n```"))

# Define a function to pretty print JSON (from a file or JSON string)
def pretty_print_json(input):
    # Check if the input is a file path
    if os.path.isfile(input):
        # Read the content of the file
        with open(input, 'r') as file:
            json_content = json.load(file)
    else:
        # Assume the input is an JSON string
        json_content = json.loads(input)
        
    # Pretty print the JSON
    pretty_json_as_string = json.dumps(json_content, indent=2)

    # Print the pretty JSON
    print(pretty_json_as_string)

def pretty_print_css(input_css):
    """
    Pretty prints CSS input.
    
    :param input_css: The CSS input as a string or a file path.
    """
    # Check if the input is a file path
    if os.path.isfile(input_css):
        # Read the content of the file
        with open(input_css, 'r') as file:
            css_content = file.read()
    else:
        # Assume the input is a CSS string
        css_content = input_css

    # Use jsbeautifier to pretty print the CSS
    beautifier_opts = jsbeautifier.default_options()
    beautified_css = jsbeautifier.beautify(css_content, beautifier_opts)

    # Print the pretty CSS
    print(beautified_css)



# %%
################################################################################
# Test Taker and Result API
################################################################################

results_api_url = tao_server_url + "/taoResultServer/QtiRestResults"

# Test Taker (Ghislain Hachey) Resource Identifier
testtakerUri = urllib.parse.quote(sample_testtakerUri, safe='');
# Delivery of Test 3 Resource Identifier
deliveryUri = urllib.parse.quote(sample_deliveryUri, safe='');

# Case A: Result id for delivery execution ???
resultId = urllib.parse.quote(deliveryUri, safe='');

# Or Case B: Result id for LTI delivery ???
#resultId = 'bf29e71611330b19a723e2bed6f47255';

# Construct the full URL two endpoints
# Initialize the request to get the latest results for a given test-taker and delivery
full_url1 = f"{results_api_url}/getLatest?testtaker={testtakerUri}&delivery={deliveryUri}"

# OR Initialize the request to get a specific result (by default the result identifier is the same as the delivery execution identifier)
full_url2 = f"{results_api_url}/getQtiResultXml?delivery={deliveryUri}&result={resultId}"

# Set the headers
headers = {
    'Accept': 'application/xml, application/json'
}

# Make the GET request with basic authentication
response = requests.get(full_url1, headers=headers, auth=(username, password))

# Check the response
if response.status_code == 200:
    print("Request was successful")
    #print(response.text)  # or response.json() for JSON response

    # Pretty printing XML
    pretty_print_xml(response.text)
else:
    print(f"Request failed with status code {response.status_code}")

# Make the GET request with basic authentication
response = requests.get(full_url2, headers=headers, auth=(username, password))

# Check the response
if response.status_code == 200:
    print("Request was successful")
    #print(response.text)  # or response.json() for JSON response

    # Pretty printing XML
    pretty_print_xml(response.text)
else:
    print(f"Request failed with status code {response.status_code}")

# %%
################################################################################
# Item API
################################################################################
item_api_url = tao_server_url + "/taoQtiItem/RestQtiItem"

# Item Resource Identifier
itemUri = sample_itemUri

def get_item(itemUri):
    itemUri = urllib.parse.quote(itemUri, safe='');
    # Construct the full URL
    # Initialize the request to get the latest results for a given test-taker and delivery
    full_url = f"{item_api_url}/export?id={itemUri}"
    
    # Set the headers
    headers = {
        'Accept': 'application/json, application/zip',    
    }
    
    # Make the GET request with basic authentication
    response = requests.get(full_url, headers=headers, auth=(username, password))
    
    # Check the response
    if response.status_code == 200:
        print("Request was successful, downloading the QTI package...")
        
        # Save the zip file
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
        print(f"QTI package saved to {zip_file_path}")
    
        # Extract the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"QTI package extracted to {extract_path}")
    
        # List the contents of the extracted directory
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                print(os.path.join(root, file))
    
            for file in files:
                print("\nPretty printing: {}".format(file))
                if file.endswith('.xml'):
                    pretty_print_xml(os.path.join(root, file))
                elif file.endswith('.css'):
                    pretty_print_css(os.path.join(root, file))
                else:
                    print("Unsupported file type: {}".format(file))
            
    else:
        print(f"Request failed with status code {response.status_code}")

get_item(itemUri)

# %%
################################################################################
# Test API (getItems of a test)
################################################################################
test_api_url = tao_server_url + "/taoQtiTest/RestQtiTests"

# Test Resource Identifier
testUri = urllib.parse.quote(sample_testUri, safe='');
test_items = []

# Construct the full URL
# Initialize the request to get the latest results for a given test-taker and delivery
full_url = f"{test_api_url}/getItems?testUri={testUri}"

# Set the headers
headers = {
    'Accept': 'application/json, application/xml, text/xml',
}

# Make the GET request with basic authentication
response = requests.get(full_url, headers=headers, auth=(username, password))

# Check the response
if response.status_code == 200:
    print("Request was successful")
    #print(type(response.text))
    pretty_print_json(response.text)  # or response.json() for JSON response
    test_items = response.json()["data"]
else:
    print(f"Request failed with status code {response.status_code}")

# %%
################################################################################
# Test API (Show all items of a test)
################################################################################

for item in test_items:
    print(item['itemUri'])
    get_item(item['itemUri'])

# %%
################################################################################
# Test API (exportQtiPackage)
################################################################################
test_api_url = tao_server_url + "/taoQtiTest/RestQtiTests"

# Item Resource Identifier
testUri = sample_testUri2

# Compare with previously used function, seems could be abstracted
def get_package(testUri):
    testUri = urllib.parse.quote(testUri, safe='');
    # Construct the full URL
    # Initialize the request to get the latest results for a given test-taker and delivery
    full_url = f"{test_api_url}/exportQtiPackage?testUri={testUri}"
    
    # Set the headers
    headers = {
        'Accept': 'application/json, application/zip', 
    }
    
    # Make the GET request with basic authentication
    response = requests.get(full_url, headers=headers, auth=(username, password))
    
    # Check the response
    if response.status_code == 200:
        print("Request was successful, downloading the QTI package...")

        pretty_print_json(response.text)
        
        # Extract the base64 string from the response
        base64_zip_str = response.json()['data']['qtiPackage']
        
        # Decode the base64 string
        zip_bytes = base64.b64decode(base64_zip_str)
        
        # Save the decoded bytes as a zip file
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(zip_bytes)
        print(f"QTI package saved to {zip_file_path}")
        
        # Extract the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"QTI package extracted to {extract_path}")

        # List the contents of the extracted directory
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                print(os.path.join(root, file))
    
            for file in files:
                print("\nPretty printing: {}".format(file))
                pretty_print_xml(os.path.join(root, file))
            
    else:
        print(f"Request failed with status code {response.status_code}")

get_package(testUri)

# %%

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
# %%time
###############################################################################
# This notebook focuses on data retrieval from OnlineSBA's RESTful API        #
###############################################################################

# Retrieve a single file (testing)

import requests
from lxml import etree 
import os

cwd = os.getcwd()
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
save_path = os.path.join(local_path, 'exams-xml-data-from-onlinesba/')
os.makedirs(save_path, exist_ok=True)
test_f = os.path.join(save_path, 'test.xml')

#xml_str = requests.get('http://nmctscore.com/api/exams/nmct/tests/M04/2014-2015').text
# Try one with no data
#xml_str = requests.get('http://nmctscore.com/api/exams/nmct/tests/M06/2014-2015').text
# Try one with modified standard/benchmark descriptions in the OnlineSBA
xml_str = requests.get('http://nmctscore.com/api/exams/nmct/tests/M06/2018-2019').text
# Try regex to find and replace &
import re
xml_str_fixed = re.sub(r'&([^a-zA-Z#])',r'&amp;\1',xml_str)

print(xml_str_fixed)
root = etree.fromstring(bytes(xml_str_fixed, encoding='utf8'))
#etree.fromstring(requests.get('http://nmctscore.com/api/exams/nmct/tests/M04/2014-2015').text)
data = etree.tostring(root, pretty_print=True).decode()

with open(test_f, 'w') as f:
    #print(exams_data)
    f.write(data)

# %%
# %%time
import requests
import os
from lxml import etree
import re

# Retrieve all files as identified in exams dictionary

# RESTful API endpoints like this http://rmisat.com/api/exams/misat/tests/M10/2016-2017
exams = [
    {
        'url': 'http://nmctscore.com/api/exams/',
        'exam': 'nmct',
        'tests': ['M04','M06','M08','M10','R06','R08'],
        'years': ['2014-2015','2015-2016','2016-2017','2017-2018','2018-2019']
    },   
    {
        'url': 'http://rmisat.com/api/exams/',
        'exam': 'misat',
        'tests': ['B03','B06','E01','E03','E06','E10','E12','H08','M03','M06','M10','M12','S03','S06'],
        'years': ['2011-2012','2012-2013','2013-2014','2014-2015','2015-2016','2016-2017','2017-2018','2018-2019']
    }
]

for e in exams:
    for t in e['tests']:
        for y in e['years']:       
            exams_url = e['url'] + e['exam'] + '/tests/' + t + '/' + y
            #print(exams_url)
            
            print("Retrieving data from", exams_url)
            #r = requests.get('')
            r = requests.get(exams_url)
            exams_data = r.text
            # Only needed until OnlineSBA fixes their system and return valid XML
            exams_data = re.sub(r'&([^a-zA-Z#])',r'&amp;\1', exams_data)
            exams_data_filename = os.path.join(save_path, e['exam'] + '-' + t + '-' + y + '.xml')
            
            # parse into XML
            # Try and sent email when error
            try: 
                root = etree.fromstring(bytes(exams_data, encoding='utf8'))
                exams_data_pretty = etree.tostring(root, pretty_print=True).decode()
                
                print("Start processing the file", exams_data_filename)
                with open(exams_data_filename, 'w') as f:
                    #print(exams_data)
                    f.write(exams_data_pretty)
                print("Complete processing the file", exams_data_filename)
            except:
                print("Problem with validity of", exams_url)
                
            


# %%

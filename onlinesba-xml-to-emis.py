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
# This notebook focuses on loading data retrieved from OnlineSBA's            #
# RESTful API into the Pacific EMIS database directly                         #
###############################################################################

# import everything we need here
import os
import json

# database stuff
import pyodbc

# Initial setup
test = 'MISAT' # NMCT
country = 'RMI' # FSM
cwd = os.getcwd()
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
data_dir = os.path.join(local_path, country+'/'+test+'/exams-xml-data/')
save_path = os.path.join(cwd, data_dir)
os.makedirs(save_path, exist_ok=True)

# Configuration
with open('config.json', 'r') as file:
     config = json.load(file)

# %%
# Establish a connection to the MS SQL Server
# Here this was tricky as I am running Jupyter Lab from the Windows Linux Subsystem (WSL 2) on Debian 10
# I have to install MS SQL Server Driver on Debian (https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15)
# Then I was getting SSL unsupported so I downgraded the minimum TLS version on Debian's SSL and trust self sign cert
# and a couple of hours after I got back to work...argh!
# A less experienced user should stick to running the Jupyter Lab directly in Windows
from sqlalchemy import create_engine

# Establish a database server connection
conn = """
    Driver={{ODBC Driver 17 for SQL Server}};
    Server={},{};
    Database={};
    authentication=SqlPassword;UID={};PWD={};
    TrustServerCertificate=yes;
    autocommit=True
    """.format(config['server_ip'], config['server_port'], config['database'], config['uid'], config['pwd'])

sql_conn = pyodbc.connect(conn)

cursor = sql_conn.cursor()
cursor.execute('SELECT schNo, schName FROM Schools')

for row in cursor:
    print(row)
cursor.fetchone()    


# %%
def load_file(xml_f):
    """Loads an XML file with Students Exam data for a particular exam and year into the SQL DB.

    Parameters
    ----------
    xml_f : str, required
        The filename of the XML file

    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    """

    with open(xml_f, 'r') as f:
        # Check if there is data
        xml_str = f.read()
        root = etree.fromstring(xml_str)
        #print(etree.tostring(root, pretty_print=True).decode())    
        if root.find('.//Student') is not None:
            print("Processing student data", xml_f, "into database")
            sql = 'exec pExamWrite.loadExam @xml=?, @fileReference=?, @user=?'
            params = (xml_str,'357156F1-D60F-4600-A0EC-43F249CB2CBB','ghachey@nuzusys.com')
            cursor.execute(sql, params)
            cursor.commit()
        else:
            print("There is no student data, nothing to do")
            pass


# %%
# %%time

# Now we've got a connection to the SQL Server we can load and process all the XML exams data files
# This cell is mostly for experimenting and does it with an individual file.

import os
from lxml import etree

file = 'misat-B03-2012-2013-test.xml' # test with data
#file = 'misat-B03-2011-2012-test.xml' # test without data
test_file = os.path.join(save_path, file)

# Load into the database (only if there is data)
load_file(test_file)

# %%
# %%time

# Same as above cell but loads all files in a folder with Student data

import os
from lxml import etree

# Get list of files
all_files = os.listdir(save_path)
# only files starting with misat
misat_files = [i for i in all_files if 'misat' in i]
# construct full filename
misat_files = [os.path.join(save_path, i) for i in all_files]
# process each file
[load_file(i) for i in misat_files]

# %%

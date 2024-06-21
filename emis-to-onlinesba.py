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
###############################################################################
# This notebook provides some tools for better integration between the        #
# Pacific EMIS and OnlineSBA. It does the following                           #
#   - Retrieve SchoolID, School Name, etc. to automatically produce the       #
#     entity characteristics file used to load into OnlineSBA                 #
###############################################################################

# Core stuff
import os
import json

# Data stuff
import pandas as pd # Data analysis
import xlrd # excel 
from sqlalchemy.engine import URL # SQL DB

# Pretty printing stuff
from IPython.display import display, HTML
import pprint
pp = pprint.PrettyPrinter(indent=4)

# Initial setup
test = 'MISAT' # NMCT
country = 'RMI' # FSM
cwd = os.getcwd()

# Configuration
with open('config.json', 'r') as file:
     config = json.load(file)

# %%
# Load the relevant data from EMIS database

# Establish a database server connection
conn = """
    Driver={{ODBC Driver 17 for SQL Server}};
    Server={},{};
    Database={};
    authentication=SqlPassword;UID={};PWD={};
    TrustServerCertificate=yes;
    autocommit=True
    """.format(config['server_ip'], config['server_port'], config['database'], config['uid'], config['pwd'])

connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn})

from sqlalchemy import create_engine
engine = create_engine(connection_url)

query = """
SELECT [schNo] AS SCHOOLID
      ,[schName] AS SCHOOLNAME
	  ,I.iName AS ISLAND
	  ,D.dName AS DISTRICT
	  ,A.authName AS AUTHORITY
	  ,AT.codeDescription AS AUTHORITYTYPE
	  ,AG.codeDescription AS URBAN
      ,[schClosed] AS CLOSED
      ,[schCloseReason] AS CLOSEDREASON
  FROM [dbo].[Schools] S
  INNER JOIN Islands I ON S.iCode = I.iCode
  INNER JOIN Districts D ON I.iGroup = D.dID
  INNER JOIN Authorities A ON S.schAuth = A.authCode
  INNER JOIN lkpAuthorityType AT ON A.authType = AT.codeCode
  INNER JOIN lkpAuthorityGovt AG ON AT.codeGroup = AG.codeCode
"""

query_ethnicity = """SELECT [codeDescription] AS ETHNICITY FROM [dbo].[lkpEthnicity]"""

with engine.begin() as sql_conn:
    df_schools_x = pd.read_sql_query(query, sql_conn)
    display(df_schools_x)
    df_ethnicities = pd.read_sql_query(query_ethnicity, sql_conn)
    display(df_ethnicities)

# %%
df_schools = df_schools_x.copy()
df_schools = df_schools[['SCHOOLID','SCHOOLNAME','ISLAND','DISTRICT','URBAN']]
display(df_schools)

s_islands = df_schools['ISLAND'].drop_duplicates().reset_index(drop=True)
s_islands.rename('UNIQUEISLANDNAME', inplace=True)
display(s_islands)

s_rubric_levels = pd.Series(data=['Beginning','Developing','Proficient','Advanced'], name='RUBRICLEVELS')
display(s_rubric_levels)

s_strand_layers = pd.Series(data=['Indicator','Benchmark','Standard'], name='STRANDLAYERS')
display(s_strand_layers)

s_subject = pd.Series(data=['B:Reading (Marshallese)','M:Math','N:Math Form B',
                            'E:English','H:High School Entrance','S:Science'], name='SUBJECT')
display(s_subject)


# %%
# Write various DataFrame into Excel to examine (testing)
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')

#s = os.path.join(local_path, country + '/entity-characteristics-test.xlsx')
# Write various DataFrame into Excel (real one)
s = os.path.join(local_path, country + '/onlinesba-load-files-csv/'+ country +'-entity-characteristics.xlsx')

filename = os.path.join(cwd, s)
with pd.ExcelWriter(filename) as writer:
    # add DataFrames you want to write to Excel here
    df_schools.to_excel(writer, index=False, sheet_name='RMIEntityCharacteristics', engine='openpyxl')
    s_islands.to_excel(writer, index=False, sheet_name='RMIEntityCharacteristics', startcol=5, engine='openpyxl')
    df_ethnicities.to_excel(writer, index=False, sheet_name='RMIEntityCharacteristics', startcol=6, engine='openpyxl')
    s_rubric_levels.to_excel(writer, index=False, sheet_name='RMIEntityCharacteristics', startcol=7, engine='openpyxl')
    s_strand_layers.to_excel(writer, index=False, sheet_name='RMIEntityCharacteristics', startcol=8, engine='openpyxl')
    s_subject.to_excel(writer, index=False, sheet_name='RMIEntityCharacteristics', startcol=9, engine='openpyxl')

# %%

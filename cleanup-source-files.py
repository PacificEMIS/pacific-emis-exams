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
# This notebook provides some cleanup tools                                   #
# Tools include the following                                                 #
#   - Remove all files in a directory tree that is not an AllSchool           #
#   - Combined all schools in a directory into a AllSchools (when missing)    #
###############################################################################

# Core stuff
import os
from pathlib import Path
import re
import json

# Data stuff
import pandas as pd # Data analysis
import xlrd # excel 

# Configuration (initial setup)
with open('config.json', 'r') as file:
     config = json.load(file)

year_to_load = config['load_year']
test = config['test']
country = config['country']
cwd = os.getcwd()


# %%
def load_excel_to_df(filename):
    """Loads an Excel filename to a Pandas DataFrame.

    Parameters
    ----------
    filename : str, required
        The filename of the excel file to load

    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    DataFrame
    """
    file_path = Path(filename)
    file_extension = file_path.suffix.lower()[1:]

    if file_extension == 'xlsx':
        df = pd.read_excel(filename, index_col=None, header=0, engine='openpyxl')
    elif file_extension == 'xls':
        df = pd.read_excel(filename, index_col=None, header=0)
    elif file_extension == 'csv':
        df = pd.read_csv(filename, index_col=None, header=0)
    else:
        raise Exception("File not supported")

    return df


# %%
# Testing the regex
name = 'AllSchool_A03_2008-09_Results1.xls'
p = re.compile('AllSchool_.*_Results[0-9]?\.x.*', re.IGNORECASE)
p.match(name)

# %%
# %%time
# Cleanup and only keep the AllSchools exams file
# (~6 seconds on iMac with i9 CPU and 32GB RAM)
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
data_dir = os.path.join(local_path, country+'/'+test)
path = os.path.join(cwd, data_dir)

if year_to_load != 'all':
    path = os.path.join(path, year_to_load)
    
p = re.compile('AllSchools_.*_Results[0-9]?\.x.*', re.IGNORECASE)

for root, directories, files in os.walk(path, topdown=False):
    for name in files:
        if p.match(name):
            pass
            #print(os.path.join(root, name))
        else:            
            print('Deleting file: ', os.path.join(root, name))
            os.remove(os.path.join(root, name))
    #for name in directories:
    #    print(os.path.join(root, name))

# %%
os.listdir(os.path.join(local_path, 'RMI/MISAT/MISAT 2017/Gr10Math2017'))

# %%
# After cleanup verify each directory has the AllSchools exams file
for root, directories, files in os.walk(path, topdown=False):
    for d in directories:
        if root[len(path):].count(os.sep) == 1:
            d_abs = os.path.join(root, d)
            
            # List those with multiple (or missing) AllSchools files
            files = os.listdir(d_abs)  
            if len(files) == 0:
                print("Missing AllSchools file in directory {}".format(d_abs))
        
            if len(files) > 1:
                print("Directory {}".format(d_abs))
                for filename in files:
                    print("Contain file {}".format(filename))

# %%
# Combined all schools in a directory into a single AllSchools
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
path = os.path.join(local_path, country+'/combine-from-schools')


df_student_results_list = []

for root, directories, files in os.walk(path, topdown=False):
    for name in files:
        filename = os.path.join(root, name)
        print('Loading into DataFrame:', filename)
        try:
            df_student_results_list.append(load_excel_to_df(filename))
        except Error as e:
            print('Problem loading:', filename)
            print('Error was', e)            

print('Completed loading excel files')

df_all_schools_student_resuls = pd.concat(df_student_results_list)
df_all_schools_student_resuls

# Write resulting AllSchool DataFrame into Excel
filename = os.path.join(path, 'AllSchools_M10_2017-18_Results.xlsx')
with pd.ExcelWriter(filename) as writer:
    df_all_schools_student_resuls.to_excel(writer, index=False, sheet_name='Responses', engine='openpyxl')
    
print('Completed writing resulting AllSchool DataFrame to file')

# %%

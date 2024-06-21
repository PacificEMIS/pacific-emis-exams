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
# This notebook focuses on processing data from excel spreadsheet directly    #
# into another format ready to load into OnlineSBA. It's focused on producing #
# the items meta file                                                         #
# This notebook should work on the same set of SOE assessment files as        #
# the notebook soe-to-onlinesba for best results                              #
#                                                                             #
# It is also used to process raw SOE workbooks and flag data issues           #
###############################################################################
# Core stuff
import os
from pathlib import Path
import re
import json

# Data stuff
import pandas as pd # Data analysis

# Pretty printing stuff
from tqdm.notebook import trange, tqdm

# Configuration (initial setup)
with open('config.json', 'r') as file:
     config = json.load(file)
test = config['test']
country = config['country']
cwd = os.getcwd()

year_to_load = config['load_year']


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
        df_student_results = pd.read_excel(filename, index_col=None, header=0, engine='openpyxl')
    elif file_extension == 'xls':
        df_student_results = pd.read_excel(filename, index_col=None, header=0)
    elif file_extension == 'csv':
        df_student_results = pd.read_csv(filename, index_col=None, header=0)
    else:
        raise Exception("File not supported")

    return df_student_results


# %%
# Load a single SOE Assessment workbook (for testing,)
# in particular the sheet with the raw data
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2019/3GrEng2019/AllSchools_A03_2018-19_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2012/6grEng12/AllSchools_A06_2011-12_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2010/3GrMath/AllSchools_M03_2009-10_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2012/6GrEng2012/AllSchools_A06_2011-12_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2009/3GrKM2009/AllSchools_B03_2008-09_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2014/Gr6Eng2014/AllSchools_A06_2013-14_Results.xls')
filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2017/Gr3Eng2017/AllSchools_A03_2016-17_Results.xls')
#filename = os.path.join(local_path, 'FSM/NMCT/NMCT 2021/AllSchools_R08_2020-21_Results.xls')

df_student_results = load_excel_to_df(filename)
print('df_student_results')
display(df_student_results)

# %%
# %%time
# Load all SOE Assessment workbook inside a directory
# (~50 seconds on iMac with i9 CPU and 32GB RAM)
path = os.path.join(local_path, country+'/'+test+'/')

if year_to_load != 'all':
    path = os.path.join(path, year_to_load)
    
df_student_results_list = []

for root, directories, files in os.walk(path, topdown=False):
    for name in files:
        filename = os.path.join(root, name)
        print('Loading into DataFrame:', filename)
        try:
            df_student_results_list.append(load_excel_to_df(filename))
            #df_student_results_list[name] = load_excel_to_df(filename)
        except:
            print('Problem loading:', filename)
            #print('Error was:', )            

print('Completed loading excel files')

# %%
l = 'Item_002_AS0302010102m_aaa'
'_'.join(l.split('_', 2)[2:])


# %%
def are_consecutive(l):
    """Simply checks the items are all consecutive (e.g. Item_001, Item_002, etc)
    
    Parameters
    ----------
    l : List of items
    
    Returns
    -------
    True if the Items are numbered consecutively
    """    
    l = [int(i.split('_')[1]) for i in l]
    return l == list(range(min(l), max(l)+1))

def has_duplicates(l):
    """Simply checks the items for any duplicates (e.g. Item_001_AS0302010102m_aaa and Item_002_AS0302010102m_aaa)
    
    Or is this a valid scenario?
    
    Parameters
    ----------
    l : List of items
    
    Returns
    -------
    True if the Items have duplicates metadata
    """    
    l = ['_'.join(l.split('_', 2)[2:]) for i in l]
    return len(l) == len(set(l))

def create_series(df, accept_testid_alt: False, testing: False):
    """Create a pandas series containing meta data from a SOE Assessment responses raw DataFrame.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame, required
        The DataFrame to produce the Series

    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    pandas.core.serries.Series
    """
    # Create the Series for a particular exams
    sy = df['SchoolYear'].iloc[0]
    if not re.match('20\d{2}-\d{2}$', sy):
        tqdm.write('Year format incorrect')
    testid = df['TestID'].iloc[0]
    testid_chars = list(testid)
    testid_chars.insert(1,'S')
    testid_alt = "".join(testid_chars)
    testname = df['TestName'].iloc[0]
    
    if testid == 'A12' or testid == 'B12':
        testid_alt = 'MS12'        
    
    # this also excludes items with _zzz
    items = df.columns[df.columns.str.startswith('Item_') & ~df.columns.str.contains('_zzz')].tolist()
    
    if testing:
        tqdm.write("testid: {}".format(testid))
        tqdm.write("testid_chars: {}".format(testid_chars))
        tqdm.write("testid_alt: {}".format(testid_alt))
        tqdm.write("testname: {}".format(testname))
        tqdm.write("items: {}".format(items))
        
    # Check for inconsistencies in Test Items
    # TestID must be the same as found in the Items (e.g. MS03 is in Item_055_MS0304010103h_ddd)
    test_item_not_matching = False 
    test_missing_items = False
    test_are_consecutive = False
    test_has_duplicates = False
    
    # Test for items heads to match the expected Test ID
    for i in items:
        if accept_testid_alt:
            if not testid in i and not testid_alt in i:
                test_item_not_matching = True
        else:
            if not testid in i:
                test_item_not_matching = True
    
    try:
        if test_item_not_matching and testid != 'H08':
            tqdm.write("Inconsistency detected in the test {} for year {}: Items test ID not matching test ID (i.e. The TestID says {} but items look like {})".format(testname, sy, testid, items[0]))
        if len(items) == 0:
            test_missing_items = True
            tqdm.write("Inconsistency detected in the test {} for year {}: There does not seem to be any items (e.g. Item_001_MS0301010101e_aaa, Item_002_MS0301010101e_aaa, Item_004_MS0301010101e_aaa missing Item_003)".format(testname, sy))             
        if not are_consecutive(items):
            test_are_consecutive = True
            tqdm.write("Inconsistency detected in the test {} for year {}: Items not correctly ordered (e.g. Item_001_MS0301010101e_aaa, Item_002_MS0301010101e_aaa, Item_004_MS0301010101e_aaa missing Item_003)".format(testname, sy)) 
        if has_duplicates(items):
            test_has_duplicates = True
            tqdm.write("Inconsistency detected in the test {} for year {}: Items contain duplicated metadata(e.g. Item_001_MS0301010101e_aaa and Item_002_MS0301010101e_aaa have the same MS0301010101e_aaa)".format(testname, sy))
        #if test_inconsistencies:
        #    tqdm.write("")
    except:
        pass
    
    test_meta = [sy, test, testname, len(items), testid]
    test_meta = test_meta + items
    
    s = pd.Series(test_meta)
    return s


# %%
# Create a single Series from SOE Assessment workbook (for testing,)
#t = df_student_results
#t.at[0,'SchoolYear'] = '2009-2010'
s_exam_meta_data = create_series(df_student_results, accept_testid_alt=True, testing=True)
print('s_exam_meta_data')
display(s_exam_meta_data)

# %%
# %%time

# Create a list of Series from all SOE Assessment workbooks (for testing,)
# Working with all student exams files (~28 seconds on iMac with i9 CPU and 32GB RAM)
s_exam_meta_data_list = []

for df in tqdm(df_student_results_list):
    s_exam_meta_data_list.append(create_series(df, accept_testid_alt=True, testing=False))

# %%
# Re-assemble list of series into DataFrames based on the school year
years = []
df_exam_meta_data_list = []

# First create a unique list of all the years for which we have exams data
for s in s_exam_meta_data_list:
    # Get the year
    years.append(s[0])
years = list(dict.fromkeys(years))
print(years)

# Create a dictionary of year to exams meta data DataFrame starting with empty DataFrames
exam_meta_data_dict = {}
for year in years:
    exam_meta_data_dict[year] = pd.DataFrame()
#exam_meta_data_dict
#display(s_exam_meta_data_list)

print('Processing exam meta data files')

# Go through the list of series and populate their respective DataFrames
for s in tqdm(s_exam_meta_data_list):
    # e.g. exam_meta_data_dict['2019-20']
    #exam_meta_data_dict[s[0]]
    try:
        #tqdm.write('Processing exam meta data for test id {} and year {}'.format(s[4], s[0]))
        df1 = exam_meta_data_dict[s[0]]
        df2 = pd.DataFrame()
        df2[s[0]+'-'+s[4]] = s.reset_index(drop=True)   
        df3 = df1.join(df2, how='outer')
        exam_meta_data_dict[s[0]] = df3
    except ValueError as e:
        tqdm.write('File contains the wrong TestID. Fix file with TestID of {} to match Test Name of {} in year {}'.format(s[4], s[2], s[0]))        
        tqdm.write('Error was {}'.format(e))
    except Exception as e:
        tqdm.write('Unknown error {}'.format(e))

#exam_meta_data_dict['2011-12']

# %%
# Write processed data back into excel (or CSV directly)
# Working with all student exams files

for year, df in tqdm(exam_meta_data_dict.items()):
    # Remove the year row? They don't seem to need it
    df = df.drop([0])
    try: 
        #exam_year_meta = 'data/'+country+''/onlinesba-load-files-xls/' + test + '-' + year + '.xlsx'        
        exam_year_meta = os.path.join(local_path, country+'/onlinesba-load-files-csv/' + test + '-' + year + '.csv')
        filename = os.path.join(cwd, exam_year_meta)        
        df.to_csv(filename, index=False)
        #with pd.ExcelWriter(filename) as writer:
        #    # add DataFrames you want to write to Excel here
        #    df.to_excel(writer, index=False, sheet_name='Sheet1', engine='openpyxl', header=False)
        
        #tqdm.write('Writing {}'.format(filename))
    except TypeError as e:
        tqdm.write('TypeError {}'.format(e))
    except Exception as e:
        tqdm.write('Unknown error {}'.format(e)) 

# %%

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
# This notebook contains a collection of useful tools used with SOE Assessment#
# Current list of tools:                                                      #
#  * List indicators with less then 4 items (or not multiple of 4 items)      #
#  * Bin tool (show equal width bins vs custom SOE bins)                      #
###############################################################################
# Core stuff
import os
from pathlib import Path
import re
import json

# Data stuff
import pandas as pd # Data analysis
import numpy as np

# Pretty printing stuff
from IPython.display import display, HTML
import pprint
pp = pprint.PrettyPrinter(indent=4)

# Configuration (initial setup)
with open('config.json', 'r') as file:
     config = json.load(file)

test = config['test']
country = config['country']
cwd = os.getcwd()

if country == 'FSM':
    achievement_levels = ['well below competent', 'approaching competent', 'minimally competent', 'competent'] # NMCT
elif country == 'RMI':
    achievement_levels = ['Beginning', 'Developing', 'Proficient', 'Advanced'] # MISAT
else:
    achievement_levels = ['Level 1', 'Level 2', 'Level 3', 'Level 4'] # Default


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
###############################################################################
# Responses Sheet                                                             #
###############################################################################

# Load a single SOE Assessment workbook (for testing,)
# in particular the sheet with the raw data
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')

#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2019/3GrEng2019/AllSchools_A03_2018-19_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2012/6grEng12/AllSchools_A06_2011-12_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2009/3GrEng09/AllSchools_A03_2008-09_Results.xls')
filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2021/Gr6Math2021/AllSchools_M06_2020-21_Results.xls')

df_student_results = load_excel_to_df(filename)
print('df_student_results')
display(df_student_results)

# %%
# %%time
###############################################################################
# Responses Sheet (all)                                                       #
###############################################################################

# Load all SOE Assessment workbook inside a directory
# (~50 seconds on iMac with i9 CPU and 32GB RAM)
cwd = os.getcwd()
path = os.path.join(cwd, 'data/'+country+'/'+test+'/')

df_student_results_list = []

for root, directories, files in os.walk(path, topdown=False):
    for name in files:
        filename = os.path.join(root, name)
        print('Loading into DataFrame:', filename)
        try:
            df_student_results_list.append(load_excel_to_df(filename))
        except:
            print('Problem loading:', filename)
            #print('Error was:', )            

print('Completed loading excel files')

# %%
# %%time
# e.g. {'A.6.2.1.4': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa', etc.]}
indicators_items = {}
# e.g. {'A.6.2.1': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa', etc.]}
benchmarks_items = {}
# e.g. {'A.6.2': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa', etc.]}
standards_items = {}

def compile_items(item, test='N/A', year='N/A'):
    """ A function to compile the related items into their indicators (e.g. Test.Grade.Standard.Benchmark.Indicator), benchmarks,
    standards.

    Parameters
    ----------
    item : String, required
        The item string (e.g. Item_002_AS0602010402M_aaa)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    Nothing
    """
    item_meta = item.split('_')
    item_parts = list(item_meta[2])
    indicator = (test, year, item_parts[0] + '.' + item_parts[3] + '.' + item_parts[5] + '.' + item_parts[7] + '.' + item_parts[9])
    benchmark = (test, year, item_parts[0] + '.' + item_parts[3] + '.' + item_parts[5] + '.' + item_parts[7])
    standard = (test, year, item_parts[0] + '.' + item_parts[3] + '.' + item_parts[5])
    
    # Check if indicator already added, if not add it
    if indicator in indicators_items:       
        indicators_items[indicator].append(item)
    else:
        indicators_items[indicator] = [item]
        
    # Check if benchmark already added, if not add it
    if benchmark in benchmarks_items:       
        benchmarks_items[benchmark].append(item)
    else:
        benchmarks_items[benchmark] = [item]    
        
    # Check if standard already added, if not add it
    if standard in standards_items:       
        standards_items[standard].append(item)
    else:
        standards_items[standard] = [item]        

for df in df_student_results_list:
    test = df['TestID'][0]
    year = df['SchoolYear'][0]
    cols = df.columns.values
    cols_items = [i for i in cols if 'Item_' in i]

    for i in cols_items:
        compile_items(i, test, year)
 
# output too long with all SOE workbooks processed
#print('Indicators items')
#print('----------------')
#pp.pprint(indicators_items)
#print('Benchmarks items')
#print('----------------')
#pp.pprint(benchmarks_items)
#print('Standards items')
#print('----------------')
#pp.pprint(standards_items)

# %%
# Check list of used TestNames in SOE workbooks throughout the years
for df in df_student_results_list:
    #print(df['TestID'])
    test = df['TestName'][0]
    print(test)

# %%
# Cycle through the indicators items and count/identify the ones that
#  * have less than 4 items
#  * do not have a number of item that is a multiple of 4 (4, 8, 12, etc.) items

indicators_without_items = []
indicators_less_than_four = []
indicators_not_multiple_of_four = []

for indicator in indicators_items:
    #print(len(indicators_items[indicator]))
    if (len(indicators_items[indicator]) == 0):
        indicators_without_items.append(indicator)    
    elif (len(indicators_items[indicator]) < 4):
        indicators_less_than_four.append((indicator, str(len(indicators_items[indicator]))+' items'))
    elif (len(indicators_items[indicator]) % 4 != 0):
        indicators_not_multiple_of_four.append((indicator, str(len(indicators_items[indicator]))+' items'))

print('Number of Indicators with less than 4 items')
print('-------------------------------------------')
pp.pprint(indicators_less_than_four)
print(len(indicators_less_than_four))
print('Number of Indicators with number of items that is not a multiple of 4')
print('---------------------------------------------------------------------')
pp.pprint(indicators_not_multiple_of_four)
print(len(indicators_not_multiple_of_four))
print('Number of Indicators without any items')
print('--------------------------------------')
pp.pprint(indicators_without_items)
print(len(indicators_without_items))

# %%
# Cycle through the benchmark items and count/identify the ones that
#  * have less than 4 items
#  * do not have a number of item that is a multiple of 4 (4, 8, 12, etc.) items

benchmarks_without_items = []
benchmarks_less_than_four = []
benchmarks_not_multiple_of_four = []

for benchmark in benchmarks_items:
    #print(len(benchmarks_items[benchmark]))
    if (len(benchmarks_items[benchmark]) == 0):
        benchmarks_without_items.append(benchmark)    
    elif (len(benchmarks_items[benchmark]) < 4):
        benchmarks_less_than_four.append((benchmark, str(len(benchmarks_items[benchmark]))+' items'))
    elif (len(benchmarks_items[benchmark]) % 4 != 0):
        benchmarks_not_multiple_of_four.append((benchmark, str(len(benchmarks_items[benchmark]))+' items'))

print('Number of benchmarks with less than 4 items')
print('-------------------------------------------')
pp.pprint(benchmarks_less_than_four)
print(len(benchmarks_less_than_four))
print('Number of benchmarks with number of items that is not a multiple of 4')
print('---------------------------------------------------------------------')
pp.pprint(benchmarks_not_multiple_of_four)
print(len(benchmarks_not_multiple_of_four))
print('Number of benchmarks without any items')
print('--------------------------------------')
pp.pprint(benchmarks_without_items)
print(len(benchmarks_without_items))

# %%
# Playing with Bin values into discrete intervals.

# Example with IntervalIndex. 
# I actually prefer using int (for equal bins) or sequence of scalar (for non-uniform width/edges)
#bins = pd.IntervalIndex.from_tuples([(0, 1), (2, 3), (4, 5)])
#display(bins)
#pd.cut([0, 0.5, 1.5, 2.5, 4.5], bins, retbins=True, include_lowest=True)

print('Shows for each total number of items correct what level would be achieved')
print('=========================================================================')
print()

s1 = pd.Series(np.array([0, 1]))
c1a = pd.cut(s1, 4, labels=achievement_levels, retbins=True, right=True) # Default
c1b = pd.cut(s1, [-0.002,  -0.001 ,  0.5  ,  0.75 ,  1. ], labels=achievement_levels, retbins=True, include_lowest=True) # SOE
print('Bins with 1 Item')
print('-----------------')
display('Equal width bins', c1a)
display('SOE equivalent bins', c1b)
print()

s2 = pd.Series(np.array([0, 1, 2]))
c2a = pd.cut(s2, 4, labels=achievement_levels, retbins=True, right=True)
c2b = pd.cut(s2, [-0.002,  -0.001  ,  0.999   ,  1.5  ,  2.], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 2 Items')
print('-----------------')
display('Equal width bins', c2a)
display('SOE equivalent bins', c2b)
print()

s3 = pd.Series(np.array([0, 1, 2, 3]))
c3a = pd.cut(s3, 4, labels=achievement_levels, retbins=True, right=True)
c3b = pd.cut(s3, [-0.003,  0.75 ,  1.5  ,  2.25 ,  3.], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 3 Items')
print('-----------------')
display('Equal width bins', c3a)
display('SOE equivalent bins', c3b)
print()

s4 = pd.Series(np.array([0, 1, 2, 3, 4]))
c4a = pd.cut(s4, 4, labels=achievement_levels, retbins=True, right=True)
#c4b = pd.cut(s4, [0,1,2,3,4], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 4 Items')
print('-----------------')
display('Equal width bins', c4a)
#display('SOE equivalent bins', c4b)
print()

s5 = pd.Series(np.array([0, 1, 2, 3, 4, 5]))
c5a = pd.cut(s5, 4, labels=achievement_levels, retbins=True, right=True)
c5b = pd.cut(s5, [-0.005,  1.25 ,  3.5  ,  4.75 ,  5.], labels=achievement_levels, retbins=True, right=True, include_lowest=True)
print('Bins with 5 Items')
print('-----------------')
display('Equal width bins', c5a)
display('SOE equivalent bins', c5b)
print()

s8 = pd.Series(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8]))
c8a = pd.cut(s8, 4, labels=achievement_levels, retbins=True, right=True)
#c8b = pd.cut(s8, [0,2,4,6,8], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 8 Items')
print('-----------------')
display('Equal width bins', c8a)
#display('SOE equivalent bins', c8b)
print()

s9 = pd.Series(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
c9a = pd.cut(s9, 4, labels=achievement_levels, retbins=True, right=True)
c9b = pd.cut(s9, [-0.009,  4.25 ,  6.5  ,  7.75 ,  9. ], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 9 Items')
print('-----------------')
display('Equal width bins', c9a)
display('SOE equivalent bins', c9b)
print()

s11 = pd.Series(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
c11a = pd.cut(s11, 4, labels=achievement_levels, retbins=True, right=True)
c11b = pd.cut(s11, [-0.011,  5.75,  7.50,  9.25,  11.0], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 11 Items')
print('-----------------')
display('Equal width bins', c11a)
display('SOE equivalent bins', c11b)
print()

s12 = pd.Series(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
c12a = pd.cut(s12, 4, labels=achievement_levels, retbins=True, right=True)
#c12b = pd.cut(s12, [0,3,6,9,12], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 12 Items')
print('-----------------')
display('Equal width bins', c12a)
#display('SOE equivalent bins', c12b)
print()

s40 = pd.Series(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                          21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]))
c40a = pd.cut(s40, 4, labels=achievement_levels, retbins=True, right=True)
#c40b = pd.cut(s40, [0,10,20,30,40], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 40 Items')
print('-----------------')
display('Equal width bins', c40a)
#display('SOE equivalent bins', c40b)
print()

# %%
# Some other higher number of items (standards and whole test)
s40 = pd.Series(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                         11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                         21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                         31, 32, 33, 34, 35, 36, 37, 38, 39, 40,]))
c40a = pd.cut(s40, 4, labels=achievement_levels, retbins=True, right=True)
c40b = pd.cut(s40, [0,10,20,30,40], labels=achievement_levels, retbins=True, include_lowest=True)
print('Bins with 40 Items')
print('-----------------')
display('Equal width bins', c40a)
display('SOE equivalent bins', c40b)
print()

# %%

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
# This notebook is a SOE Assessment equivalent re-engineered to have a        #
# complete undersanding of exams data in countries using it.                  #
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

# Plotting stuff
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable

# Configuration (initial setup)
with open('config.json', 'r') as file:
     config = json.load(file)

test = config['test']
country = config['country']
cwd = os.getcwd()

descriptions_file = test+"-descriptions.py"

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
        df_student_results = pd.read_excel(filename, index_col=None, header=0, engine='openpyxl')
    elif file_extension == 'xls':
        df_student_results = pd.read_excel(filename, index_col=None, header=0)
    elif file_extension == 'csv':
        df_student_results = pd.read_csv(filename, index_col=None, header=0)
    else:
        raise Exception("File not supported")

    return df_student_results


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
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2010/6GrEng2010/AllSchools_A06_2009-10_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2019/Gr3Eng2019/AllSchools_A03_2018-19_Results.xls')
filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2021/Gr6Math2021/AllSchools_M06_2020-21_Results.xls')
#filename = os.path.join(local_path, 'RMI/MISAT/MISAT 2020/Gr8HSET2020/AllSchools_H08_2019-20_Results.xls')
#filename = os.path.join(local_path, 'FSM/NMCT/NMCT 2021/AllSchools_R08_2020-21_Results.xls')

df_student_results = load_excel_to_df(filename)
print('df_student_results')
display(df_student_results)


# %%
# Rough school filtering. Just uncomment when needed.
#display(df_student_results['SchoolName'].unique())

#df_student_results = df_student_results[df_student_results['SchoolName'] == 'Aerok A']
#print('df_student_results')
#display(df_student_results)

# %%
# %%time
###############################################################################
# NOT NEEDED                                                                  #
# Responses Sheet (all)                                                       #
###############################################################################

# Load all SOE Assessment workbook inside a directory
# (~50 seconds on iMac with i9 CPU and 32GB RAM)
#cwd = os.getcwd()
#path = os.path.join(cwd, 'data/'+country+'/'+test+'/')

#df_student_results_list = []

#for root, directories, files in os.walk(path, topdown=False):
#    for name in files:
#        filename = os.path.join(root, name)
#        print('Loading into DataFrame:', filename)
#        try:
#            df_student_results_list.append(load_excel_to_df(filename))
#        except:
#            print('Problem loading:', filename)
#            #print('Error was:', )            

#print('Completed loading excel files')

# %%
###############################################################################
# Scores Sheet                                                                #
###############################################################################
def score(answer, item):
    """ Scores the answer.

    Parameters
    ----------
    answer : String, required
        The student's answer to an item (e.g. A, B, BLANK)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    1 is correct, 0 if incorrect
    """
    if type(answer) == float:
        # Float is currently assumed to be a wrong answer
        # (seen in some of the high school test last item)
        return 0
    elif answer.upper() == item[-1].upper():
        return 1
    else:
        return 0

df_student_results_scores = df_student_results.copy()

cols = df_student_results_scores.columns.values
cols_items = [i for i in cols if 'Item_' in i]
cols_items.sort()

for item in cols_items:
    df_student_results_scores[item] = df_student_results_scores[item].apply(score, item, args=(item,))
display(df_student_results_scores)

# %% [markdown]
# From Phil Geeves' NDOE NSTT Reports for computing benchmark levels for students
#
# # Appendix 1 Determining achievement levels for benchmarks
#
# The FSM curriculum is divided into subject areas, standards, year levels and benchmarks.
# The NMCT tests assesses each student as being at one of four achievement levels against
# each benchmark:
#
# - "competent"
# - "minimally competent"
# - "approaching competent"
# - "well below competent"
#
# The test is multiple choice, with, usually, four questions being used to assess the level of
# achievement of any student. To be considered competent, all four questions must be
# answered correctly.
#
# For some seven benchmarks (out of 83 in total) there are more than 4 questions relating to
# the benchmarks. These are organised in sets of 4 questions relating to a particular 'indicator'
# associated with the benchmark. Two benchmarks have 12 questions and five have 8
# questions. When determining the achievement level, the following business rules were
# used.
#
# <table>
#     <caption>Minimum number of correct answers required for each achievement level</caption>
#     <thead>
#         <tr>
#             <th>Achievement Level</th>
#             <th colspan="3">Number of questions contributing to the benchmark assessment</th>            
#         </tr>
#         <tr>
#             <th></th>
#             <th>4</th>
#             <th>8</th>
#             <th>12</th>
#         </tr>
#     </thead>
#     <tbody>
#         <tr>
#             <td>well below competent</td>
#             <td style="text-align: center;">0</td>
#             <td style="text-align: center;">0</td>
#             <td style="text-align: center;">0</td>
#         </tr>
#         <tr>
#             <td>approaching competent</td>
#             <td style="text-align: center;">2</td>
#             <td style="text-align: center;">3</td>
#             <td style="text-align: center;">4</td>
#         </tr>
#         <tr>
#             <td>minimally competent</td>
#             <td style="text-align: center;">3</td>
#             <td style="text-align: center;">5</td>
#             <td style="text-align: center;">7</td>
#         </tr>
#         <tr>
#             <td>competent</td>
#             <td style="text-align: center;">4</td>
#             <td style="text-align: center;">7</td>
#             <td style="text-align: center;">10</td>
#         </tr>
#     </tbody>
# </table>

# %%
###############################################################################
# AggregateScores Sheet                                                       #
###############################################################################
df_student_results_aggscores = df_student_results_scores.copy()

###############################################################################
# Utility functions
###############################################################################

def get_level(s):
    """ A function to get a level (i.e. Beginning, Developing, Advanced, Proficient)
    from a string of format A.6.2.1_L1Percent. The level is in the string itself (L1 -> Beginning).

    Parameters
    ----------
    s : String, required
        The level string representing an benchmark, standard or test (e.g. A.6.2.1_L1Percent)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    level : String
    """ 
    levels = {
        'L1': 'Beginning',
        'L2': 'Developing',
        'L3': 'Proficient',
        'L4': 'Advanced',
    }
    try: 
        level = levels[s.split('_')[1].split('Percent')[0]]
    except:
        level = levels[s.split('Percent')[0]]
    return level

def get_bins(total_possible_scores, metric):
    """ Getting total possible score is really optional code
    since the bins are essentially 4 equal bins no matter what the total items 
    for an indicator (or benchmark, standard, test). But it is included here in case
    one would want to adjust the width of the bins.
    
    Otherwise, the bins could simply be set to 4 in pandas.cut
    and it would produce the same results as below.

    Parameters
    ----------
    total_possible_scores : Integer, required
        The total possible for a particular indicator or benchmark
        
    metric: String, required
        Added mostly for troubleshooting (whether we dealing with indicators, benchmarks, standards or test)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    bins : List
        The Scalar representing the bins
    """ 
    
    if len(total_possible_scores) != 1:
        print('Something is wrong. There should not be more then one total unique scores for a particular benchmark.')
        
    total_possible_score = total_possible_scores[0]
    
    # Here I actually need all possible (expected) bins defined as arrays since otherwise it will divide based on the
    # bin edges and this would provide false results. For example, total items is 40 the bins should be [0,10,20,30,40]
    # but if I just pass bins=4 (for 4 equal sized bins) and the dataset sets only include total correct answer of say 12, 13, 8, and 9
    # the 4 bins will be between range of 8-13 (and not 0-40)
    # in practice this as affected mostly smaller datasets with not all possible edges achieved.
    #
    # WARNING: The below remains currently prone to rare errors as I have just added the most common possible ranges.
    if  total_possible_scores[0] == 1:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        print("""WARNING: number of items less than 4 (i.e. only {}). SOE vs EMIS results may vary a little.""".format(1))
        # Using the same binning as SOE.
        bins = [-0.002,  -0.001 ,  0.5  ,  0.75 ,  1. ]        
    elif  total_possible_scores[0] == 2:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))        
        print("""WARNING: number of items less than 4 (i.e. only {}). SOE vs EMIS results may vary a little.""".format(2))
        # Using the same binning as SOE.
        bins = [-0.002,  -0.001  ,  0.999   ,  1.5  ,  2.]
    elif  total_possible_scores[0] == 3:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))        
        print("""WARNING: number of items less than 4 (i.e. only {}). SOE vs EMIS results may vary a little.""".format(3))
        # Using the same binning as SOE.
        bins = [-0.003,  0.75 ,  1.5  ,  2.25 ,  3.]
    elif  total_possible_scores[0] == 4:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,1,2,3,4]
    elif total_possible_scores[0] == 8:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,2,4,6,8]
    elif total_possible_scores[0] == 12:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,3,6,9,12]
    elif total_possible_scores[0] == 16:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,4,8,12,16]
    elif total_possible_scores[0] == 20:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,5,10,15,20]
    elif total_possible_scores[0] == 24:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,6,12,18,24]    
    elif total_possible_scores[0] == 40:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,10,20,30,40]   
    elif total_possible_scores[0] == 60:
        #print('Total bins {} with {}.'.format(total_possible_scores, metric))
        bins = [0,15,30,45,60]   
    else:
        print("""WARNING: Unexpected number of bins {} with {}. When you see this, it is possible a new custom bins would be required for correct results""".format(total_possible_scores[0], metric))        
        # If none of the above total numner of possible score (i.e. correct items)
        # then simply be lazy and fallback to 4 which will simply cut into 
        # 4 equal size bins (e.g. 60 items [0,15,30,45,60] which means [0-15, 16-30, 31-45, 46-60])
        bins = 4
        
    return bins

###############################################################################    
# Columns e.g. A.6.2.1.3, A.6.2.1.4, A.6.2.2.1, etc. in SOE AggregateScores   
# i.e. indicators
###############################################################################

# e.g. {'A.6.2.1.4': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa',]}
indicators_items = {}
# e.g. {'A.6.2.1': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa',]}
benchmarks_items = {}
# e.g. {'A.6.2': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa',]}
standards_items = {}
# e.g. {'A.6': ['Item_001_AS0602010401E_ddd', 'Item_002_AS0602010402M_aaa',]}
test_items = {}

def compile_items(item):
    """ A function to compile the related items into their indicators (e.g. Test.Grade.Standard.Benchmark.Indicator), benchmarks,
    standards and test.

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
    indicator = item_parts[0] + '.' + item_parts[3] + '.' + item_parts[5] + '.' + item_parts[7] + '.' + item_parts[9]
    benchmark = item_parts[0] + '.' + item_parts[3] + '.' + item_parts[5] + '.' + item_parts[7]
    standard = item_parts[0] + '.' + item_parts[3] + '.' + item_parts[5]
    test = item_parts[0] + '.' + item_parts[3]
    
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
        
    # Check if test already added, if not add it
    if test in test_items:       
        test_items[test].append(item)
    else:
        test_items[test] = [item]    

cols = df_student_results_aggscores.columns.values
cols_items = [i for i in cols if 'Item_' in i]

for i in cols_items:
    compile_items(i)

for ind in sorted(indicators_items.keys()):
    items = indicators_items[ind]
    df_student_results_aggscores[ind] = df_student_results_aggscores.loc[:, items].sum(axis=1)    

###############################################################################    
# Columns e.g. A.6.2.1.3Total, A.6.2.1.4Total, A.6.2.2.1Total, not shown in SOE AggregateScores
# but useful in calculation later on
###############################################################################
for ind in sorted(indicators_items.keys()):
    items = indicators_items[ind]
    df_student_results_aggscores[ind+'Total'] = df_student_results_aggscores.loc[:, items].count(axis=1)
    
###############################################################################    
# Columns e.g. A.6.2.1, A.6.2.2, etc. not in SOE AggregateScores
# i.e. benchmarks (to bypass indicator like Phill Geeves)
###############################################################################    
for ben in sorted(benchmarks_items.keys()):
    items = benchmarks_items[ben]
    df_student_results_aggscores[ben] = df_student_results_aggscores.loc[:, items].sum(axis=1)    

###############################################################################    
# Columns e.g. A.6.2.1Total, A.6.2.2Total, not shown in SOE AggregateScores
# but useful in calculation later on (to bypass indicator like Phill Geeves)
###############################################################################
for ben in sorted(benchmarks_items.keys()):
    items = benchmarks_items[ben]
    df_student_results_aggscores[ben+'Total'] = df_student_results_aggscores.loc[:, items].count(axis=1)
    
###############################################################################    
# Columns e.g. A.6.2, etc. not in SOE AggregateScores   
# i.e. standards (to bypass indicator like Phill Geeves)
###############################################################################    
for sta in sorted(standards_items.keys()):
    items = standards_items[sta]
    df_student_results_aggscores[sta] = df_student_results_aggscores.loc[:, items].sum(axis=1)    

###############################################################################    
# Columns e.g. A.6.2Total, etc. not shown in SOE AggregateScores
# but useful in calculations later on (to bypass indicator like Phill Geeves)
###############################################################################
for sta in sorted(standards_items.keys()):
    items = standards_items[sta]
    df_student_results_aggscores[sta+'Total'] = df_student_results_aggscores.loc[:, items].count(axis=1)
    
###############################################################################    
# Columns e.g. A.6, etc. not in SOE AggregateScores   
# i.e. test (to bypass indicator like Phill Geeves)
###############################################################################    
for tes in sorted(test_items.keys()):
    items = test_items[tes]
    df_student_results_aggscores[tes] = df_student_results_aggscores.loc[:, items].sum(axis=1)    

###############################################################################    
# Columns e.g. A.6Total, etc. not shown in SOE AggregateScores
# but useful in calculations later on (to bypass indicator like Phill Geeves)
###############################################################################
for tes in sorted(test_items.keys()):
    items = test_items[tes]
    df_student_results_aggscores[tes+'Total'] = df_student_results_aggscores.loc[:, items].count(axis=1)
    
###############################################################################
# Columns e.g. A.6.2.1.3Level, A.6.2.1.4Level, A.6.2.2.1Level, etc. in SOE AggregateScores
#
# Business rule: 
# Essentially standard bins technique where total items correct from total items will
# define the level. Results do vary when items are not a multiple of 4 for a given
# indicator (a bit rare but to note)
###############################################################################
for ind in sorted(indicators_items.keys()):
    items = indicators_items[ind]
    total_possible_scores = df_student_results_aggscores[ind+'Total'].unique()
    bins = get_bins(total_possible_scores, 'indicators')
        
    df_student_results_aggscores[ind+'Level'] = pd.cut(df_student_results_aggscores[ind], bins, 
                                                       labels=achievement_levels, include_lowest=True)
    
###############################################################################    
# Columns e.g. A.6.2.1_L1Percent, A.6.2.1_L2Percent, A.6.2.1_L3Percent, A.6.2.1_L4Percent, A.6.2.2_L1Percent, A.6.2.2_L2Percent, etc. in SOE AggregateScores
# i.e. benchmarks weighted scores
###############################################################################
# e.g. {'A.6.2.1': ['A.6.2.1.3Level', 'A.6.2.1.4Level',]}
benchmarks_indicators_levels = {}
# e.g. {'A.6.2.1': ['A.6.2.1.3', 'A.6.2.1.4',]}
benchmarks_indicators = {}
# e.g. {'A.6.2.1': ['A.6.2.1_L1Percent', 'A.6.2.1_L2Percent', 'A.6.2.1_L3Percent', 'A.6.2.1_L4Percent']}
benchmarks_levels_percent = {}

def compile_benchmarks(level):
    """ A function to compile the related indicators into their benchmarks (e.g. Test.Grade.Standard.Benchmark).

    Parameters
    ----------
    level : String, required
        The level string representing an indicator (e.g. A.6.2.1.3Level)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    Nothing
    """    
    level_parts = level.split('.')
    benchmark = level_parts[0] + '.' + level_parts[1] + '.' + level_parts[2] + '.' + level_parts[3]
    #print('benchmark:', benchmark)
    # Check if group already added, if not add it
    indicator = level.split('Level')[0]
    if benchmark in benchmarks_indicators_levels:       
        benchmarks_indicators_levels[benchmark].append(level)
        benchmarks_indicators[benchmark].append(indicator)        
    else:
        benchmarks_indicators_levels[benchmark] = [level]
        benchmarks_indicators[benchmark] = [indicator]
        benchmarks_levels_percent[benchmark] = [benchmark+'_L1Percent',benchmark+'_L2Percent',benchmark+'_L3Percent',benchmark+'_L4Percent']

# Get indicators Level columns (i.e. A.6.2.1.3Level, A.6.2.1.4Level, A.6.2.2.1Level, etc.)
cols = df_student_results_aggscores.columns.values
cols_indicators_levels = [i for i in cols if 'Level' in i]        

for i in cols_indicators_levels:
    compile_benchmarks(i)

for b in sorted(benchmarks_indicators_levels.keys()):
    # Total indicators for the benchmark
    total_indicators = len(benchmarks_indicators_levels[b])
    print('A total of {} indicators ({}) for benchmarks {}.'.format(total_indicators, benchmarks_indicators_levels[b], b))  
    #level_nums = [i+'Num' for i in benchmarks_indicators_levels[b]]
    #print('level_nums', level_nums)
    
    df_level = df_student_results_aggscores.loc[:, benchmarks_indicators_levels[b]]    
    df_student_results_aggscores[b+'_L1Percent'] = df_level[ df_level == 'Beginning' ].count(axis='columns') / total_indicators
    df_student_results_aggscores[b+'_L2Percent'] = df_level[ df_level == 'Developing' ].count(axis='columns') / total_indicators
    df_student_results_aggscores[b+'_L3Percent'] = df_level[ df_level == 'Proficient' ].count(axis='columns') / total_indicators
    df_student_results_aggscores[b+'_L4Percent'] = df_level[ df_level == 'Advanced' ].count(axis='columns') / total_indicators

###############################################################################    
# Columns e.g. A.6.2.1Level, A.6.2.2Level, etc. not in SOE AggregateScores
# but used in analyzing benchmarks following the student count by levels analysis (not level count)
# This approach actually builds on what it seems like SOE was heading for with his
# *_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent columns (totalling 1). 
# But SOE does not seem to use this in his results anaylis.
# Also referred in Pacific EMIS as "weighted scores"
#
# This technique still requires to go through indicators "in the background"
#
# This will need to be set on new defined business rule. They are based (calculated on)
# the columns e.g. A.6.2.1_L1Percent, A.6.2.1_L2Percent, A.6.2.1_L3Percent, A.6.2.1_L4Percent, A.6.2.2_L1Percent, A.6.2.2_L2Percent, A.6.2.2_L3Percent, A.6.2.2_L4Percent (i.e. benchmarks)
# The level with the highest percentage can be used. If two or more levels have equal percentages
# then take the (best or worst level?). It can do both by commenting/uncommenting lines below
# i.e. benchmarks
###############################################################################

for b in benchmarks_levels_percent:
    df1 = df_student_results_aggscores[benchmarks_levels_percent[b]] #.copy()
    # START: If highest maximum level is sought
    cols = df1.columns.to_list()
    cols.sort(reverse=True)
    df1 = df1[cols]
    # END: If highest maximum level is sought
    df_student_results_aggscores[b+'Level'] = df1.idxmax(axis=1)
    df_student_results_aggscores[b+'Level'] = df_student_results_aggscores[b+'Level'].apply(lambda x: get_level(x))


    
###############################################################################    
# Columns e.g. A.6.2_L1Percent, A.6.2_L2Percent, A.6.2_L3Percent, A.6.2_L4Percent, etc. in SOE AggregateScores
# i.e. standards
###############################################################################

# e.g. {'A.6.2': ['A.6.2.1.3Level', 'A.6.2.1.4Level', 'A.6.2.2.1Level', etc.]}
standards_indicators_levels = {}
# e.g. {'A.6.2': ['A.6.2.1.3', 'A.6.2.1.4', 'A.6.2.2.1', etc.]}
standards_indicators = {}
# e.g. {'A.6.2': ['A.6.2_L1Percent','A.6.2_L2Percent','A.6.2_L3Percent','A.6.2_L4Percent']}
standards_levels_percent = {}

def compile_standards(level):
    """ A function to compile the related indicators into their standards (e.g. Test.Grade.Standard).

    Parameters
    ----------
    level : String, required
        The level string representing an indicator (e.g. A.6.2.1.3Level)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    Nothing
    """    
    level_parts = level.split('.')
    standard = level_parts[0] + '.' + level_parts[1] + '.' + level_parts[2]
    #print('standard:', standard)
    # Check if standard already added, if not add it
    indicator = level.split('Level')[0]
    if standard in standards_indicators_levels:       
        standards_indicators_levels[standard].append(level)
        standards_indicators[standard].append(indicator)
    else:
        standards_indicators_levels[standard] = [level]
        standards_indicators[standard] = [indicator]
        standards_levels_percent[standard] = [standard+'_L1Percent',standard+'_L2Percent',standard+'_L3Percent',standard+'_L4Percent']

# Get Level benchmarks columns (i.e. A.6.2.1Level, A.6.2.2Level, etc.)
# At this point we now have additional *Level columns for benchmarks
cols = df_student_results_aggscores.columns.values
cols_benchmarks_levels = [i for i in cols if 'Level' in i] 
cols_benchmarks_levels = list(set(cols_benchmarks_levels) - set(cols_indicators_levels))

for i in cols_indicators_levels:
    compile_standards(i)
    
for s in sorted(standards_indicators_levels.keys()):
    # Total indicators for the standard
    total_indicators = len(standards_indicators_levels[s])
    print('A total of {} indicators ({}) for standards {}.'.format(total_indicators, standards_indicators_levels[s], s))  
    
    df_level = df_student_results_aggscores.loc[:, standards_indicators_levels[s]]
    df_student_results_aggscores[s+'_L1Percent'] = df_level[ df_level == 'Beginning' ].count(axis='columns') / total_indicators
    df_student_results_aggscores[s+'_L2Percent'] = df_level[ df_level == 'Developing' ].count(axis='columns') / total_indicators
    df_student_results_aggscores[s+'_L3Percent'] = df_level[ df_level == 'Proficient' ].count(axis='columns') / total_indicators
    df_student_results_aggscores[s+'_L4Percent'] = df_level[ df_level == 'Advanced' ].count(axis='columns') / total_indicators    

###############################################################################    
# Columns e.g. A.6.2Level, etc. not in SOE AggregateScores
# but used in analyzing standards following the student count by levels analysis (not level count)
# This approach actually builds on what it seems like SOE was heading for with his
# *_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent columns (totalling 1). 
# But SOE does not seem to use this in his results analysis.
# Also referred in Pacific EMIS as "weighted scores"
#
# This technique still requires to go through indicators "in the background"
# 
# This will need to be set on defined business rule. They are based (calculated on)
# the columns e.g. A.6.2_L1Percent, A.6.2_L2Percent, A.6.2_L3Percent, A.6.2_L4Percent (i.e. standards)
# The level with the higher percentage can be used. If two or more levels have equal percentages
# then take the (best or worst level?)
# i.e. standards
###############################################################################

for s in standards_levels_percent:
    df1 = df_student_results_aggscores[standards_levels_percent[s]] #.copy()
    # START: If highest maximum level is sought
    cols = df1.columns.to_list()
    cols.sort(reverse=True)
    df1 = df1[cols]
    # END: If highest maximum level is sought
    df_student_results_aggscores[s+'Level'] = df1.idxmax(axis=1)
    df_student_results_aggscores[s+'Level'] = df_student_results_aggscores[s+'Level'].apply(lambda x: get_level(x))

###############################################################################  
# Column TotalScore_* in SOE AggregateScores   
###############################################################################  
df_student_results_aggscores['TotalScore'] = df_student_results_aggscores.loc[:, cols_items].sum(axis=1)
df_student_results_aggscores['TotalScore_LowerLimit'] = df_student_results_aggscores['TotalScore'] - 6
df_student_results_aggscores['TotalScore_UpperLimit'] = df_student_results_aggscores['TotalScore'] + 6

###############################################################################    
# Columns e.g. L1Percent, L2Percent, L3Percent, L4Percent, etc. in SOE AggregateScores
# Should be named A.6L1Percent, A.6L2Percent, A.6L3Percent, A.6L4Percent, etc. for consistency
###############################################################################

# e.g. {'A.6': ['A.6.2.1.3Level', 'A.6.2.1.4Level', 'A.6.2.2.1Level', etc.]}
test_indicators_levels = {}
# e.g. {'A.6': ['A.6.2.1.3', 'A.6.2.1.4', 'A.6.2.2.1', etc.]}
test_indicators = {}
# e.g. {'A.6': ['L1Percent','L2Percent','L3Percent','L4Percent']}
# or if not following Dr. SOE to be more consistent would have been {'A.6': ['A.6_L1Percent','A.6_L2Percent','A.6_L3Percent','A.6_L4Percent']}
test_levels_percent = {}


def compile_test(level):
    """ A function to compile the related indicators into the whole test (e.g. Test.Grade).

    Parameters
    ----------
    level : String, required
        The level string representing an indicator (e.g. A.6.2.1.3Level)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    Nothing
    """    
    level_parts = level.split('.')
    test = level_parts[0] + '.' + level_parts[1]
    #print('test:', test)
    # Check if test already added, if not add it
    indicator = level.split('Level')[0]
    if test in test_indicators_levels:       
        test_indicators_levels[test].append(level)
        test_indicators[test].append(indicator)
    else:        
        test_indicators_levels[test] = [level]
        test_indicators[test] = [indicator]
        test_levels_percent[test] = ['L1Percent','L2Percent','L3Percent','L4Percent']

# Get Level standards columns (i.e. A.6.2Level, etc.)
# At this point we now have additional *Level columns for standards and benchmarks
cols = df_student_results_aggscores.columns.values
cols_standards_levels = [i for i in cols if 'Level' in i] 
cols_standards_levels = list(set(cols_standards_levels) - set(cols_benchmarks_levels) - set(cols_indicators_levels))
        
for i in cols_indicators_levels:
    compile_test(i)
    
for t in sorted(test_indicators_levels.keys()):
    # Total indicators for the test
    total_indicators = len(test_indicators_levels[t])
    print('A total of {} indicators ({}) for test {}.'.format(total_indicators, test_indicators_levels[t], t))  
    
    df_level = df_student_results_aggscores.loc[:, test_indicators_levels[t]]
    df_student_results_aggscores['L1Percent'] = df_level[ df_level == 'Beginning' ].count(axis='columns') / total_indicators
    df_student_results_aggscores['L2Percent'] = df_level[ df_level == 'Developing' ].count(axis='columns') / total_indicators
    df_student_results_aggscores['L3Percent'] = df_level[ df_level == 'Proficient' ].count(axis='columns') / total_indicators
    df_student_results_aggscores['L4Percent'] = df_level[ df_level == 'Advanced' ].count(axis='columns') / total_indicators

###############################################################################    
# Columns e.g. A.6Level not in SOE AggregateScores
# but used in analyzing standards following the student count by levels analysis (not level count)
# This approach actually builds on what it seems like SOE was heading for with his
# *_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent columns (totalling 1). 
# But SOE does not seem to use this in his results analysis.
# Also referred in Pacific EMIS as "weighted scores"
#
# This technique still requires to go through indicators "in the background"
#
# This will need to be set on defined business rule. They are based (calculated on)
# the columns e.g. L1Percent, L2Percent, L3Percent, L4Percent (i.e. test)
# The level with the higher percentage can be used. If two or more levels have equal percentages
# then take the (best or worst level?)
# i.e. test
###############################################################################

for t in test_levels_percent:
    df1 = df_student_results_aggscores[test_levels_percent[t]] #.copy()
    # START: If highest maximum level is sought
    cols = df1.columns.to_list()
    cols.sort(reverse=True)
    df1 = df1[cols]
    # END: If highest maximum level is sought
    df_student_results_aggscores[t+'Level'] = df1.idxmax(axis=1)
    df_student_results_aggscores[t+'Level'] = df_student_results_aggscores[t+'Level'].apply(lambda x: get_level(x))
    
###############################################################################        
# Column AYP (Level 3 and 4) in SOE AggregateScores   
###############################################################################    
df_student_results_aggscores['AYP'] = df_student_results_aggscores['L3Percent'] + df_student_results_aggscores['L4Percent']

# Final column cleanup
df_student_results_aggscores = df_student_results_aggscores.drop(cols_items, axis=1)

# Get Level test columns (i.e. A.6Level)
# At this point we now have additional *Level columns for test, standards and benchmarks
cols = df_student_results_aggscores.columns.values
cols_test_levels = [i for i in cols if 'Level' in i] 
cols_test_levels = list(set(cols_test_levels) - set(cols_standards_levels) - set(cols_benchmarks_levels) - set(cols_indicators_levels))

###############################################################################
# The following offers an alternative way of producing analysis on benchmarks,
# standards and test based directy on their respective items (not so called level count
# as in SOE).
# This is more akin to how "indicator" analysis in SOE works. 
# This is *not* in SOE AggregateScores.
# This is more based on Phill Geeves final report (refer to Appendix 1 in cell above)
# and also how other common assessment system works (e.g. OnlineSBA by Pacific Testing)
#
# Business rule:
# Use the ItemCount method exactly as we do to calculate the Candidate/Indicator Level. 
# Specifically, take the sum across all Items that contribute to all Indicators in the Benchmark (or Standard, Whole Test)
# (in other words, all the benchmarks' respective items), and convert the ratio of Correct Items / Total Items 
# back to an achievement Level 1-4 (bins)
#
# Compare results with above for curiosity
###############################################################################
for ben in sorted(benchmarks_items.keys()):
    items = benchmarks_items[ben]
    total_possible_scores = df_student_results_aggscores[ben+'Total'].unique()
    bins = get_bins(total_possible_scores, 'benchmarks')
    df_student_results_aggscores[ben+'LevelAlt'] = pd.cut(df_student_results_aggscores[ben], bins, 
                                                       labels=achievement_levels, include_lowest=True)
for sta in sorted(standards_items.keys()):
    items = standards_items[sta]
    total_possible_scores = df_student_results_aggscores[sta+'Total'].unique()
    bins = get_bins(total_possible_scores, 'standards')
    df_student_results_aggscores[sta+'LevelAlt'] = pd.cut(df_student_results_aggscores[sta], bins, 
                                                       labels=achievement_levels, include_lowest=True)
for tes in sorted(test_items.keys()):    
    items = test_items[tes]
    total_possible_scores = df_student_results_aggscores[tes+'Total'].unique()
    bins = get_bins(total_possible_scores, 'test')    
    display(df_student_results_aggscores[tes])
    df_student_results_aggscores[tes+'LevelAlt'] = pd.cut(df_student_results_aggscores[tes], bins, 
                                                       labels=achievement_levels, include_lowest=True)    

# Get Level benchmarks columns (i.e. A.6.2.1LevelAlt, A.6.2.2LevelAlt, etc.)
# At this point we now have additional *LevelAlt columns for benchmarks, standards and test
cols = df_student_results_aggscores.columns.values
cols_levels_alt = [i for i in cols if 'LevelAlt' in i]

cols_benchmarks_levels_alt = []
cols_standards_levels_alt = []
cols_test_levels_alt = []

for la in cols_levels_alt:
    parts = len(la.split("."))
    #print("Part", parts)
    if parts == 4:
        cols_benchmarks_levels_alt.append(la)
    elif parts == 3:
        cols_standards_levels_alt.append(la)
    elif parts == 2:
        cols_test_levels_alt.append(la)
    else:
        print("Error this test does not seem like others. Check the naming convention of Test.Standard.Benchmark.Indicator", la)
        

print('indicators_items')
pp.pprint(indicators_items)
print('benchmarks_items')
pp.pprint(benchmarks_items)
print('standards_items')
pp.pprint(standards_items)
print('test_items')
pp.pprint(test_items)

print('cols_indicators_levels')
pp.pprint(cols_indicators_levels)
print('cols_benchmarks_levels')
pp.pprint(cols_benchmarks_levels)
print('cols_standards_levels')
pp.pprint(cols_standards_levels)
print('cols_test_levels')
pp.pprint(cols_test_levels)

print('benchmarks_indicators_levels')
pp.pprint(benchmarks_indicators_levels)
print('benchmarks_indicators')
pp.pprint(benchmarks_indicators)
print('benchmarks_levels_percent')
pp.pprint(benchmarks_levels_percent)
print('standards_indicators_levels')
pp.pprint(standards_indicators_levels)
print('standards_indicators')
pp.pprint(standards_indicators)
print('standards_levels_percent')
pp.pprint(standards_levels_percent)
print('test_indicators_levels')
pp.pprint(test_indicators_levels)
print('test_indicators')
pp.pprint(test_indicators)
print('test_levels_percent')
pp.pprint(test_levels_percent)

print('cols_benchmarks_levels_alt')
pp.pprint(cols_benchmarks_levels_alt)
print('cols_standards_levels_alt')
pp.pprint(cols_standards_levels_alt)
print('cols_test_levels_alt')
pp.pprint(cols_test_levels_alt)

#print(df_student_results_aggscores.columns)
#display(df_student_results_aggscores)

# %%
list(benchmarks_levels_percent.values())
benchmarks_levels_percent_flattened = [val for sublist in list(benchmarks_levels_percent.values()) for val in sublist]
benchmarks_levels_percent_flattened

# %%
###############################################################################
# Results Sheet                                                               #
###############################################################################
df_student_results_analysis = df_student_results_aggscores.copy()
#display(df_student_results_analysis)

# Flatten all the levels_percent lists for use later in the weighted technique
benchmarks_levels_percent_flattened = [val for sublist in list(benchmarks_levels_percent.values()) for val in sublist]
standards_levels_percent_flattened = [val for sublist in list(standards_levels_percent.values()) for val in sublist]
test_levels_percent_flattened = [val for sublist in list(test_levels_percent.values()) for val in sublist]


print('School Name = {} (N = {})'.format('AllSchools', df_student_results_analysis.count()[0]))
print('Test Name = {} (Test Date = {})'.format(df_student_results_analysis['TestName'][0], df_student_results_analysis['SchoolYear'][0]))

df_indicators = df_student_results_analysis[['StudentName','Gender'] + cols_indicators_levels] #['StudentName'] + 
print('Indicators Levels')
display(df_indicators)

df_benchmarks = df_student_results_analysis[['StudentName','Gender'] + cols_benchmarks_levels] #['StudentName'] + 
print('Benchmarks Levels')
display(df_benchmarks)

df_benchmarks_alt = df_student_results_analysis[['StudentName','Gender'] + cols_benchmarks_levels_alt] #['StudentName'] + 
print('Benchmarks Levels Alt')
display(df_benchmarks_alt)

df_benchmarks_weighted = df_student_results_analysis[['StudentName','Gender'] + cols_benchmarks_levels_alt + benchmarks_levels_percent_flattened] #['StudentName'] + 
print('Benchmarks Levels Weighted')
display(df_benchmarks_weighted)

df_standards = df_student_results_analysis[['StudentName','Gender'] + cols_standards_levels] #['StudentName'] + 
print('Standards Levels')
display(df_standards)

df_standards_alt = df_student_results_analysis[['StudentName','Gender'] + cols_standards_levels_alt] #['StudentName'] + 
print('Standards Levels Alt')
display(df_standards_alt)

df_standards_weighted = df_student_results_analysis[['StudentName','Gender'] + cols_standards_levels_alt + standards_levels_percent_flattened] #['StudentName'] + 
print('Standards Levels Weighted')
display(df_standards_weighted)

df_test = df_student_results_analysis[['StudentName','Gender'] + cols_test_levels] #['StudentName'] + 
print('Test Levels')
display(df_test)

df_test_alt = df_student_results_analysis[['StudentName','Gender'] + cols_test_levels_alt] #['StudentName'] + 
print('Test Levels Alt')
display(df_test_alt)

df_test_weighted = df_student_results_analysis[['StudentName','Gender'] + cols_test_levels_alt + test_levels_percent_flattened] #['StudentName'] + 
print('Test Levels Weighted')
display(df_test_weighted)


# %%
# Utility function for cells that follow

def prepare_for_chart(df):
    """Does some basic redundent preparation to a dataframe before plotting with matplotlib.
    Essentially it does the following:
     * Computes the percentage (e.g. 0.1, 0.9)
     * Adds a Total row with 100 percent (i.e. 1)
     * Rounds all values to 2 decimals
     * Re-order the levels ready for plotting
     * Assign negative values for levels to be on the bottom (or left) of the axis

    Parameters
    ----------
    filename : df, required
        The DataFrame to prep

    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    DataFrame
    """
    # When level values don't add up to 1 it's because of rounding
    df = df.apply(lambda x: x / float(x.sum()))
    df.loc['Total'] = df.sum()
    df = df.round(2)
    levels_index = ['Proficient','Advanced','Developing','Beginning','Total']
    df = df.reindex(levels_index)
    df.loc[['Developing','Beginning']] = df.loc[['Developing','Beginning']].apply(lambda x: -x)
    return df

def add_total_in_column_names(df, index='Index'):
    """Adds a string or the form (n=X) in the columns showing the total.

    Parameters
    ----------
    df : DataFrame, required
        The DataFrame to prep
    cos_levels : List, OBSOLETE
        A list of levels columns
    index : String, required
        Whether we dealing with Index or MultiIndex

    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    DataFrame
    """
    
    if index == 'Index':
        #print('Dealing with a pd.core.indexes.base.Index')
        #for l in cols_levels:
        #    tot = df[l.split('Level')[0]].sum()
        #    df = df.rename(columns = {l.split('Level')[0]: l.split('Level')[0]+' (n='+str(tot)+')'})
        for c in df.columns:
            tot = df[c].sum()
            df = df.rename(columns = {c: c+' (n='+str(tot)+')'})
        return df
    elif index == 'MultiIndex':
        #print('Dealing with a pd.core.indexes.multi.MultiIndex')
        # First flatten MultiIndex (Indicator/Gender)
        df.columns = ['_'.join(col) for col in df.columns.values]

        #print("Troubleshooting MultiIndex")
        #display(df)
        #print(df.columns)
        #for l in cols_levels:
        #    for g in ['f','m']:
        #        col = l.split('Level')[0]+'_'+g
        #        tot = df[col].sum()
        #        df = df.rename(columns = {col: col+' (n='+str(tot)+')'})
        for c in df.columns:
            tot = df[c].sum()
            df = df.rename(columns = {c: c+' (n='+str(tot)+')'})        

        # Unflatten back to MultiIndex
        cols = [col.split('_') for col in df.columns.values]
        arrays = [[ i for i, j in cols ], [ j for i, j in cols ]]
        df.columns = pd.MultiIndex.from_arrays(arrays, names=(None, 'Gender'))
        return df


# %%
# Standard, benchmarks and indicators descriptions

descriptions = {
    'indicators' : {
        'A.6.2.1.3': 'A.6.2.1.3 - And some description of an indicator, it could be pretty long text actually, be ready.',
        'A.6.2.1.4': 'A.6.2.1.4 - And some description of an indicator, it could be pretty long text actually, be ready.',
        'A.6.2.2.1': 'A.6.2.2.1 - And some description of an indicator, it could be pretty long text actually, be ready.',
        'A.6.2.2.2': 'A.6.2.2.2 - And some description of an indicator, it could be pretty long text actually, be ready.',
        'A.6.2.2.4': 'A.6.2.2.4 - And some description of an indicator, it could be pretty long text actually, be ready.',
        'A.6.2.2.6': 'A.6.2.2.6 - And some description of an indicator, it could be pretty long text actually, be ready.',
        'A.6.2.3.2': 'A.6.2.3.2 - And some description of an indicator, it could be pretty long text actually, be ready.'},
    'benchmarks': {
        'A.6.2.1': 'A.6.2.1 - And some description of an benchmark, it could be pretty long text actually, be ready.',
        'A.6.2.2': 'A.6.2.2 - And some description of an benchmark, it could be pretty long text actually, be ready.',
        'A.6.2.3': 'A.6.2.3 - And some description of an benchmark, it could be pretty long text actually, be ready.',
    },
    'benchmarksalt': {
        'A.6.2.1': 'A.6.2.1 - And some description of an benchmark, it could be pretty long text actually, be ready.',
        'A.6.2.2': 'A.6.2.2 - And some description of an benchmark, it could be pretty long text actually, be ready.',
        'A.6.2.3': 'A.6.2.3 - And some description of an benchmark, it could be pretty long text actually, be ready.',
    },
    'benchmarksweighted': {
        'A.6.2.1': 'A.6.2.1 - And some description of an benchmark, it could be pretty long text actually, be ready.',
        'A.6.2.2': 'A.6.2.2 - And some description of an benchmark, it could be pretty long text actually, be ready.',
        'A.6.2.3': 'A.6.2.3 - And some description of an benchmark, it could be pretty long text actually, be ready.',
    },
    'standards' : {
        'A.6.2': 'A.6.2 - Some description about a reading standard.'
    },
    'standardsalt' : {
        'A.6.2': 'A.6.2 - Some description about a reading standard.'
    },
    'standardsweighted' : {
        'A.6.2': 'A.6.2 - Some description about a reading standard.'
    },
    'test' : {
        'A.6': 'Reading Grade 6 - English'
    },
    'testalt' : {
        'A.6': 'Reading Grade 6 - English'
    },
    'testweighted' : {
        'A.6': 'Reading Grade 6 - English'
    }
}

try: 
    if test == 'MISAT':
        # %run data/RMI/MISAT-descriptions.py
    elif test == 'NMCT':
        # %run data/FSM/NMCT-descriptions.py
    
    descriptions = {
        'indicators' : {},
        'benchmarks': {},
        'benchmarksalt': {},
        'benchmarksweighted': {},
        'standards' : {},
        'standardsalt' : {},
        'standardsweighted' : {},
        'test' : {},
        'testalt' : {},
        'testweighted' : {}
    }
    
    for k,v in misat_descriptions.items():
        l = k.split(".")
        if len(l) == 5:
            descriptions['indicators'][k] = k + ": " + v 
        if len(l) == 4:
            descriptions['benchmarks'][k] = k + ": " + v 
            descriptions['benchmarksalt'][k] = k + ": " + v 
            descriptions['benchmarksweighted'][k] = k + ": " + v 
        if len(l) == 3:
            descriptions['standards'][k] = k + ": " + v 
            descriptions['standardsalt'][k] = k + ": " + v
            descriptions['standardsweighted'][k] = k + ": " + v
        if len(l) == 2:        
            descriptions['test'][k] = k + ": " + v
            descriptions['testalt'][k] = k + ": " + v
            descriptions['testweighted'][k] = k + ": " + v
except:
    print('File does not exist')

descriptions


# %%
###############################################################################
# Results Sheet                                                               
# Analysis by indicators just like SOE assessment                             
# BUT also provides:
#  * gender disaggregation not provided in SOE at this level 
#  * with totals
#  * extended versions (with descriptions)
#  * benchmarks, standards and test analysed just like indicators 
#    (student count)
###############################################################################

def num_student_for_each_rubric_level(cols_levels, df_metric, metric, weighted=False):
    """A function to produce various variations of DataFrame used later in Analysis.

    Parameters
    ----------
    cols_levels : List or Dict, required
        A list of levels columns for the metric to be processed (e.g. ['A.6.2.1.3Level', etc.] for indicators, OR
        A dict of levels percent for the metric to be processed weighted (e.g. 
        {'A.3.2.1': ['A.3.2.1_L1Percent','A.3.2.1_L2Percent','A.3.2.1_L3Percent','A.3.2.1_L4Percent'], 'A.3.2.2': ['A.3.2.2_L1Percent', etc.})
    df_metric : DataFrame, required
        The starting DataFrame to process
    metric : String, required
        A label identifying the metric to be processed (i.e. indicators, benchmarks, standards and test)
    weighted: Boolean, required
        Whether we producing weighted versions or not
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    dfs : Dict
        Key value dictionary of dataframes available for later processing
    
    """
    print('-------------------------------------------------------------')
    print('Number of All Students for Each Rubric Level of '+metric)
    print('-------------------------------------------------------------')
    
    if weighted:
        #######################################
        # Summary (New weighted version...)
        #######################################
        metrics = []

        for k,v in cols_levels.items():
            #print(k)
            #print(v)
            # where k is the metric (Benchmark, Standard, Whole Test), and
            # where v is the Levels percent columsn (*_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent)

            df = df_metric[v].copy()
            df.loc[k] = df.sum()
            df = df.rename(columns = {v[0]: achievement_levels[0], 
                                      v[1]: achievement_levels[1], 
                                      v[2]: achievement_levels[2], 
                                      v[3]: achievement_levels[3]})
            df = df.loc[k].to_frame()
            metrics.append(df)

        df_summary = pd.concat(metrics, axis=1)
        print('df_'+metric+'_summary')
        display(df_summary)
    
        #######################################
        # Summary by gender (New weighted version...)
        #######################################
        metrics_gender = []

        for k,v in cols_levels.items():
            #print(k)
            #print(v)
            # where k is the metric (Benchmark, Standard, Whole Test), and
            # where v is the Levels percent columns (*_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent)

            df = df_metric[v+['Gender']].copy()
            df = df.pivot(columns='Gender')    
            df.loc[k] = df.sum()
            df = df.rename(columns = {v[0]: achievement_levels[0], 
                                      v[1]: achievement_levels[1], 
                                      v[2]: achievement_levels[2], 
                                      v[3]: achievement_levels[3]})
            df = df.loc[k].to_frame()
            df.fillna(0, inplace=True)
            metrics_gender.append(df)

        df_summary_gender = pd.concat(metrics_gender, axis=1)
        df_summary_gender = df_summary_gender.unstack()
        print('df_'+metric+'_summary_gender')
        display(df_summary_gender)
    else:
        #######################################
        # Summary
        #######################################
        metrics = []

        display(cols_levels)

        for m in cols_levels:
            df = df_metric[['StudentName',m]].groupby([m], observed=True).count()    
            df.rename(columns = {'StudentName':m.split('Level')[0]}, inplace = True)
            df.index.name = None
            metrics.append(df)

        df_summary = pd.concat(metrics, axis=1)
        print('df_'+metric+'_summary')
        display(df_summary)

        #######################################
        # Summary by gender
        #######################################
        metric_gender = []

        for m in cols_levels:
            df = df_metric[['StudentName','Gender',m]].groupby([m, 'Gender'], observed=True).count()    
            df = df.unstack()
            df.rename(columns = {'StudentName':m.split('Level')[0]}, inplace = True)
            df.index.name = None

            metric_gender.append(df)

        df_summary_gender = pd.concat(metric_gender, axis=1)
        print('df_'+metric+'_summary_gender')
        display(df_summary_gender)
    
    #######################################
    # Summary (extended version)
    #######################################
    df_summary_x = df_summary.rename(columns = descriptions[metric])
    print('df_'+metric+'_summary_x')
    display(df_summary_x)
    
    #######################################
    # Summary by gender (extended version)
    #######################################
    df_summary_gender_x = df_summary_gender.rename(columns = descriptions[metric])
    print('df_'+metric+'_summary_gender_x')
    display(df_summary_gender_x)

    #######################################
    # Summary including Total row
    #######################################
    df_summary_tot = df_summary.copy()
    df_summary_tot.loc['Total'] = df_summary_tot.sum()
    print('df_'+metric+'_summary_tot')
    display(df_summary_tot)

    #######################################
    # Summary including Total row by gender
    #######################################
    df_summary_gender_tot = df_summary_gender.copy()
    df_summary_gender_tot.loc['Total'] = df_summary_gender_tot.sum()
    print('df_'+metric+'_summary_gender_tot')
    display(df_summary_gender_tot)
    
    #######################################
    # Summary percent
    #######################################
    df_summary_per = df_summary.copy()
    df_summary_per = add_total_in_column_names(df_summary_per, index='Index')
    df_summary_per = prepare_for_chart(df_summary_per)
    print('df_'+metric+'_summary_per')
    display(df_summary_per)

    #######################################
    # Summary percent by gender percent
    #######################################
    df_summary_gender_per = df_summary_gender.copy()
    df_summary_gender_per = add_total_in_column_names(df_summary_gender_per, index='MultiIndex')
    df_summary_gender_per = prepare_for_chart(df_summary_gender_per)
    print('df_'+metric+'_summary_gender_per')
    display(df_summary_gender_per)

    #######################################
    # Summary percent (extended version)
    #######################################  
    df_summary_per_x = df_summary.copy()
    df_summary_per_x = df_summary_per_x.rename(columns = descriptions[metric])
    df_summary_per_x = add_total_in_column_names(df_summary_per_x, index='Index')
    df_summary_per_x = prepare_for_chart(df_summary_per_x)
    print('df_'+metric+'_summary_per_x')
    display(df_summary_per_x)

    #######################################
    # Summary percent by gender (extended version)
    #######################################
    df_summary_gender_per_x = df_summary_gender.copy()
    df_summary_gender_per_x = add_total_in_column_names(df_summary_gender_per_x, index='MultiIndex')
    df_summary_gender_per_x = df_summary_gender_per_x.rename(columns = descriptions[metric])
    df_summary_gender_per_x = prepare_for_chart(df_summary_gender_per_x)
    print('df_'+metric+'_summary_gender_per_x')
    display(df_summary_gender_per_x)   
    
    # Troubleshooting
    #print('===============================================')
    #print('df_'+metric+'_summary_per')
    #display(df_summary_per) 
    
    dfs = {         
        'df_'+metric+'_summary': df_summary,
        'df_'+metric+'_summary_gender': df_summary_gender,
        'df_'+metric+'_summary_x' : df_summary_x,
        'df_'+metric+'_summary_gender_x' : df_summary_gender_x,
        'df_'+metric+'_summary_tot' : df_summary_tot,
        'df_'+metric+'_summary_gender_tot' : df_summary_gender_tot,
        'df_'+metric+'_summary_per' : df_summary_per,
        'df_'+metric+'_summary_gender_per' : df_summary_gender_per,
        'df_'+metric+'_summary_per_x' : df_summary_per_x,
        'df_'+metric+'_summary_gender_per_x' : df_summary_gender_per_x
    }
    return dfs

##############################################################################
# Analysis of Indicators just like in SOE Assessment
##############################################################################
students_each_rubric_level = num_student_for_each_rubric_level(cols_indicators_levels, df_indicators, 'indicators')

##############################################################################
# Not in SOE Assessment but included for comparison
# This is benchmarks, standards and test analysis but analysed 
# like SOE analyses indicators
##############################################################################
students_each_rubric_level.update(num_student_for_each_rubric_level(cols_benchmarks_levels, df_benchmarks, 'benchmarks'))
students_each_rubric_level.update(num_student_for_each_rubric_level(cols_benchmarks_levels_alt, df_benchmarks_alt, 'benchmarksalt'))
students_each_rubric_level.update(num_student_for_each_rubric_level(benchmarks_levels_percent, df_benchmarks_weighted, 'benchmarksweighted', weighted=True))
students_each_rubric_level.update(num_student_for_each_rubric_level(cols_standards_levels, df_standards, 'standards'))
students_each_rubric_level.update(num_student_for_each_rubric_level(cols_standards_levels_alt, df_standards_alt, 'standardsalt'))
students_each_rubric_level.update(num_student_for_each_rubric_level(standards_levels_percent, df_standards_weighted, 'standardsweighted', weighted=True))
students_each_rubric_level.update(num_student_for_each_rubric_level(cols_test_levels, df_test, 'test'))
students_each_rubric_level.update(num_student_for_each_rubric_level(cols_test_levels_alt, df_test_alt, 'testalt'))
students_each_rubric_level.update(num_student_for_each_rubric_level(test_levels_percent, df_test_weighted, 'testweighted', weighted=True))

# %%
# Let's try another alternative to produce level count analysis: Weighted technique

df = df_student_results_aggscores.copy()

print("Benchmarks levels percent")
display(benchmarks_levels_percent)
print("Benchmarks levels columns")
display(cols_benchmarks_levels)

# Sample as previously done...
metrics = []

for m in cols_benchmarks_levels:
    df2 = df[['StudentName',m]].groupby([m]).count()    
    df2.rename(columns = {'StudentName':m.split('Level')[0]}, inplace = True)
    df2.index.name = None
    metrics.append(df2)

df3 = pd.concat(metrics, axis=1)
print('df_benchmarks_summary')
display(df3)

# New weighted version
metrics = []

for k,v in benchmarks_levels_percent.items():
    #print(k)
    #print(v)
    # where k is the metric (Benchmark, Standard, Whole Test), and
    # where v is the Levels percent columsn (*_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent)
    
    cols = benchmarks_levels_percent[k]
    df7 = df[cols].copy()
    df7.loc[k] = df7.sum()
    df7 = df7.rename(columns = {cols[0]: achievement_levels[0], cols[1]: achievement_levels[1], cols[2]: achievement_levels[2], cols[3]: achievement_levels[3]})
    df7 = df7.loc[k].to_frame()
    metrics.append(df7)

df8 = pd.concat(metrics, axis=1)
print('df_benchmarks_summary')
display(df8)

# Sample as previously done by gender...
metric_gender = []

for m in cols_benchmarks_levels:
    df4 = df[['StudentName','Gender',m]].groupby([m, 'Gender']).count()    
    df4 = df4.unstack()
    df4.rename(columns = {'StudentName':m.split('Level')[0]}, inplace = True)
    df4.index.name = None
    df4.fillna(0, inplace=True)

    metric_gender.append(df4)

df5 = pd.concat(metric_gender, axis=1)
print('df_benchmark_summary_gender')
display(df5)

# New weighted version...
metrics_gender = []

for k,v in benchmarks_levels_percent.items():
    #print(k)
    #print(v)
    # where k is the metric (Benchmark, Standard, Whole Test), and
    # where v is the Levels percent columsn (*_L1Percent, *_L2Percent, *_L3Percent, *_L4Percent)

    df9 = df[v+['Gender']].copy()
    df9 = df9.pivot(columns='Gender')    
    df9.loc[k] = df9.sum()
    df9 = df9.rename(columns = {v[0]: achievement_levels[0], 
                                v[1]: achievement_levels[1], 
                                v[2]: achievement_levels[2], 
                                v[3]: achievement_levels[3]})
    df9 = df9.loc[k].to_frame()
    df9.fillna(0, inplace=True)
    metrics_gender.append(df9)

df10 = pd.concat(metrics_gender, axis=1)
df10 = df10.unstack()
print('df_benchmarks_summary')
display(df10)


# %%
###############################################################################
# Results Sheet (continue)                                                    
# Analysis of benchmarks, standards and test just like SOE assessment 
# (level counts, not students)
###############################################################################

def level_count_for_each_rubric_level(metric_levels, metric_indicators, df_indicators_summary, metric):
    """A function to produce various variations of DataFrame used later in Analysis. This is how
    Dr. SOE does his analysis on Benchmarks, Standards and Test (not Indicators)

    Parameters
    ----------
    metric_levels : Dict, required
        List of levels columns for the metric to be processed (e.g. {'benchmarkX|standardY|test' : ['A.6.2.1.3Level', etc.]}
    metric_indicators : Dict, required
        List of indicators for the metric to be processed (e.g. {'benchmarkX|standardY|test' : ['A.6.2.1.3', etc.]}    
    df_indicators_summary : DataFrame, required
        The starting DataFrame to process benchmarks, standards and test DataFrame as SOE does it.
    metric : String, required
        A label identifying the metric to be processed (i.e. indicators, benchmarks, standards and test)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    dfs : Dict
        Key value dictionary of dataframes available for later processing
    
    """
    print('-----------------------------------------------------------------------------------')
    print('Level Counts (NOT Students) for All Students for Each Rubric Level of '+metric)
    print('-----------------------------------------------------------------------------------')
    
    #######################################
    # Summary
    #######################################
    df_summary = df_indicators_summary.copy()
    
    # Here lies the important difference in how SOE does the analysis for benchmarks, standards and test
    # The benchmark's (or standard's or test's) indicators (columns) scores are summed
    for m in metric_levels:
        indicators = metric_indicators[m]

        df_summary[m] = df_summary[indicators].sum(axis=1)
        df_summary = df_summary.drop(indicators, axis=1)

    if metric=='standards':
        df_summary['Whole Test'] = df_summary[list(metric_levels.keys())].sum(axis=1)
    
    print('df_'+metric+'_summary')
    display(df_summary)

    #######################################
    # Summary (extended version)
    #######################################

    df_summary_x = df_summary.rename(columns = descriptions[metric])
    print('df_'+metric+'_summary_x')
    display(df_summary_x)

    #######################################
    # Summary including Total row
    #######################################

    df_summary_tot = df_summary.copy()
    df_summary_tot.loc['Total'] = df_summary_tot.sum()
    print('df_'+metric+'_summary_tot')
    display(df_summary_tot)

    #######################################
    # Summary percent
    #######################################

    print('-----------------------------------------------------------------------------------')
    print('Level Percents for All Students for Each Rubric Level of '+metric)
    print('-----------------------------------------------------------------------------------')
    df_summary_per = df_summary.copy()
    df_summary_per = add_total_in_column_names(df_summary_per, index='Index')
    df_summary_per = prepare_for_chart(df_summary_per)
    print('df_'+metric+'_summary_per')
    display(df_summary_per)

    #######################################
    # Summary percent (extended version)
    #######################################
    df_summary_per_x = df_summary_x.copy()
    df_summary_per_x = add_total_in_column_names(df_summary_per_x, index='Index')
    df_summary_per_x = prepare_for_chart(df_summary_per_x)
    print('df_'+metric+'_summary_per_x')
    display(df_summary_per_x)
    
    dfs = {
        'df_'+metric+'_summary': df_summary, 
        'df_'+metric+'_summary_x' : df_summary_x,
        'df_'+metric+'_summary_tot' : df_summary_tot,
        'df_'+metric+'_summary_per' : df_summary_per,
        'df_'+metric+'_summary_per_x' : df_summary_per_x,
    }
    return dfs

df_indicators_summary = students_each_rubric_level['df_indicators_summary'].copy()

level_count_each_rubric_level_soe = level_count_for_each_rubric_level(benchmarks_indicators_levels, benchmarks_indicators, df_indicators_summary, 'benchmarks')
level_count_each_rubric_level_soe.update(level_count_for_each_rubric_level(standards_indicators_levels, standards_indicators, df_indicators_summary, 'standards'))
level_count_each_rubric_level_soe.update(level_count_for_each_rubric_level(test_indicators_levels, test_indicators, df_indicators_summary, 'test'))

# %%
###############################################################################
# Results Sheet (continue)                                                    #
###############################################################################

exam = df_student_results_analysis['TestName'][0]

def prepare_for_plotting(df, metric):
    """A function that some a couple of transformation preparing for plotting
    
    Preperations for plotting. This uses the dataframe produced in several of the
    above cells. They are all packaged in the following Dicts
 
        * students_each_rubric_level
        * level_count_each_rubric_level_soe (gender versions not currently offered)
    
    And can be accessed with following keys:
        * 'df_'+metric+'_summary'
        * 'df_'+metric+'_summary_gender'
        * 'df_'+metric+'_summary_x'
        * 'df_'+metric+'_summary_gender_x'
        * 'df_'+metric+'_summary_tot'
        * 'df_'+metric+'_summary_gender_tot'
        * 'df_'+metric+'_summary_per'
        * 'df_'+metric+'_summary_gender_per'
        * 'df_'+metric+'_summary_per_x'
        * 'df_'+metric+'_summary_gender_per_x'
    
    For example, 
        * students_each_rubric_level['df_indicators_summary_per']
        * level_count_each_rubric_level_soe['df_benchmarks_summary_per']

    Parameters
    ----------
    df : DataFrame, required
        The DataFrame to prepare for plotting
    metric : String, required
        A label identifying the metric to be processed (i.e. indicators, benchmarks, standards and test)
        
    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    df : DataFrame
        The DataFrame ready for plotting
    
    """    
    df_summary_plot = df.drop('Total', axis='index')
    df_summary_plot = df_summary_plot.T
    df_summary_plot = df_summary_plot.sort_index()
    print('df_'+metric+'_summary_plot')
    display(df_summary_plot)
    return df_summary_plot

students_each_rubric_level_plottable = [i for i in students_each_rubric_level.keys() if 'summary_per' in i] 
level_count_each_rubric_level_soe_plottable = [i for i in level_count_each_rubric_level_soe.keys() if 'summary_per' in i] 

students_each_rubric_level_plottable_dfs = {}
for df_name in students_each_rubric_level_plottable:
    df = prepare_for_plotting(students_each_rubric_level[df_name], df_name.split('_')[1])
    students_each_rubric_level_plottable_dfs[df_name] = df

level_count_each_rubric_level_soe_plottable_dfs = {}
for df_name in level_count_each_rubric_level_soe_plottable:
    df = prepare_for_plotting(level_count_each_rubric_level_soe[df_name], df_name.split('_')[1])
    level_count_each_rubric_level_soe_plottable_dfs[df_name] = df


# %%
###############################################################################
# Results Sheet (continue)                                                    #
# Plotting functions                                                          #
###############################################################################

# Trying on same grid but having difficulties with long labels
#fig = plt.figure(figsize=(30, 4)) #, constrained_layout=True) 
#gs = gridspec.GridSpec(2, 1) #, width_ratios=[4, 9]) 
#gs.update(wspace=0.02, hspace=0)

##############################
# SOE Assessment Style Chart #
##############################
def plot_soe(df, label='xlabel', dimension='Students', title='N/A'):
    """A function to plot a DataFrame in SOE style.

    Parameters
    ----------
    df : DataFrame, required
        The DataFrame to plot the graph with.
    label : String, optional
        A string that will be show in the Y axis label
    dimension : String, options
        A string to modify that X axis label. In general for this plots we have two types of analysis:
            - SOE style of "level counts" or counting of indicators in a particular benchmark/standard/test at each performance level
            - EMIS styles (more common) of counting of students  in a particular benchmark/standard/test at each performance level
    """
    fig1 = plt.figure(figsize=(8, 4)) #, constrained_layout=True) 
    ax1 = plt.subplot() #gs[0]
    df.plot(ax=ax1, kind='bar', stacked=True)

    ax1.set_title('Republic of the Marshall Islands\n{}\nAll Students of AllSchools\nSOE Chart Style ({})'.format(exam, title), color='black')
    ax1.set_xlabel(label)
    ax1.set_ylabel('Percent of '+dimension+' in Each Performance Level')

    bars1 = ax1.patches

    # Add text to bars
    for bar in bars1:
        # Find where everything is located
        height = bar.get_height()
        width = bar.get_width()
        x = bar.get_x()
        y = bar.get_y()

        # The height of the bar is the data value and can be used as the label
        label_text =f'{abs(height*100):.0f}%'  # f'{width:.2f}' to format decimal values

        label_x = x + 0.45 + width / 2
        label_y = y + height / 2

        # only plot labels greater than given width
        if abs(height) > 0:
            ax1.text(label_x, label_y, label_text, ha='center', va='center', fontsize=8)

    hatches1 = []
    for h in ['----','ooo','////','\\\\\\\\']:
        for i in range(len(df)):
            hatches1.append(h)
    colors1 = []
    for c in ['#ffffff','#ffffff','#ffffff','#ffffff']:
        for i in range(len(df)):
            colors1.append(c)
    edgecolors1 = []
    for ec in ['#0000ff','#800080','#008000','#ff0000']:
        for i in range(len(df)):
            edgecolors1.append(ec)

    for bar, hatch, color, edgecolor in zip(bars1, hatches1, colors1, edgecolors1):
        bar.set_color(color)
        bar.set_hatch(hatch)
        bar.set_edgecolor(edgecolor)

    ax1.legend(loc='upper right', bbox_to_anchor=(1.0, 1.35))

    plt.show()

############################
# Pacific EMIS Style Chart #
############################
def plot_emis(df, label='xlabel', dimension='Students', title='N/A'):
    """A function to plot a DataFrame in EMIS style.

    Parameters
    ----------
    df : DataFrame, required
        The DataFrame to plot the graph with.
    label : String, optional
        A string that will be show in the Y axis label
    dimension : String, options
        A string to modify that X axis label. In general for this plots we have two types of analysis:
            - SOE style of "level counts" or counting of indicators in a particular benchmark/standard/test at each performance level
            - EMIS styles (more common) of counting of students  in a particular benchmark/standard/test at each performance level
    """
    fig2 = plt.figure(figsize=(8, 6)) #, constrained_layout=True) 
    ax2 = plt.subplot() #gs[1]
    df.plot(ax=ax2, kind='barh', stacked=True)

    ax2.set_title('Republic of the Marshall Islands\n{}\nAll Students of AllSchools\nPacific EMIS Chart Style ({})'.format(exam, title), color='black')
    ax2.set_xlabel(label)
    ax2.set_ylabel('Percent of '+dimension+' in Each Performance Level')

    bars2 = ax2.patches

    # Add text to bars
    for bar in bars2:
        # Find where everything is located
        height = bar.get_height()
        width = bar.get_width()
        x = bar.get_x()
        y = bar.get_y()

        # The height of the bar is the data value and can be used as the label
        label_text =f'{abs(width*100):.0f}%'  # f'{width:.2f}' to format decimal values

        label_x = x + width / 2
        label_y = y + height / 2

        # only plot labels greater than given width
        if abs(width) > 0:
            ax2.text(label_x, label_y, label_text, ha='center', va='center', fontsize=8)

    colors2 = []
    for c in ['#92d050','#00b050','#ffc000','#ff0000']:
        for i in range(len(df)):
            colors2.append(c)

    for bar, color in zip(bars2, colors2):
        bar.set_color(color)

    ax2.legend(loc='upper right', bbox_to_anchor=(1.0, 1.5))

    plt.show()


# %%
###############################################################################
# Results Sheet (continue)                                                    #
# Plotting anything and everything                                            #
###############################################################################

###############################################################################
# All available DataFrames for plotting are packaged in the following Dicts
#  * students_each_rubric_level_plottable_dfs = {}
#  * level_count_each_rubric_level_soe_plottable_dfs = {}
# For example, access one like this students_each_rubric_level_plottable_dfs['df_indicators_summary_per']
print("Student count at each rubric level available DataFrames:")
pp.pprint(list(students_each_rubric_level_plottable_dfs.keys()))
print()
print("Level/Indicator counts (not Students) at each rubric level available DataFrames:")
# Following does not have an indicators dataframe since those as merely computed on student
# and thus only part of previous list above.
pp.pprint(list(level_count_each_rubric_level_soe_plottable_dfs.keys()))

###############################################################################
# Reminders:
# students_each_rubric_level_plottable_dfs['df_benchmarks_summary_*'] produce a student count at each rubric level. The levels are calculated as in SOE (e.g. use of A.6.2.1Level columns based on A.6.2.1_L1Percent columns)
# students_each_rubric_level_plottable_dfs['df_benchmarksalt_summary_*'] produce a student count at each rubric level. The levels are calculated based on 4 equal bins from all their respective items directly
# plot_soe(level_count_each_rubric_level_soe_plottable_dfs['df_benchmarks_summary_*']) produces a level count (not sutdent) at each rubric level. This is how SOE produces benchmarks, standards and test analysis
#
# Note that they end up all similar but different results
###############################################################################

###############################################################################
# Indicators analysis
###############################################################################

# Everybody does this one the same hence not all the variations like benchmarks, standards and test are included
#plot_soe(students_each_rubric_level_plottable_dfs['df_indicators_summary_per'], 'Indicators', 'Student', 'Item Count Method') # Student count at each rubric level (SOE Chart Style)
#plot_emis(students_each_rubric_level_plottable_dfs['df_indicators_summary_per_x'], 'Indicators', 'Student', 'Item Count Method') # Student count at each rubric level (EMIS Chart Style)

###############################################################################
# Benchmarks analysis
###############################################################################

#plot_soe(students_each_rubric_level_plottable_dfs['df_benchmarks_summary_per'], 'Benchmarks', 'Student', 'Level Percentage Method') # Student count at each rubric level SOE Extension rules (SOE Chart style)
#plot_soe(students_each_rubric_level_plottable_dfs['df_benchmarksalt_summary_per'], 'Benchmarks', 'Student', 'Item Count Method') # Student count at each rubric level ItemCount rule by passing indicator (SOE Chart Style) (Brian's Candidate Count)
#plot_soe(students_each_rubric_level_plottable_dfs['df_benchmarksweighted_summary_per'], 'Benchmarks', 'Indicators (Level count)', 'Weighted Method') # Level count count at each rubric level using weighting technique (SOE Chart Style)
#plot_soe(level_count_each_rubric_level_soe_plottable_dfs['df_benchmarks_summary_per'], 'Benchmarks', 'Indicators (Level count)', 'Indicators Level Count Method') # SOE's level count technique (SOE Chart style)
plot_emis(students_each_rubric_level_plottable_dfs['df_benchmarks_summary_per_x'], 'Benchmarks', 'Student', 'Level Percentage Method') # Student count at each rubric level ItemCount rule by passing indicator (EMIS Chart Style)
plot_emis(students_each_rubric_level_plottable_dfs['df_benchmarksalt_summary_per_x'], 'Benchmarks', 'Student', 'Item Count Method') # Student count at each rubric level SOE Extension rules (EMIS Chart style) (Brian's Candidate Count)
plot_emis(students_each_rubric_level_plottable_dfs['df_benchmarksweighted_summary_per_x'], 'Benchmarks', 'Indicators (Level count)', 'Weighted Method') # Level count count at each rubric level using weighting technique (EMIS Chart style)
plot_emis(level_count_each_rubric_level_soe_plottable_dfs['df_benchmarks_summary_per_x'], 'Benchmarks', 'Indicators (Level count)', 'Indicators Level Count Method') # SOE's level count technique (EMIS Chart style)

###############################################################################
# Standards analysis
###############################################################################

#plot_soe(students_each_rubric_level_plottable_dfs['df_standards_summary_per'], 'Standard', 'Student', 'Level Percentage Method') # Student count at each rubric level SOE Extension rules (SOE Chart style)
#plot_soe(students_each_rubric_level_plottable_dfs['df_standardsalt_summary_per'], 'Standard', 'Student', 'Item Count Method') # Student count at each rubric level ItemCount rule by passing indicator (SOE Chart Style) (Brian's Candidate Count)
#plot_soe(students_each_rubric_level_plottable_dfs['df_standardsweighted_summary_per'], 'Standard', 'Indicators (Level count)', 'Weighted Method') # Level count count at each rubric level using weighting technique (SOE Chart Style)
#plot_soe(level_count_each_rubric_level_soe_plottable_dfs['df_standards_summary_per'], 'Standard', 'Indicators (Level count)', 'Indicators Level Count Method') # SOE's level count technique (SOE Chart style)
#plot_emis(students_each_rubric_level_plottable_dfs['df_standards_summary_per_x'], 'Standard', 'Student', 'Level Percentage Method') # Student count at each rubric level ItemCount rule by passing indicator (EMIS Chart Style)
#plot_emis(students_each_rubric_level_plottable_dfs['df_standardsalt_summary_per_x'], 'Standard', 'Student', 'Item Count Method') # Student count at each rubric level SOE Extension rules (EMIS Chart style) (Brian's Candidate Count)
#plot_emis(students_each_rubric_level_plottable_dfs['df_standardsweighted_summary_per_x'], 'Standard', 'Indicators (Level count)', 'Weighted Method') # Level count count at each rubric level using weighting technique (EMIS Chart style)
#plot_emis(level_count_each_rubric_level_soe_plottable_dfs['df_standards_summary_per_x'], 'Standard', 'Indicators (Level count)', 'Indicators Level Count Method') # SOE's level count technique (EMIS Chart style)

###############################################################################
# Test analysis
###############################################################################

#plot_soe(students_each_rubric_level_plottable_dfs['df_test_summary_per'], 'Whole test', 'Student', 'Level Percentage Method') # Student count at each rubric level SOE Extension rules (SOE Chart style)
#plot_soe(students_each_rubric_level_plottable_dfs['df_testalt_summary_per'], 'Whole test', 'Student', 'Item Count Method') # Student count at each rubric level ItemCount rule by passing indicator (SOE Chart Style) (Brian's Candidate Count)
#plot_soe(students_each_rubric_level_plottable_dfs['df_testweighted_summary_per'], 'Whole test', 'Indicators (Level count)', 'Weighted Method') # Level count count at each rubric level using weighting technique (SOE Chart Style)
#plot_soe(level_count_each_rubric_level_soe_plottable_dfs['df_test_summary_per'], 'Whole test', 'Indicators (Level count)', 'Indicators Level Count Method') # SOE's level count technique (SOE Chart style)
#plot_emis(students_each_rubric_level_plottable_dfs['df_test_summary_per_x'], 'Whole test', 'Student', 'Level Percentage Method') # Student count at each rubric level ItemCount rule by passing indicator (EMIS Chart Style)
#plot_emis(students_each_rubric_level_plottable_dfs['df_testalt_summary_per_x'], 'Whole test', 'Student', 'Item Count Method') # Student count at each rubric level SOE Extension rules (EMIS Chart style) (Brian's Candidate Count)
#plot_emis(students_each_rubric_level_plottable_dfs['df_testweighted_summary_per_x'], 'Whole test', 'Indicators (Level count)', 'Weighted Method') # Level count count at each rubric level using weighting technique (EMIS Chart style)
#plot_emis(level_count_each_rubric_level_soe_plottable_dfs['df_test_summary_per_x'], 'Whole test', 'Indicators (Level count)', 'Indicators Level Count Method') # SOE's level count technique (EMIS Chart style)

# %%
# Write various DataFrame into Excel to examine (testing)
filename = os.path.join(local_path, 'RMI/soe-assessment-workbook.xlsx')
with pd.ExcelWriter(filename) as writer:
    # add DataFrames you want to write to Excel here
    df_student_results.to_excel(writer, index=False, sheet_name='Responses', engine='openpyxl')
    df_student_results_scores.to_excel(writer, index=False, sheet_name='Scores', engine='openpyxl')
    df_student_results_aggscores.to_excel(writer, index=False, sheet_name='AggregateScores', engine='openpyxl')

# %%

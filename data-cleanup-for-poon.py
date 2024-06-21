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
# This notebook was written to process, cleanup and attempt to retrieve       #
# better student ID and school ID data from MIEMIS on a request from Poon     #
# from Pacific Testing Center (OnlineSBA)                                     #
# An ad-hoc support request that led to a more general and re-usable notebook #
# soe-to-onlinesba.ipynb                                                      #
###############################################################################

# Import core stuff
import json

# Import Data stuff
import pandas as pd # Data analysis
import xlrd # excel 
from sqlalchemy.engine import URL # SQL DB
from sqlalchemy import create_engine

# fuzz is used to compare TWO strings
from fuzzywuzzy import fuzz
# process is used to compare a string to MULTIPLE other strings
from fuzzywuzzy import process

# Configuration
with open('config.json', 'r') as file:
     config = json.load(file)

# It is important to keep the order of the cells since there are inplace 
# operations on DataFrames

# %%
# Process data into a cleanish DataFrame
import os

local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
f = os.path.join(local_path, 'RMI/poon-cleanup-request/M03 2019.xlsx')

df_exams = pd.read_excel(f, index_col=None, header=0, engine='openpyxl')
df_exams.dropna(how='all',inplace=True)
df_exams.reset_index(drop=True, inplace=True)
df_exams


# investigate [nan, 'MH010787', None, 'MH009285', 'MH035753'] # They exists here!!!
#df_exams[df_exams['STUDENTNAME'] == 'Rine Sam']
#df_exams[df_exams['STUDENTNAME'] == 'Rine Sam'].STUDENTNAME

#len(df_exams['STUDENTID'].unique())

# %%
# Load the relevant student enrollments from the database
# there we have all known students loaded from census year after year
enrol_year = 2019

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
engine = create_engine(connection_url)


query = """
SELECT
	stuCardID
	, CONCAT(stuGiven,' ',stuFamilyName) AS Student -- stuMiddleNames,' ',
	, stuGender
	, stuDoB
	, schNo
	, stueYear
	FROM Student_ S
	INNER JOIN StudentEnrolment_ SE ON S.stuID = SE.stuID
	WHERE stueYear = {0}
""".format(enrol_year)

with engine.begin() as sql_conn:
    df_student_enrol = pd.read_sql_query(query, sql_conn)
    display(df_student_enrol)

#df_student_enrol.head(3)
#df_student_enrol.count()
#df_student_enrol[df_student_enrol['Student'].str.contains('Ranny George', case=False)]

# investigate [nan, 'MH010787', None, 'MH009285', 'MH035753'] 
# They existed here but pandas does not equate as there were spaces to trim!!!
#df_student_enrol[df_student_enrol['stuCardID'] == 'MH035753']
#df_student_enrol[df_student_enrol['stuCardID'] == 'MH035753'].Student
#df_student_enrol[df_student_enrol['Student'].str.strip() == 'Rine Sam']

# %%
# Merge both the dirty exams data with the clean student enrollments dataset

   
# lower case to make join case insensitive (like SQL Server, the default collation of Pacific EMIS anyway)
df_exams['STUDENTNAME'] = df_exams['STUDENTNAME'].str.lower()
df_student_enrol['Student'] = df_student_enrol['Student'].str.lower()

# Also need to trim spaces to make it exactly like the SQL Server join
df_exams['STUDENTNAME'] = df_exams['STUDENTNAME'].str.strip()
df_student_enrol['Student'] = df_student_enrol['Student'].str.strip()

#df_exams_and_students = df_exams.set_index('STUDENTNAME').join(df_student_enrol.set_index('Student'), lsuffix='_caller', rsuffix='_other')
df_exams_and_students = df_exams.merge(df_student_enrol, how='left', left_on='STUDENTNAME', right_on='Student', suffixes=('_from_exams', '_from_db'))
df_exams_and_students

#df_exams_and_students[df_exams_and_students[STUDENTID=='Ranny George']]
#df_exams_and_students.loc['Ranny George']
#df_exams_and_students.loc['RANNY GEORGE']
#df_exams_and_students[df_exams_and_students[schNo=='MH000036']]


# %%
# Get the duplicates. This could be that there are two or more matches
# of exams students into the clean DB students enrollments
# (e.g. same name, different student, which one is it?)
#df_exams_and_students_dups = df_exams_and_students[df_exams_and_students.index.duplicated(keep=False)]
df_exams_and_students_dups = df_exams_and_students[df_exams_and_students['STUDENTNAME'].duplicated(keep=False)]
df_exams_and_students_dups

# %%
# Get the exact matches (i.e. exact name in exams data and the database)
# not actually using this, included for observations. We'll be using fuzzy matching
df_exact_matches = df_exams_and_students.dropna(how='all', subset=['stuCardID']) #subset=['stuCardID', 'stuGender', 'stuDoB', 'schNo', 'stueYear'])
df_exact_matches

# %%
# Troubleshooting differences with SQL
# No longer needed
#query2 = """
#SELECT * FROM [dbo].[StudentMISATData] AS SMISAT LEFT JOIN 
#(SELECT
#	stuCardID
#	, CONCAT(stuGiven,' ',stuFamilyName) AS Student -- stuMiddleNames,' ',
# 	, stuGender
# 	, stuDoB
# 	, schNo
# 	, stueYear
# 	FROM Student_ S
# 	INNER JOIN StudentEnrolment_ SE ON S.stuID = SE.stuID
# 	WHERE stueYear = 2019) AS S ON SMISAT.STUDENTNAME = S.Student
# """   
# df_student_enrol2 = pd.read_sql(query2, sql_conn)
# df_student_enrol2

# # investigate [nan, 'MH010787', None, 'MH009285', 'MH035753']
# s = df_exams_and_students['stuCardID']
# s.isna().sum()
# l = list(s)
# df_exams_and_students[df_exams_and_students['stuCardID'] == 'MH035753']
# df_exams_and_students[df_exams_and_students['Student'] == 'Rine Sam']
# df_exams_and_students[df_exams_and_students['STUDENTNAME'] == 'Rine Sam']

# s2 = df_student_enrol2['stuCardID']
# s2.isna().sum()
# l2 = list(s2)

# df_student_enrol2[df_student_enrol2['stuCardID'] == 'MH035753']
# df_student_enrol2[df_student_enrol2['Student'] == 'Rine Sam']
# df_student_enrol2[df_student_enrol2['STUDENTNAME'] == 'Rine Sam']

#common_cols = list(set(df_exams_and_students.columns) & set(df_student_enrol2.columns))
#common_cols

#pd.merge(df_exams_and_students, df_student_enrol2, how='right', left_on='STUDENTNAME', right_on='Student')

# Python code t get difference of two lists
# Using set()
# def Diff(li1, li2):
#     return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))
 
# # Driver Code
# li1 = [10, 15, 20, 25, 30, 35, 40]
# li2 = [25, 40, 35]
# print(Diff(l, l2))

# %%
# resources http://jonathansoma.com/lede/algorithms-2017/classes/fuzziness-matplotlib/fuzzing-matching-in-pandas-with-fuzzywuzzy/
# Scores: 100 is 100% matching
#print(fuzz.ratio("ghislain hachey", "gislain hachey")) # compares entire string in order
#print(fuzz.partial_ratio("ghislain timbasal", "ghislain hachey")) # compare subsection of the string
#print(fuzz.token_sort_ratio("ghislain hachey", "hachey ghislain")) # ignores work order
#print(fuzz.token_sort_ratio("ghislain hachey", "hachey gislain")) # ignores work order
#print(fuzz.token_set_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear")) # ignore duplicate words

# fuzzy on  a dataset
#choices = ['fuzzy fuzzy was a bear', 'is this a test', 'THIS IS A TEST!!']
#process.extract("this is a test", choices, scorer=fuzz.ratio)

# def fuzzy_merge(df1, df2, key1, key2, threshold=90, limit=2):
#     """
#     :param df1: the left table to join
#     :param df2: the right table to join
#     :param key1: key column of the left table
#     :param key2: key column of the right table
#     :param threshold: how close the matches should be to return a match, based on Levenshtein distance
#     :param limit: the amount of matches that will get returned, these are sorted high to low
#     :return: dataframe with boths keys and matches
#     """
#     s = df2[key2].tolist()

#     m = df1[key1].apply(lambda x: process.extract(x, s, limit=limit))    
#     df_1['matches'] = m

#     m2 = df1['matches'].apply(lambda x: ', '.join([i[0] for i in x if i[1] >= threshold]))
#     df1['matches'] = m2

#     return df1

#df_exams.merge(df_student_enrol, how='left', left_on='STUDENTNAME', right_on='Student', suffixes=('_from_exams', '_from_db'))
#fuzzy_merge(df_exams, df_student_enrol, 'STUDENTNAME', 'Student', 80)

# %%
# %%time

# Let's get try a bit of fuzzy search see if we can get more students matching
# This fuzzy_pandas package is seamingly more straight forward
import fuzzy_pandas as fpd

exams_cols = list(set(df_exams.columns))
stuen_cols = list(set(df_student_enrol.columns))

df_fuzzy_matches = fpd.fuzzy_merge(
    df_exams, df_student_enrol,
    left_on=['STUDENTNAME'], right_on=['Student'],
    #keep='all',
    method='levenshtein',
    threshold=0.9,
    ignore_case=True,
    ignore_nonalpha=False,
    ignore_nonlatin=False,
    ignore_order_words=False,
    ignore_order_letters=False,
    ignore_titles=False,
    join='left-outer' # { 'inner', 'left-outer', 'right-outer', 'full-outer' }
)

df_fuzzy_matches

#s = df_fuzzy_matches['stuCardID'] == ''
#s.sum()

# %%
# Repackage the data into the original format for the exams system
df_fuzzy_matches

df_fuzzy_cleaned = df_fuzzy_matches.drop(['SCHOOLID','GENDER','stueYear'] , axis='columns')
df_fuzzy_cleaned.rename(columns={'STUDENTID':'STUDENTID_ORIG','stuCardID':'STUDENTID','stuGender':'GENDER','schNo':'SCHOOLID'}, inplace=True)
df_fuzzy_cleaned = df_fuzzy_cleaned[[
    'STUDENTID_ORIG', 'STUDENTID', 'SPED', 'ACCOM', 'STUDENTNAME', 'Student', 'stuDoB', 'SCHOOLID', 'GENDER', 'TESTID', 'TEACHERNAME', 
    'ITEM_001', 'ITEM_002', 'ITEM_003', 'ITEM_004',
    'ITEM_005', 'ITEM_006', 'ITEM_007', 'ITEM_008', 'ITEM_009', 'ITEM_010',
    'ITEM_011', 'ITEM_012', 'ITEM_013', 'ITEM_014', 'ITEM_015', 'ITEM_016',
    'ITEM_017', 'ITEM_018', 'ITEM_019', 'ITEM_020', 'ITEM_021', 'ITEM_022',
    'ITEM_023', 'ITEM_024', 'ITEM_025', 'ITEM_026', 'ITEM_027', 'ITEM_028',
    'ITEM_029', 'ITEM_030', 'ITEM_031', 'ITEM_032', 'END']]

# minor cleanup of teacher names: at least remove white spaces :)
df_fuzzy_cleaned['TEACHERNAME'] = df_fuzzy_cleaned['TEACHERNAME'].str.strip()
#df_teacher_school[df_teacher_school['TEACHERNAME'] == 'Jiem Lakmej']

# Re camel case student names
df_fuzzy_cleaned['STUDENTNAME']= df_fuzzy_cleaned['STUDENTNAME'].str.title()
df_fuzzy_cleaned['Student']= df_fuzzy_cleaned['Student'].str.title()

df_fuzzy_cleaned.sort_values(by=['STUDENTID_ORIG'])
#df_fuzzy_cleaned.columns
#len(df_fuzzy_cleaned['STUDENTID_ORIG'].unique())

# %%
# Now try some educated 'guesses'. Set the school based on known variable:
# the teachers' most commonly supervised school
df_teacher_school = df_fuzzy_cleaned[['SCHOOLID','TEACHERNAME']].copy()

# All teachers with known schools based on fuzzy search on students in EMIS data
df_teacher_with_school = df_teacher_school[df_teacher_school['SCHOOLID'] != ''].copy()

# All students remaining with no schools (or gender) known from fuzzy searching EMIS data
df_teacher_no_school = df_teacher_school[df_teacher_school['SCHOOLID'] == ''].copy()

#df_teacher_with_school#.groupby(by='TEACHERNAME')
df_teacher_with_school_occurance = df_teacher_with_school.value_counts(sort=True, ascending=False)
df_teacher_with_school_occurance = df_teacher_with_school_occurance.reset_index().groupby('TEACHERNAME').first()
del df_teacher_with_school_occurance[0]
teacher_school = df_teacher_with_school_occurance.to_dict()['SCHOOLID']
teacher_school

# %%
# Start by assigning a best guess school to all remaining records without one
# However, only do this on the subset of rows with no acquired 
# information from the EMIS DB
df_fuzzy_cleaned[['SCHOOLID','TEACHERNAME']]
df_fuzzy_cleaned.loc[df_fuzzy_cleaned['SCHOOLID'] == '', ['SCHOOLID']] = df_fuzzy_cleaned['TEACHERNAME'].map(teacher_school)
df_fuzzy_cleaned

# %%
# Write processed data back into excel for final scrutiny
f_cleaned = os.path.join(cwd, 'data/RMI/poon-cleanup-request/M03 2019-cleaned.xlsx')
df_fuzzy_cleaned.to_excel(f_cleaned, index=False, sheet_name='M03 2019', engine='openpyxl')

# %%

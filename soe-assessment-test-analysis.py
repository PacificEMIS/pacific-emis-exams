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
# This notebook is a SOE Assessment Test Analysis.                            #
###############################################################################
# Core stuff
import os
from pathlib import Path
import re
import json

import random
import string

# Data stuff
import pandas as pd # Data analysis
import numpy as np
import math

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

def save(df, filename, as_string):
    # Generate the output file path with -anonymized added
    file_root, file_ext = os.path.splitext(filename)
    filename_as_string = f"{file_root}{as_string}{file_ext}"
    
    # Save the anonymized data to the new file
    if file_ext in ['.csv']:
        df.to_csv(filename_as_string, index=False)
        print(f"Saving {filename_as_string}")
    elif file_ext in ['.xls', '.xlsx']:
        df.to_excel(filename_as_string, index=False)
        print(f"Saving {filename_as_string}")
    else:
        raise ValueError(f"Unsupported file extension: {file_ext}")


# %%
###############################################################################
# Response Sheet                                                              #
###############################################################################

# Load a single SOE Assessment workbook (for testing,)
# in particular the sheet with the raw data
local_path = os.path.abspath('/mnt/h/Development/Pacific EMIS/repositories-data/pacific-emis-exams/')
filename = os.path.join(local_path, 'RMI/soe-load-files/e33a8ebb-2d79-411f-a7a6-d3f4c443906b.xlsx')

df_student_results = load_excel_to_df(filename)
print('df_student_results')
display(df_student_results)


# %%
# Function to generate a unique fictitious name
def generate_fictitious_name(existing_names):
    while True:
        name = ''.join(random.choices(string.ascii_uppercase, k=5))
        if name not in existing_names:
            existing_names.add(name)
            return name

# Initialize sets to keep track of used fictitious names
student_names = set()
teacher_names = set()

# Create mappings for student and teacher names
student_name_mapping = {name: generate_fictitious_name(student_names) for name in df_student_results['STUDENTNAME'].unique()}
teacher_name_mapping = {name: generate_fictitious_name(teacher_names) for name in df_student_results['TEACHERNAME'].unique()}

# Replace the names in the DataFrame
df_student_results['STUDENTNAME'] = df_student_results['STUDENTNAME'].map(student_name_mapping)
df_student_results['TEACHERNAME'] = df_student_results['TEACHERNAME'].map(teacher_name_mapping)

# Display the first few rows to verify
display(df_student_results)

save(df_student_results, filename, '-anonymized')


# %%
# Function to extract item information from the column name
def extract_item_info(column_name):
    match = re.match(r"ITEM_(\d+)_([A-Z0-9]+)_([A-Z]+)$", column_name)
    if match:
        item_number = match.group(1)
        item_details = match.group(2)
        correct_answer = match.group(3)[0]
        return item_number, item_details, correct_answer
    return None, None, None

# Initialize lists to store extracted information
item_numbers = []
item_details = []
correct_answers = []

# Convert column names to uppercase
df_student_results.columns = [col.upper() for col in df_student_results.columns]

# Extract item information from each item column
for column in df_student_results.columns:
    if column.startswith('ITEM_'):
        item_number, item_detail, correct_answer = extract_item_info(column)
        item_numbers.append(item_number)
        item_details.append(item_detail)
        correct_answers.append(correct_answer)

# Create a DataFrame with the extracted item information
item_info_df = pd.DataFrame({
    'Item Number': item_numbers,
    'Item Details': item_details,
    'Correct Answer': correct_answers
})

# Display the item information DataFrame
display(item_info_df)


# %%
# Function to check if the student's answer is correct
def is_correct_answer(student_answer, correct_answer):
    return 1 if str(student_answer).strip().upper() == correct_answer else 0

# Initialize a DataFrame to store the results
df_results = df_student_results.copy()

# Calculate the score for each item
for column in df_student_results.columns:
    if column.startswith('ITEM_'):
        item_number, item_detail, correct_answer = extract_item_info(column)
        if correct_answer:
            df_results[f'{column}_CORRECT'] = df_student_results[column].apply(is_correct_answer, correct_answer=correct_answer)

# Calculate the total score for each student
df_results['TOTAL_SCORE'] = df_results.filter(like='_CORRECT').sum(axis=1)

# Display the results DataFrame
display(df_results)
save(df_results, filename, '-with-scores')

# %%
# Extract columns containing 'SCORE' in their names but excluding 'MAXSCORE', 'SCORE_RATIO', 'SCORE_TOTAL', and 'SCORE_TOTAL_MAX'
score_columns = [col for col in df_results.columns if 'CORRECT' in col]

# Summary statistics for each score column
score_statistics = df_results[score_columns].describe()

# Display the statistics
print("Summary Statistics for SCORE Columns:")
display(score_statistics)

# %%
################################################################################
# Calculate Cronbach's alpha
################################################################################

# Subset the data to include only the score columns
df_scores = df_results[score_columns]

# Calculate the number of items
n_items = len(score_columns)
print(f"Number of items: {n_items}")

# Calculate the variance for each item
item_variances = df_scores.var(axis=0, ddof=1)
#print(f"Item variances: {item_variances.head()}")
print(f"Sum of item variances: {item_variances.sum()}")

# Calculate the total score for each participant
total_scores = df_scores.sum(axis=1)
#print(f"Total scores: {total_scores.head()}")
# Calculate the standard deviation of totals
std_dev_totals = total_scores.std()
print(f"Standard Deviation of Totals: {std_dev_totals}")

# Calculate the variance of the total scores
total_score_variance = total_scores.var(ddof=1)
print(f"Total scores variance: {total_score_variance}")

# Calculate Cronbach's alpha
cronbach_alpha = (n_items / (n_items - 1)) * (1 - (item_variances.sum() / total_score_variance))

print(f"Cronbach's Alpha: {cronbach_alpha}")

# Calculate SEM
sem = std_dev_totals * (1 - cronbach_alpha) ** 0.5
print(f"Standard Error of Measurement: {sem}")

# %%
# Define the item column to analyze
item_column = 'ITEM_001_MS0601010101E_DDD'

# Function to extract the correct answer from the item column name
def extract_correct_answer(column_name):
    match = re.match(r"ITEM_(\d+)_([A-Z0-9]+)_([A-Z]{3})$", column_name)
    if match:
        correct_answer = match.group(3)[0]  # Take only the first letter of the correct answer
        return correct_answer
    return None

# Extract the correct answer for the item
correct_answer = extract_correct_answer(item_column)

# Function to count the number of candidates for each possible answer
def count_candidates(item_column):
    answers = ['A', 'B', 'C', 'D']
    counts = {answer: 0 for answer in answers}
    
    for answer in df_results[item_column]:
        if str(answer).strip().upper() in counts:
            counts[str(answer).strip().upper()] += 1
    
    return counts

# Count the number of candidates for each possible answer
counts = count_candidates(item_column)

# Create a DataFrame with the results
df_item_analysis = pd.DataFrame({
    'Answer': list(counts.keys()),
    'Number of Candidates': list(counts.values())
})

# Calculate the percentage of candidates for each answer
total_candidates = df_item_analysis['Number of Candidates'].sum()
df_item_analysis['Percentage of Candidates'] = (df_item_analysis['Number of Candidates'] / total_candidates) * 100

# Add a column to indicate the correct answer
df_item_analysis['Is Correct'] = df_item_analysis['Answer'] == correct_answer

# Display the DataFrame with conditional formatting
def highlight_correct(s):
    return ['background-color: lime' if is_correct else '' for is_correct in s]

df_styled = df_item_analysis.style.apply(highlight_correct, subset=['Is Correct'])
df_styled = df_styled.format({'Percentage of Candidates': '{:.2f}%'})

display(df_styled)


# %%
import matplotlib.pyplot as plt

# Create a pie chart based on the df_item_analysis DataFrame
fig, ax = plt.subplots()

# Plot the pie chart
wedges, texts, autotexts = ax.pie(
    df_item_analysis['Number of Candidates'],
    labels=df_item_analysis['Answer'],
    autopct='%1.1f%%',
    startangle=90,
    colors=['blue', 'orange', 'green', 'red']
)

# Highlight the correct answer
correct_answer_index = df_item_analysis[df_item_analysis['Answer'] == correct_answer].index[0]
wedges[correct_answer_index].set_edgecolor('lime')
wedges[correct_answer_index].set_linewidth(2)

# Add a title
plt.title('Distribution of Candidates\' Answers')

# Display the pie chart
plt.show()

# %%
import pandas as pd
import re

# Assuming df_results is already defined and contains the necessary data

# Function to extract expected difficulty from the item column name
def extract_expected_difficulty(column_name):
    match = re.match(r"ITEM_(\d+)_([A-Z0-9]+)([EMH])_([A-Z]{3})$", column_name)
    if match:
        expected_difficulty = match.group(3).lower()  # Extract and convert to lowercase
        if expected_difficulty == 'h':
            return 'Hard'
        elif expected_difficulty == 'e':
            return 'Easy'
        elif expected_difficulty == 'm':
            return 'Moderate'
        else:
            return 'Error'
    return None

# Function to calculate assessed difficulty
def calculate_assessed_difficulty(correct_answers, total_answers):
    percentage_correct = (correct_answers / total_answers) * 100
    if percentage_correct < 33.33:
        return 'Hard'
    elif percentage_correct > 66.66:
        return 'Easy'
    else:
        return 'Moderate'

# Initialize lists to store the difficulty levels
expected_difficulties = []
assessed_difficulties = []

# Iterate through each item column to extract expected difficulty and calculate assessed difficulty
for column in df_results.columns:
    if column.startswith('ITEM_') and column.endswith('_CORRECT'):
        # Extract expected difficulty
        base_column_name = column[:-8]  # Remove '_CORRECT' to get the base column name
        expected_difficulty = extract_expected_difficulty(base_column_name)
        
        # Calculate assessed difficulty
        total_answers = len(df_results)
        correct_answers = df_results[column].sum()
        assessed_difficulty = calculate_assessed_difficulty(correct_answers, total_answers)
        
        expected_difficulties.append(expected_difficulty)
        assessed_difficulties.append(assessed_difficulty)

# Create a DataFrame with the difficulty comparison report
df_difficulty_comparison = pd.DataFrame({
    'Item': [col[:-8] for col in df_results.columns if col.startswith('ITEM_') and col.endswith('_CORRECT')],
    'Expected Difficulty': expected_difficulties,
    'Assessed Difficulty': assessed_difficulties
})

# Display the DataFrame
#df_styled = df_difficulty_comparison.style.applymap(lambda x: 'background-color: lightgreen' if x == 'easy' else ('background-color: lightcoral' if x == 'hard' else 'background-color: lightyellow'), subset=['Assessed Difficulty'])
df_difficulty_comparison

# %%
import pandas as pd

# Assuming df_results is already defined and contains the necessary data

# Define the item column to analyze
item_column = 'ITEM_001_MS0601010101E_DDD_CORRECT'

# Calculate the total score for each student
df_results['TOTAL_SCORE'] = df_results.filter(like='_CORRECT').sum(axis=1)

# Rank students based on their total scores
df_results['RANK'] = df_results['TOTAL_SCORE'].rank(ascending=False, method='first')
#print("df_resuts ranked:")
#display(df_results)

# Calculate the number of students in each group
num_students = len(df_results)
num_top_bottom = math.ceil(num_students * 0.27)
num_middle = num_students - (num_top_bottom*2)

# Sort the dataframe by rank
df_sorted = df_results.sort_values(by='RANK')
save(df_sorted, filename, '-sorted')

# Select top and bottom 27% of students (and middle 46%)
top_27_percent = df_sorted.head(num_top_bottom)
bottom_27_percent = df_sorted.tail(num_top_bottom)
middle_46_percent = df_sorted.iloc[num_top_bottom:-num_top_bottom]

# Calculate the rate of correct answers for the top, middle, and bottom groups
top_group_correct = top_27_percent[item_column].sum()
middle_group_correct = middle_46_percent[item_column].sum()
bottom_group_correct = bottom_27_percent[item_column].sum()
total_group_correct = top_group_correct + middle_group_correct + bottom_group_correct
print(f"top_group_correct: {top_group_correct}")
print(f"middle_group_correct: {middle_group_correct}")
print(f"bottom_group_correct: {bottom_group_correct}")
print(f"total_group_correct: {total_group_correct}")

top_group_correct_rate = top_group_correct / num_top_bottom
middle_group_correct_rate = middle_group_correct / num_middle
bottom_group_correct_rate = bottom_group_correct / num_top_bottom
total_group_correct_rate = total_group_correct / num_students
print(f"top_group_correct_rate: {top_group_correct_rate}")
print(f"middle_group_correct_rate: {middle_group_correct_rate}")
print(f"bottom_group_correct_rate: {bottom_group_correct_rate}")
print(f"total_group_correct_rate: {total_group_correct_rate}")

# Compute the discrimination index
discrimination_index = top_group_correct_rate - bottom_group_correct_rate

# Compute the discrimination index
discrimination_index = top_group_correct_rate - bottom_group_correct_rate

discrimination_index

# NOTE: that the final correct rates and thus the discrimination index will vary a little
# from live Pacific EMIS. The reason is in the ranking and thus the final selection of the 
# top and bottom students. The EMIS will sort by exam candidate ID and essentially randomly
# cutoff at 27% (top and bottom) where you would generally get equiqually performing students.
# Due to a lot of "ties" one has no choice to do this. 

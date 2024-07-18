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
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import pdfkit
import json
from pathlib import Path
import openpyxl

# Configuration (initial setup)
with open('config.json', 'r') as file:
     config = json.load(file)
    
tao_local_path = config['tao_local_path']

# Define the file path
file_path = 'path_to_your_file.csv'  # Replace with your actual file path

result_dir = os.path.join(tao_local_path, 'results_exports')

# Choose with file to work with
#result_filename = 'delivery_of_mathematics_practice_test_2020_v1_i16066499465949598_2024070317025365.csv'
result_filename = 'delivery_of_english_language_arts_practice_test_2020_v1_i160664998645852_2024070317033875.xlsx'
filename = os.path.join(result_dir, result_filename)


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

def save_df_to_file(df, filename):
    """Saves an Pandas DataFrame to a file handling the file type.

    Parameters
    ----------
    filename : str, required
        The filename of the excel file to load
    df : DataFrame, required
        The Pandas DataFramw to save to file

    Raises
    ------
    NotImplementedError
        Could raise unknown error. Implement if it happens
    
    Returns
    -------
    None
    """
    file_path = Path(filename)
    file_extension = file_path.suffix.lower()[1:]

    if file_extension == 'xlsx':
        df.to_excel(filename, index=False)  # index=False to avoid saving the index as a column
    elif file_extension == 'xls':
        df.to_excel(filename, index=False)  # index=False to avoid saving the index as a column
    elif file_extension == 'csv':
        df.to_csv(filename, index=False)
    else:
        raise Exception(f"File type {file_extension} not supported")

    print(f"Saved file {filename}")


# %%
################################################################################
# Load the file into a DataFrame
################################################################################
df_data = load_excel_to_df(filename)

print('df_data preview')
display(df_data[:3])

print('df_date info')
print(df_data.info())

print('df_date columns')
print(list(df_data.columns))

# %%
# Create a copy of df_data to work on
df_data_filled_missing = df_data.copy()

# Extract columns containing 'SCORE' in their names but excluding 'MAXSCORE', 'SCORE_RATIO', 'SCORE_TOTAL', and 'SCORE_TOTAL_MAX'
score_columns = [col for col in df_data_filled_missing.columns if 'SCORE' in col and all(exclusion not in col for exclusion in ['MAXSCORE', 'SCORE_RATIO', 'SCORE_TOTAL', 'SCORE_TOTAL_MAX'])]

# Extract columns containing 'duration' in their names
duration_columns = [col for col in df_data_filled_missing.columns if 'duration' in col]

# Define the function to fill missing data
def fill_missing_data(df, score_col):
    item_prefix = score_col.replace('-SCORE', '')
    df.loc[df[score_col].isnull(), f'{item_prefix}-MAXSCORE'] = 1
    df.loc[df[score_col].isnull(), f'{item_prefix}-RESPONSE'] = np.nan
    df.loc[df[score_col].isnull(), score_col] = 0
    df.loc[df[score_col].isnull(), f'{item_prefix}-completionStatus'] = np.nan
    df.loc[df[score_col].isnull(), f'{item_prefix}-duration'] = np.nan
    df.loc[df[score_col].isnull(), f'{item_prefix}-numAttempts'] = np.nan

# Apply the function to each 'SCORE' column
for score_col in score_columns:
    fill_missing_data(df_data_filled_missing, score_col)

# Calculate the total score for each participant as the sum of SCORE = 1 divided by the total number of items
computed_scores = df_data_filled_missing[score_columns].sum(axis=1) / len(score_columns)
# Identify the position to insert the new column
score_ratio_columns = [col for col in df_data_filled_missing.columns if '-SCORE_RATIO' in col]
if score_ratio_columns:
    insert_position = df_data_filled_missing.columns.get_loc(score_ratio_columns[0]) + 1
else:
    insert_position = len(df_data_filled_missing.columns)

# Insert the new column into the specified position
df_data_filled_missing = pd.concat([
    df_data_filled_missing.iloc[:, :insert_position],
    pd.DataFrame({'Computed_Test_SCORE_RATIO': computed_scores}),
    df_data_filled_missing.iloc[:, insert_position:]
], axis=1)

# Display the first few rows to verify the insertion
df_data_filled_missing.head()

# Save the modified DataFrame to a new file
output_filename = filename.split('.')[0]+'-filled-missing.'+filename.split('.')[1]
save_df_to_file(df_data_filled_missing, output_filename)

# %%
# Summary statistics for each score column
score_statistics = df_data[score_columns].describe()
score_statistics_filled_missing = df_data_filled_missing[score_columns].describe()

# Display the statistics
print("Summary Statistics for SCORE Columns (original):")
display(score_statistics)
print("Summary Statistics for SCORE Columns (filled missing):")
display(score_statistics_filled_missing)

# %%
# Check for missing values in each score column
missing_values = df_data[score_columns].isnull().sum()

print("\nMissing Values in SCORE Columns (from original):")
print(missing_values)

# Identify the unique identifier for users (e.g., email or name)
# Assuming 'First Name', 'Last Name', and 'Mail' are the identifiers
user_identifiers = ['First Name', 'Last Name', 'Mail']

# Create a dictionary to store users who missed each item
missing_items = {col: df_data[user_identifiers + [col]][df_data[col].isnull()] for col in score_columns}

# Display the users who missed each item
#for item, users in missing_items.items():
#    print(f"Users who missed {item}:")
#    print(users[user_identifiers])
#    print("\n")

# %%
################################################################################
# Simple plot of the data
################################################################################

# Count the number of participants scoring 1 and 0 for each item
score_1_counts = df_data_filled_missing[score_columns].apply(lambda x: (x == 1).sum())
score_0_counts = df_data_filled_missing[score_columns].apply(lambda x: (x == 0).sum())

# Combine counts into a DataFrame and sort by score_1_counts
score_counts = pd.DataFrame({'score_1_counts': score_1_counts, 'score_0_counts': score_0_counts})
score_counts = score_counts.sort_values(by='score_1_counts', ascending=False)

# Plot the number of participants scoring 1 and 0 for each item in groups of 10
group_size = 10
num_groups = (len(score_counts) + group_size - 1) // group_size  # Calculate the number of groups

for i in range(num_groups):
    start = i * group_size
    end = start + group_size
    plt.figure(figsize=(14, 7))
    plt.bar(score_counts.index[start:end], score_counts['score_1_counts'][start:end], color='green', label='SCORE = 1')
    plt.bar(score_counts.index[start:end], score_counts['score_0_counts'][start:end], bottom=score_counts['score_1_counts'][start:end], color='red', label='SCORE = 0')
    plt.title(f'Number of Participants Scoring 1 and 0 for Items {start + 1} to {min(end, len(score_counts))}')
    plt.xlabel('Item')
    plt.ylabel('Number of Participants')
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()


# %%
################################################################################
# Process simple reports
################################################################################

# Select relevant columns for the report
report_df = df_data_filled_missing[['First Name', 'Last Name', 'Mail', 'Computed_Test_SCORE_RATIO']]

# Sort the DataFrame by the computed test score in descending order
report_df = report_df.sort_values(by='Computed_Test_SCORE_RATIO', ascending=False)

# Format the score as percentage using .loc to avoid the warning
report_df.loc[:, 'Computed_Test_SCORE_RATIO'] = (report_df['Computed_Test_SCORE_RATIO']*100).map("{:.2f}%".format)

display(report_df)

# Style the DataFrame for HTML output
def color_score(val):
    score = float(val[:-1])
    color = 'green' if score >= 70.00 else 'red'
    return f'color: {color}'

styled_report = report_df.style.map(color_score, subset=['Computed_Test_SCORE_RATIO'])

# Save the styled DataFrame as an HTML file
# Save the modified DataFrame to a new file

html_filename = filename.split('.')[0]+'-report.html'
excel_filename = filename.split('.')[0]+'-report.xlsx'
pdf_filename = filename.split('.')[0]+'-report.pdf'

html = styled_report.to_html()
with open(html_filename, 'w') as f:
    f.write(html)

# Save the DataFrame as an Excel file
save_df_to_file(report_df, excel_filename)

# Convert the HTML report to PDF
pdfkit.from_file(html_filename, pdf_filename)

# %%
################################################################################
# Calculate Cronbach's alpha
################################################################################

# Subset the data to include only the score columns
scores_df = df_data_filled_missing[score_columns]

# Calculate the number of items
n_items = len(score_columns)
print(f"Number of items: {n_items}")

# Calculate the variance for each item
item_variances = scores_df.var(axis=0, ddof=1)
#print(f"Item variances: {item_variances}")
print(f"Sum of item variances: {item_variances.sum()}")

# Calculate the total score for each participant
total_scores = scores_df.sum(axis=1)
#print(f"Total scores: {total_scores}")

# Calculate the variance of the total scores
total_score_variance = total_scores.var(ddof=1)
print(f"Total scores variance: {total_score_variance}")

# Calculate Cronbach's alpha
cronbach_alpha = (n_items / (n_items - 1)) * (1 - (item_variances.sum() / total_score_variance))

print(f"Cronbach's Alpha: {cronbach_alpha}")

# %%
################################################################################
# Anonymize the data (useful for sharing with ChatGPT or others)
################################################################################

import random
import string

df_anonymized = df_data_filled_missing.copy()

# Function to generate a unique fictitious name
def generate_fictitious_name(existing_names):
    while True:
        name = ''.join(random.choices(string.ascii_uppercase, k=5))
        if name not in existing_names:
            existing_names.add(name)
            return name

# Columns of interest to anonymize
#'Test Taker', 'Login', 'First Name', 'Last Name', 'Mail',

# Initialize sets to keep track of used fictitious names
teacher_first_names = set()
teacher_last_names = set()

# Create mappings for student and teacher names
teacher_first_name_mapping = {name: generate_fictitious_name(teacher_first_names) for name in df_anonymized['First Name'].unique()}
teacher_last_name_mapping = {name: generate_fictitious_name(teacher_last_names) for name in df_anonymized['Last Name'].unique()}

# Replace the names in the DataFrame
df_anonymized['First Name'] = df_anonymized['First Name'].map(teacher_first_name_mapping)
df_anonymized['Last Name'] = df_anonymized['Last Name'].map(teacher_last_name_mapping)
df_anonymized['Test Taker'] = df_anonymized['First Name'] + ' ' + df_anonymized['Last Name']
df_anonymized['Login'] = df_anonymized['First Name'] + df_anonymized['Last Name']
df_anonymized['Mail'] = df_anonymized['Login'].str.lower() + '@example.com'

df_anonymized.insert(0, 'row', range(len(df_anonymized)))

# Display the first few rows to verify
display(df_anonymized[:3])

output_filename = filename.split('.')[0]+'-anonymized.'+filename.split('.')[1]
save_df_to_file(df_anonymized, output_filename)

# %%
################################################################################
# Extract RESPONSEs and SCOREs to analyse them
################################################################################

# Drop all columns except 'row' and those matching 'RESPONSE' and 'SCORE' but not 'MAXSCORE'
columns_to_keep = ['row'] + [col for col in df_anonymized.columns if ('RESPONSE' in col or 'SCORE' in col) and 'MAXSCORE' not in col]
df_anonymized_filtered = df_anonymized[columns_to_keep]

# Display the first few rows of the filtered DataFrame
df_anonymized_filtered.head()

# Select RESPONSE columns
response_columns = [col for col in df_anonymized_filtered.columns if 'RESPONSE' in col]
score_columns = [col for col in df_anonymized_filtered.columns if 'SCORE' in col]

# Melt the DataFrame to unpivot the RESPONSE columns
df_melted_response = df_anonymized_filtered.melt(id_vars=['row'], value_vars=response_columns, 
                                        var_name='item', value_name='result')
df_melted_score = df_anonymized_filtered.melt(id_vars=['row'], value_vars=score_columns, 
                                        var_name='item', value_name='result')

# Extract the actual item name from the column names
df_melted_response['item'] = df_melted_response['item'].str.replace('-RESPONSE', '')
df_melted_score['item'] = df_melted_score['item'].str.replace('-SCORE', '')

# Sort the melted DataFrame by the 'row' column to keep the data for each participant closer
df_melted_response = df_melted_response.sort_values(by=['row','item'])
df_melted_score = df_melted_score.sort_values(by=['row','item'])

# Display the first few rows of the transformed DataFrame
display(df_melted_response[:3])
display(df_melted_score[:3])

# Merge the melted RESPONSE and SCORE DataFrames on 'row' and 'item'
df_final = df_melted_response.merge(df_melted_score, on=['row', 'item'], suffixes=('_response', '_score'))

# Rename the columns for clarity
df_final = df_final.rename(columns={'result_response': 'result', 'result_score': 'score'})

# Display the first few rows of the final merged DataFrame
df_final.head(20)

# %%
################################################################################
# Create a pivot table to summarize the scores
# Used to compare with Excel pivot table from SQL processed data as verification
################################################################################
pivot_table = df_final.pivot_table(values='row', index='item', columns='score', aggfunc='count', fill_value=0)

# Plot the pivot table with lighter colors and numbers on the bars
ax = pivot_table.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='Pastel1')
plt.title('Summary of Scores by Item')
plt.xlabel('Item')
plt.ylabel('Count of Scores')
plt.legend(title='Score')
plt.grid(axis='y', alpha=0.75)

# Add numbers on the bars
for container in ax.containers:
    ax.bar_label(container, label_type='center')

plt.tight_layout()
plt.show()


# %%

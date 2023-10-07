import pandas as pd
import numpy as np
import streamlit as st
import time
import re
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from google.auth import default
from collections import defaultdict

st.title("Generate Risk Matrix")

def simulate_data_processing():
    # Simulating some data processing task
    time.sleep(3)
    return "Trace Matrix   successfully generated. [Click here to view](https://docs.google.com/spreadsheets/d/19ZW_Eq3ySx925glrnokXDLBvx69_A7sTP02f8-NuB4Q/edit#gid=28624861)"
user_input = st.text_input("Please Enter the uri of the application", " ")
option = st.selectbox("Select an option:", ["Risk Analysis", "URS"])
grant_access = st.checkbox("Grant edit access to services@cloudkarya.com")

match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", user_input)
if match:
    FILE_ID = match.group(1)
    print(FILE_ID)
else:
    print("Invalid Google Sheets URL")

#FILE_ID="19ZW_Eq3ySx925glrnokXDLBvx69_A7sTP02f8-NuB4Q"
print(FILE_ID)
credentials = ServiceAccountCredentials.from_json_keyfile_name('/workspace/Demo/red-studio-400805-60aea2585639.json', ['https://www.googleapis.com/auth/spreadsheets'])




def execute_RiskAnalysis():
    global df  # Assuming df is a global variable containing the DataFrame
    global new_df  # Assuming new_df is a global variable
    global ijno_names  # Assuming ijno_names is a global variable
    global credentials
      
    gc = gspread.authorize(credentials)

    sht1 = gc.open_by_key(FILE_ID)
    worksheet = sht1.worksheet('Master')
    data = worksheet.get_all_values()
    #<========================TM 1Step RA===============================>

    # Extract headers and ensure uniqueness
    headers = data[0]
    seen_headers = set()
    for i in range(len(headers)):
        header = headers[i]
        if header in seen_headers:
            headers[i] = f"{header}_{i}"
        seen_headers.add(header)

    # Extract relevant columns
    selected_columns = ['I', 'J', 'N', 'O']
    ijno_names = [headers[ord(i) - 65] for i in selected_columns]

    # Prepare lists to create DataFrame
    controls_list = []
    function_list = []
    urs_ra_list = []
    urs_num_list = []
    ra_num_list = []
    name_list = []
    iq_list = []
    oq_list = []
    pq_list = []
    sop_list = []

    # Iterate through the data
    for i in range(1, len(data)):
        row = data[i]
        for column, value in zip(headers, row):
            if column in ijno_names:
                oq_value, iq_value, pq_value, sop_value = ' ', ' ', ' ', ' '
                if value.startswith('OQ'):
                    oq_value = 'x'
                elif value.startswith('IQ'):
                    iq_value = 'x'
                elif value.startswith('PQ'):
                    pq_value = 'x'
                elif value.startswith('SOP'):
                    sop_value = 'x'

                # Append values to respective lists
                controls_list.append(value)
                function_list.append(row[headers.index('Function of field unit')])
                urs_ra_list.append(value + " " + row[headers.index('Function of field unit')])
                urs_num_list.append(' ')
                ra_num_list.append(row[headers.index('Row ID#')])
                name_list.append(' ')
                iq_list.append(iq_value)
                oq_list.append(oq_value)
                pq_list.append(pq_value)
                sop_list.append(sop_value)

    # Create the new DataFrame
    new_df = pd.DataFrame({
        'Controls': controls_list,
        'Function of Field Unit': function_list,
        'Requirement from URS or RA': urs_ra_list,
        'URS Num': urs_num_list,
        'RA Num': ra_num_list,
        'Name of document': name_list,
        'IQ': iq_list,
        'OQ': oq_list,
        'PQ': pq_list,
        'SOP': sop_list
    })

    credentials = ServiceAccountCredentials.from_json_keyfile_name('/workspace/Demo/red-studio-400805-60aea2585639.json', ['https://www.googleapis.com/auth/spreadsheets'])
    gc = gspread.authorize(credentials)

    # Access the Google Sheets
    sheet_url = "https://docs.google.com/spreadsheets/d/19ZW_Eq3ySx925glrnokXDLBvx69_A7sTP02f8-NuB4Q"
    sh = gc.open_by_url(sheet_url)
    worksheet_name = 'TM 1Step RA'
    worksheet = None
    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet is not found, create it
        worksheet = sh.add_worksheet(title=worksheet_name, rows=1, cols=len(new_df.columns))
    else:
        # If the worksheet exists, clear its content
        worksheet.clear()
    worksheet.update('A1', [new_df.columns.values.tolist()])  # Update header

    
    worksheet.append_rows(new_df.values.tolist())

    worksheet = sht1.worksheet('TM 1Step RA')
    df_step1 = worksheet.get_all_values()
    #<========================TM 2Step RA===============================>
    cols_step2 = ["Requirement from URS or RA", "URS Num", "RA Num", "Name of document", "IQ", "OQ", "PQ", "SOP"]
    # Extract headers and ensure uniqueness
    headers = df_step1[0]
    seen_headers = set()
    for i in range(len(headers)):
        header = headers[i]
        if header in seen_headers:
            headers[i] = f"{header}_{i}"
        seen_headers.add(header)

    # Create a DataFrame using the remaining rows as data and with the extracted headers
    df_step1 = pd.DataFrame(df_step1[1:], columns=headers)

    # Keep only the required columns
    new_df_step2 = df_step1[cols_step2]
    
    # Filter out rows where "Requirement from URS or RA" contains 'none'
    new_df_step2 = df_step1[~df_step1['Requirement from URS or RA'].str.contains('none')]

    # Keep only the required columns
    new_df_step2 = new_df_step2[cols_step2]

    # Update the Google Sheets for the second sheet
    worksheet_step2_name = 'TM 2Step RA'
    worksheet_step2 = None

    try:
        # Try to access the worksheet, if it exists
        worksheet_step2 = sh.worksheet(worksheet_step2_name)
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet is not found, create it
        worksheet_step2 = sh.add_worksheet(title=worksheet_step2_name, rows=1, cols=len(new_df_step2.columns))
    else:
    # If the worksheet exists, clear its content
        worksheet_step2.clear()
    # Update header
    worksheet_step2.update('A1', [new_df_step2.columns.values.tolist()])

    # Append data
    worksheet_step2.append_rows(new_df_step2.values.tolist())

    #<========================TM 3Step RA===============================>
    cols_step3 = "Requirement from URS or RA,URS Num,RA Num,Name of document,IQ,OQ,PQ,SOP".split(',')

    # Fetch data from TM 2Step RA worksheet
    worksheet_step3 = sht1.worksheet('TM 2Step RA')
    df_step3 = pd.DataFrame(worksheet_step3.get_all_records())

    # Group RA Num based on Requirement from URS or RA
    new_df_step3_rano = df_step3.groupby('Requirement from URS or RA')['RA Num'].agg(list).reset_index()['RA Num']

    # Get unique Requirement from URS or RA values
    new_df_step3_req = list(set(df_step3['Requirement from URS or RA']))

    # Prepare a list of dictionaries for the new DataFrame
    new_data_step3 = []

    # Iterate through the data
    for i in range(len(new_df_step3_req)):
        new_row = {
            'Requirement from URS or RA': new_df_step3_req[i],
            'URS Num': ' ',
            'RA Num': str(new_df_step3_rano[i])[1:-1],
            'Name of document': ' ',
            'IQ': df_step3.iloc[i]['IQ'],
            'OQ': df_step3.iloc[i]['OQ'],
            'PQ': df_step3.iloc[i]['PQ'],
            'SOP': df_step3.iloc[i]['SOP']
        }
        new_data_step3.append(new_row)

    # Create the new DataFrame
    new_df_step3 = pd.DataFrame(new_data_step3, columns=cols_step3)
    # Create a new worksheet 'TM 3Step RA' and update header
    worksheet_step3_name = 'TM 3Step RA'
    worksheet_step3 = None

    try:
        # Try to access the worksheet, if it exists
        worksheet_step3 = sht1.add_worksheet(title=worksheet_step3_name, rows=1, cols=len(cols_step3))
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet is not found, create it
        worksheet_step3 = sht1.add_worksheet(title=worksheet_step3_name, rows=1, cols=len(cols_step3))
    else:
    # If the worksheet exists, clear its content
        worksheet_step3.clear()
    # Update header
    worksheet_step3.update('A1', [cols_step3])

    # Append data
    worksheet_step3.append_rows(new_df_step3.values.tolist())
    #<========================TM 4Step RA===============================>


    cols_step4 = "Requirement from URS or RA,URS Num,RA Num,Name of document,IQ,OQ,PQ,SOP".split(',')
    worksheet_step4_name = 'TM 4Step RA'
    
    # Fetch data from TM 3Step RA worksheet
    worksheet_step3 = sht1.worksheet('TM 3Step RA')
    df_step3 = pd.DataFrame(worksheet_step3.get_all_records())

    # Initialize a defaultdict to store RA Num for each Requirement from URS or RA
    new_df_step4_rano_dict = defaultdict(set)

    # Map Requirement from URS or RA to corresponding RA Num
    keywords_mapping = {
        'alarm Test': 'OQ alarm Test: all sensors',
        'calibration Sensor': 'OQ calibration-all sensors',
        'test Sensor of the centuring frame': 'OQ functional test-Sensor of the centuring frame',
        'test Sensor CONVEYOR TUB PRESENCE': 'OQ functional test-Sensor CONVEYOR TUB PRESENCE'
    }

    # Iterate through the data and map keywords to corresponding RA Num
    for i in range(len(df_step3['Requirement from URS or RA'])):
        for keyword, mapped_keyword in keywords_mapping.items():
            if keyword in df_step3.iloc[i]['Requirement from URS or RA']:
                ra_nums = set(map(int, str(df_step3.iloc[i]['RA Num']).split(', ')))
                new_df_step4_rano_dict[mapped_keyword].update(ra_nums)

    # Create a new DataFrame for TM 4Step RA
    new_df_step4_rows = []
    for key, value in new_df_step4_rano_dict.items():
        row = [key, ' ', str(value)[1:-1], key, ' ', ' ', ' ', ' ']
        new_df_step4_rows.append(row)

    # Create the new DataFrame
    new_df_step4 = pd.DataFrame(new_df_step4_rows, columns=cols_step4)

    # Update or create the worksheet 'TM 4Step RA'
    
    worksheet_step4 = None

    try:
        # Try to access the worksheet, if it exists
        worksheet_step4 = sh.worksheet(worksheet_step4_name)
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet is not found, create it
        worksheet_step4 = sh.add_worksheet(title=worksheet_step4_name, rows=1, cols=len(cols_step4))
    else:
        # If the worksheet exists, clear its content
        worksheet_step4.clear()

    # Update header and append data
    worksheet_step4.update([new_df_step4.columns.values.tolist()] + new_df_step4.values.tolist())
def execute_URS():
    global df  # Assuming df is a global variable containing the DataFrame
    global new_df  # Assuming new_df is a global variable
    global ijno_names  # Assuming ijno_names is a global variable
    global credentials
    gc = gspread.authorize(credentials)
    sht1 = gc.open_by_key(FILE_ID)
    worksheet = sht1.worksheet('Master')
    all_records = worksheet.get_all_records()
    #<========================20_URS_1===============================>

    cols = "Requirement Num,DI Control,GxP Critical,Requirement Description".split(',')
    headers = all_records[0].keys()  # Extract headers
    try:
        worksheet = sht1.worksheet('20_URS_1')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sht1.add_worksheet(title='20_URS_1', rows="100", cols="20")

    # Clear the worksheet
    worksheet.clear()
    df_step1 = pd.DataFrame(all_records)

    mask = df_step1['QP, BEA or ES'] == 'QP'
    filtered_df = df_step1.loc[mask, ['Requirement-ID \nClient', 'DI Control', 'QP, BEA or ES', 'Requirement Description']]
    filtered_df.columns = ['Requirement Num', 'DI Control', 'GxP Critical', 'Requirement Description']

    # Create a new DataFrame and reset the index
    new_df_step1 = pd.DataFrame(filtered_df)
    new_df_step1.reset_index(drop=True, inplace=True)

    # Fill NaN values with empty strings
    new_df_step1.fillna('', inplace=True)

    # Assuming cols is a list of columns to keep
    if cols:
        new_df_step1 = new_df_step1[cols]

    # Update the Google Sheets worksheet
    worksheet = sht1.worksheet('20_URS_1')
    worksheet.update([new_df_step1.columns.values.tolist()] + new_df_step1.values.tolist())






if st.button("Submit"):
    with st.spinner("Processing..."):
        # Perform data processing and update Google Sheets
        if option == "Risk Analysis":
            execute_RiskAnalysis()
        elif option == "URS":
            execute_URS()

        # Simulate some data processing task
        time.sleep(3)
        success_message = "Trace Matrix successfully generated. [Click here to view]( user_input )"

        st.success(success_message)



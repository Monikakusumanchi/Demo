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

st.title("Generate Risk Matrix")

def simulate_data_processing():
    # Simulating some data processing task
    time.sleep(3)
    return "Trace Matrix   successfully generated. [Click here to view](https://docs.google.com/spreadsheets/d/19ZW_Eq3ySx925glrnokXDLBvx69_A7sTP02f8-NuB4Q/edit#gid=28624861)"
user_input = st.text_input("Please Enter the uri of the application", " ")
option = st.selectbox("Select an option:", ["Risk Analysis", "URS"])
grant_access = st.checkbox("Grant edit access to services@cloudkarya.com")




def process_and_update_google_sheets():
    global df  # Assuming df is a global variable containing the DataFrame
    global new_df  # Assuming new_df is a global variable
    global ijno_names  # Assuming ijno_names is a global variable
    
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", user_input)
    if match:
        FILE_ID = match.group(1)
        print(FILE_ID)
    else:
        print("Invalid Google Sheets URL")
   
    #FILE_ID="19ZW_Eq3ySx925glrnokXDLBvx69_A7sTP02f8-NuB4Q"
    print(FILE_ID)
    credentials = ServiceAccountCredentials.from_json_keyfile_name('/workspace/Demo/red-studio-400805-60aea2585639.json', ['https://www.googleapis.com/auth/spreadsheets'])

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
    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet is not found, create it
        worksheet = sh.add_worksheet(title=worksheet_name, rows=1, cols=1)
        worksheet.update('A1', new_df.columns.values.tolist())  # Update header
    else:
        # If the worksheet exists, clear its content
        worksheet.clear()

    # Update the Google Sheets
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
    sh_step2 = gc.open_by_url(sheet_url)
    worksheet_step2 = sh_step2.worksheet('TM 2Step RA')

    try:
        # Attempt to clear the worksheet's content
        worksheet_step2.clear()
    except gspread.exceptions.APIError:
        # Handle API error (might occur if the worksheet is not found)
        pass

    # Update the Google Sheets for the second sheet
    worksheet_step2.update([new_df_step2.columns.values.tolist()] + new_df_step2.values.tolist())

if st.button("Submit"):
    with st.spinner("Processing..."):
        # Perform data processing and update Google Sheets
        process_and_update_google_sheets()

        # Simulate some data processing task
        time.sleep(3)
        success_message = "Trace Matrix successfully generated. [Click here to view]( user_input )"
        st.success(success_message)



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
    headers = data[0]

    # Ensure headers are unique, if not, rename duplicates
    seen_headers = set()
    for i in range(len(headers)):
        header = headers[i]
        if header in seen_headers:
            headers[i] = f"{header}_{i}"
        seen_headers.add(header)

    # Create DataFrame
    df = pd.DataFrame(data[1:], columns=headers)
    
    selected_columns = ['I', 'J', 'N', 'O']
    ijno_names = [df.columns[ord(i)-65] for i in selected_columns]
    cols = "Controls,Function of Field Unit,Requirement from URS or RA,URS Num,RA Num,Name of document,IQ,OQ,PQ,SOP".split(",")
    new_df = pd.DataFrame(columns=cols)
    for i in range(len(df)):
        for column, value in df.iloc[i].items():
            if column in ijno_names:
                oq_value, iq_value, pq_value, sop_value = ' ',' ',' ',' '
                if value.startswith('OQ'):
                    oq_value = 'x'
                elif value.startswith('IQ'):
                    iq_value = 'x'
                elif value.startswith('PQ'):
                    pq_value = 'x'
                elif value.startswith('SOP'):
                    sop_value = 'x'
                new_row = {
                    'Controls': value,
                    'Function of Field Unit': df.iloc[i]['Function of field unit'],
                    'Requirement from URS or RA': value + " " + df.iloc[i]['Function of field unit'],
                    'URS Num': ' ',
                    'RA Num': df.iloc[i]['Row ID#'],
                    'Name of document': ' ',
                    'IQ': iq_value,
                    'OQ': oq_value,
                    'PQ': pq_value,
                    'SOP': sop_value
                }

                new_df = pd.concat([new_df, pd.DataFrame([new_row])], ignore_index=True)
            credentials = ServiceAccountCredentials.from_json_keyfile_name('/workspace/Demo/red-studio-400805-60aea2585639.json', ['https://www.googleapis.com/auth/spreadsheets'])
            gc = gspread.authorize(credentials)

            # Access the Google Sheets
            sheet_url = "https://docs.google.com/spreadsheets/d/19ZW_Eq3ySx925glrnokXDLBvx69_A7sTP02f8-NuB4Q"
            sh = gc.open_by_url(sheet_url)
            worksheet = sh.worksheet('TM 1Step RA')

            # Update the Google Sheets
            worksheet.update([new_df.columns.values.tolist()] + new_df.values.tolist())
if st.button("Submit"):
    with st.spinner("Processing..."):
        # Perform data processing and update Google Sheets
        process_and_update_google_sheets()

        # Simulate some data processing task
        time.sleep(3)
        success_message = "Trace Matrix successfully generated. [Click here to view]( user_input )"
        st.success(success_message)



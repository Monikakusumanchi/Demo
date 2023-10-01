import pandas as pd
import numpy as np
import streamlit as st
import time
st.title("Upload Here to Automate your data")

def simulate_data_processing():
    # Simulating some data processing task
    time.sleep(3)
    return "Data successfully submitted!"
user_input = st.text_input("Please Enter the uri of the application", " ")
option = st.selectbox("Select an option:", ["Risk Analysis", "URL's", "Option 3"])
st.write("Please give edit access to services at CloudKarya ")
if st.button("Submit"):
        with st.spinner("Processing..."):
            success_message = simulate_data_processing()
            st.success(success_message)

# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import csv
from scoring import initialize_and_score

st.set_page_config(page_title="Scoring Page", page_icon="🚀")

# Path to the CSV file for persistent storage
HISTORY_CSV = 'address_history.csv'

def save_history(address, score):
    """Save a new entry to the CSV file."""
    with open(HISTORY_CSV, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['address', 'score'])
        if file.tell() == 0:
            writer.writeheader()  # File is empty, write header
        writer.writerow({'address': address, 'score': score})

def run():
    
    # Load history data from CSV
    #history_data = load_history()

    # Main app layout
    #main_col, history_col = st.columns([3, 1])

    #with main_col:
    st.write("# Address Scoring Optimized 🚀")
    address = st.text_input("Enter Address", "")

    if st.button("Check Scoring"):
        with st.spinner('Calculating score...'):
            score, messages = initialize_and_score(address)
            # Save the new address and score to the history CSV
            save_history(address, score)
            # Update the in-memory history data
            #history_data.append({'address': address, 'score': score})
            for message in messages:
                st.text(message)  # Display each message
            st.markdown(f"### Score: {score}")

    # with history_col:
    #     st.write("## History")
    #     # Display the history from in-memory data
    #     for item in reversed(history_data):
    #         st.text(f"Address: {item['address']}\nScore: {item['score']}")

if __name__ == "__main__":
    run()

# pages/history.py
import streamlit as st
import csv

# Function to load history from a CSV file
def load_history():
    history_data = []
    try:
        with open('address_history.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            history_data = [row for row in reader]
    except FileNotFoundError:
        st.error("History file not found.")
    return history_data

def app():
    st.title('Address Check History')

    history_data = load_history()

    # Display the history
    for item in history_data:
        st.text(f"Address: {item['address']} \n Score: {item['score']}")

# This condition ensures the app function runs only when this file is executed directly
if __name__ == "__main__":
    app()

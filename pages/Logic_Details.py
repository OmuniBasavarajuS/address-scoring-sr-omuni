import streamlit as st

def app():
    st.title("Logic Details")

    st.write("""
        Details about the scoring logic:
        - Special characters count towards the score.
        - High priority words have more weight.
        - Presence of city and pincode is checked.
        - Additional checks for consistency.
    """)

# Call the app function if this is the main script being run
if __name__ == "__main__":
    app()

import streamlit as st
import pandas as pd


st.set_page_config(page_title='Sport', 
                   layout="wide",
                   page_icon="💪")

def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    """

    # Side bar
    database_loaded = None
    with st.sidebar:
        uploaded_file = st.file_uploader(label="Base de données", type=".csv")
        if uploaded_file is not None:
            database_loaded = pd.read_csv(uploaded_file)

    if database_loaded is not None:
        st.dataframe(database_loaded, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()


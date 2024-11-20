import datetime

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu


st.set_page_config(page_title='Sport', 
                   layout="wide",
                   page_icon="💪")

def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    """
    # Tabs and side bar
    if 'tabs' not in st.session_state:
        st.session_state.tabs = ['Base de données']
        st.session_state.icons = ['arrow-bar-up']
        
    with st.sidebar:
        tab_selected = option_menu("Pages", options=st.session_state.tabs, icons=st.session_state.icons, menu_icon="bookmark")
    
    if tab_selected == 'Base de données':
        # Upload database
        file_uploaded = st.file_uploader(label="Base de données", type=".csv")
        if file_uploaded is not None:
            # Read .csv file
            df = pd.read_csv(file_uploaded)

            # Format date column
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True).dt.date
            
            # Hide this tab and display the others
            st.session_state.tabs = ['Visualiser', 'Nouvel exercice']
            st.session_state.icons = ['eye', 'database-add']
            st.session_state.df = df
            st.rerun()

    if tab_selected == 'Visualiser':
        col_category, col_exercise = st.columns(2)
        with col_category:
            # Select a category
            categories = ['Tout'] + st.session_state.df['Catégorie'].unique().tolist()
            selected_category = st.selectbox("Choix de la catégorie", options=categories)

        with col_exercise:
            # Select an exercise
            exercise_container = st.empty()
            if selected_category=='Tout':
                selected_exercice = 'Tout'
            
            else:
                exercices = ['Tout'] + st.session_state.df[st.session_state.df['Catégorie']==selected_category]['Name'].unique().tolist()
                selected_exercice = exercise_container.selectbox("Choix de l'exercice", options=exercices)

        # Filter the dataframe. If "Tout" is selected for either category or subcategory, show all data of the given filter
        if selected_category == "Tout":
            df = st.session_state.df.copy()
        elif selected_exercice == "Tout":
            df = st.session_state.df[st.session_state.df['Catégorie'] == selected_category].copy()
        else:
            df = st.session_state.df[(st.session_state.df['Catégorie'] == selected_category) & (st.session_state.df['Name'] == selected_exercice)].copy()

        # Display
        df.sort_values(by='Date', ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)

    if tab_selected == 'Nouvel exercice':
        col_date, col_category, col_exercise = st.columns(3)
        with col_date:
            new_date = st.date_input('Date', value=datetime.datetime.today(), format="YYYY-MM-DD")
        with col_category:
            new_category = st.selectbox("Catégorie", options=st.session_state.df['Catégorie'].unique())
        with col_exercise:
            new_exercice = st.selectbox('Exercice', options=st.session_state.df[st.session_state.df['Catégorie']==new_category]['Name'].unique())

        col_serie, col_repetition, col_load = st.columns(3)
        with col_serie:
            new_serie = st.number_input('Séries', min_value=1, value=4)
        with col_repetition:
            new_repetition = st.number_input('Répétitions', min_value=1, value=10)
        with col_load:
            new_load = st.number_input('Charge (kg)', min_value=1)

        col_rest, col_difficulty, col_superset = st.columns(3)
        with col_rest:
            new_rest = st.number_input('Temps de repos', min_value=1, value=90)
        with col_difficulty:
            new_difficulty = st.number_input('Difficulté', min_value=1, max_value=5)
        with col_superset:
            today = pd.Timestamp.today().normalize().strftime('%d-%m-%Y')
            new_superset = st.selectbox('Superset', options=['Non'] + st.session_state.df[st.session_state.df['Date']==today]['Name'].unique().tolist())

        if st.button('Sauvegarder'):
            st.session_state.df.loc[len(st.session_state.df)] = [new_exercice, new_category, new_load, new_date, new_difficulty, None, None, new_rest, new_repetition, new_serie]
            st.session_state.df = st.session_state.df.sort_values(by='Date', ascending=False)

if __name__ == "__main__":
    main()


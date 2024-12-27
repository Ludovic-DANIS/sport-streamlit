import datetime
from io import BytesIO

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
        st.session_state.difficulties = ['', 'Augmenter', 'Garder', 'Baisser']
        
    with st.sidebar:
        tab_selected = option_menu("Pages", options=st.session_state.tabs, icons=st.session_state.icons, menu_icon="bookmark")
    
    if tab_selected == 'Base de données':
        # Load .xlsx
        file_uploaded = st.file_uploader(label="Base de données", type=".xlsx")
        if file_uploaded is not None:
            # Sheet workout
            df_workout = pd.read_excel(file_uploaded, sheet_name='Musculation', parse_dates=['Date'])
            df_workout['Date'] = df_workout['Date'].dt.date
            # df_workout[['Charge', 'Difficulté', 'Repos', 'Séries', 'Répétitions']] = df_workout[['Charge', 'Difficulté', 'Repos', 'Séries', 'Répétitions']].astype(int)
            st.session_state.df_workout = df_workout

            # Sheet cardio
            df_cardio = pd.read_excel(file_uploaded, sheet_name='Cardio', parse_dates=['Date'])
            df_cardio['Date'] = df_cardio['Date'].dt.date
            st.session_state.df_cardio = df_cardio

            # Sheet categories
            df_categories = pd.read_excel(file_uploaded, sheet_name='Catégories')
            st.session_state.df_categories = df_categories

            # Hide this tab and display the others
            st.session_state.tabs = ['Visualiser', 'Nouvel exercice', 'Télécharger']
            st.session_state.icons = ['eye', 'database-add', 'download']
            st.rerun()

    if tab_selected == 'Visualiser':
        col_category, col_exercise = st.columns(2)
        df_categories = st.session_state.df_categories.copy()

        # Select a category
        with col_category:
            selected_category = st.selectbox("Choix de la catégorie", options=['']+df_categories['Catégorie'].unique().tolist())

        # # Select an exercise
        # with col_exercise:
        #     exercise_container = st.empty()
        #     if selected_category != '':
        #         selected_exercise = exercise_container.selectbox("Choix de l'exercice", options=['']+df_categories.loc[df_categories['Catégorie']==selected_category, 'Exercice'].tolist())

        # Filter the dataframe. If "Tout" is selected for either category or subcategory, show all data of the given filter
        if selected_category != '':
            # Either cardio or workout
            df = st.session_state.df_cardio.copy() if selected_category=='Cardio' else st.session_state.df_workout.copy()
            
        #     # Filter
        #     if selected_exercise != '':
        #         df = df.loc[df['Exercice']==selected_exercise]
        #     else:
        #         df = df.loc[df['Exercice'].isin(df_categories.loc[df_categories['Catégorie']==selected_category, 'Exercice'].tolist())]

            # Sort and display
            df = df.sort_values(by='Date', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

    if tab_selected == 'Nouvel exercice':
        df_workout = st.session_state.df_workout.copy().sort_values(by='Date', ascending=False)
        df_cardio = st.session_state.df_cardio.copy().sort_values(by='Date', ascending=False)
        df_categories = st.session_state.df_categories

        with st.expander(label='Need to add a new exercise ?', expanded=False, icon='❓'):
            col_category, col_muscle, col_exercise = st.columns(3)
            with col_category:
                category = st.selectbox("Catégorie", options=['']+df_categories['Catégorie'].unique().tolist(), key='category_for_new_exercise')
            with col_muscle:
                if category != '':
                    muscle_to_add = st.selectbox("Muscle", options=['']+df_categories.loc[df_categories['Catégorie']==category, 'Muscle'].unique().tolist())         
            with col_exercise:
                if category != '':
                    exercise_to_add = st.text_input("Nom de l'exercice")
            
            if category != '':
                if st.button('Ajouter', icon='✅') and exercise_to_add != '':
                    df_categories.loc[len(df_categories)] = [exercise_to_add, category, muscle_to_add]
                    st.session_state.df_categories = df_categories.copy()

        col_date, col_category, col_exercise = st.columns(3)
        with col_date:
            new_date = st.date_input('Date', value=pd.Timestamp('today').normalize(), format="DD/MM/YYYY")
        with col_category:
            new_category = st.selectbox("Catégorie", options=['']+df_categories['Catégorie'].unique().tolist())
        with col_exercise:
            if new_category != '':
                new_exercise = st.selectbox('Exercice', options=['']+df_categories.loc[df_categories['Catégorie']==new_category, 'Exercice'].tolist())

        # Display last sessions
        if new_category and new_exercise:
            st.divider()
            df = df_cardio.copy() if new_category=='Cardio' else df_workout.copy()

            # Filter
            if new_exercise != '':
                df = df.loc[df['Exercice']==new_exercise]
            else:
                df = df.loc[df['Exercice'].isin(df_categories.loc[df_categories['Catégorie']==new_category, 'Exercice'].tolist())]

            df = df.sort_values(by='Date', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.divider()

            if new_category=='Cardio':
                # Display remaining attributes to fill
                col_duration, col_time, col_levels, col_difficulty = st.columns(4)
                with col_duration:
                    new_duration = st.number_input('Durée totale', min_value=5.)
                with col_time:
                    new_time = st.text_input('Temps', value='[]')
                with col_levels:
                    new_levels = st.text_input('Niveaux', value='[]')
                with col_difficulty:
                    new_difficulty = st.selectbox('Difficulté', options=st.session_state.difficulties, index=0)
                
                if st.button('Sauvegarder'):
                    st.session_state.df_cardio.loc[len(st.session_state.df_cardio)] = [new_date, new_exercise, new_duration, new_difficulty, new_time, new_levels]

            else:
                if len(df) == 0:
                    serie_default = 4
                    repetition_default = 20 if new_category=='Jambes' else 10
                    load_default = None
                    rest_default = 90
                    difficulty_default = ''
                
                else:
                    serie_default = df.iloc[0]['Séries']
                    repetition_default = df.iloc[0]['Répétitions']
                    load_default = df.iloc[0]['Charge']
                    rest_default = df.iloc[0]['Repos']
                    difficulty_default = df.iloc[0]['Difficulté']

                # Display remaining attributes to fill
                col_serie, col_repetition, col_load = st.columns(3)
                with col_serie:
                    new_serie = st.number_input('Séries', min_value=1, value=serie_default)
                with col_repetition:
                    new_repetition = st.number_input('Répétitions', min_value=1, value=repetition_default)
                with col_load:
                    new_load = st.number_input('Charge (kg)', min_value=1, value=load_default)

                col_rest, col_difficulty, col_superset = st.columns(3)
                with col_rest:
                    new_rest = st.number_input('Temps de repos', min_value=1, value=rest_default)
                with col_difficulty:
                    new_difficulty = st.selectbox('Difficulté', options=st.session_state.difficulties, index=st.session_state.difficulties.index(difficulty_default))
                with col_superset:
                    new_superset = st.selectbox('Superset', options=['Non'] + df[df['Date'] == pd.Timestamp('today').normalize()]['Exercice'].unique().tolist())

                if st.button('Sauvegarder'):
                    st.session_state.df_workout.loc[len(st.session_state.df_workout)] = [new_date, new_exercise, new_load, new_difficulty, new_repetition, new_serie, new_rest]

    if tab_selected == 'Télécharger':
        excel_file_name = st.text_input('Nom du fichier .xlsx', value='musculation')

        # Function to convert DataFrames to Excel with multiple sheets
        @st.cache_data
        def convert_dfs_to_excel():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                st.session_state.df_workout.to_excel(writer, sheet_name='Musculation', index=False)
                st.session_state.df_cardio.to_excel(writer, sheet_name='Cardio', index=False)
                st.session_state.df_categories.to_excel(writer, sheet_name='Catégories', index=False)
            return output.getvalue()

        # Create a download button
        st.download_button(
            label="Télécharger",
            data=convert_dfs_to_excel(),
            file_name=f'{excel_file_name}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main()

# with st.expander("Ajouter un exercice"):
#     category = st.selectbox('catégorie', options=Session.CATEGORIES)
#     match category:
#         case "Dos":
#             session = Session(exercise=None, date=datetime.datetime.today(), category=category, load=10, serie=4, repetition=10, difficulty=None, rest=90, duration=None)
#         case "Epaules":
#             session = Session(exercise=None, date=datetime.datetime.today(), category=category, load=20, serie=4, repetition=10, difficulty=None, rest=90, duration=None)
#         case _ :
#             session = Session(exercise=None, date=datetime.datetime.today(), category=None, load=None, serie=None, repetition=None, difficulty=None, rest=None, duration=None)

#     with st.form('Nouvelle séance'):
#         col_exercise, col_date = st.columns(2)
#         with col_exercise:
#             exercise = st.text_input('Exercice', value=session.exercise)
#         with col_date:
#             date = st.date_input('Date', value=session.date)

#         col_load, col_serie, col_repetition, col_rest = st.columns(4)
#         with col_load:
#             load = st.number_input('Charge (kg)', min_value=1, value=session.load)
#         with col_serie:
#             serie = st.number_input('Séries)', min_value=1, value=session.serie)
#         with col_repetition:
#             repetition = st.number_input('Répétitions', min_value=1, value=session.repetition)
#         with col_rest:
#             rest= st.number_input('Temps de repos',min_value=1, value=session.rest)
        
#         duration = None
#         difficulty = st.slider('Difficulté', min_value=1, max_value=5, value=session.difficulty)

#         done = st.form_submit_button('Enregistrer')
#         if done:
#             session = Session(exercise, date, category, load, serie, repetition, difficulty, rest, duration)
#             excel_sessions.loc[len(excel_sessions)] = session.to_list

# st.divider()

# with st.expander('Base de donnée', expanded=True):
#     if excel_sessions is not None:
#         st.data_editor(excel_sessions, num_rows='dynamic', use_container_width=True, key='test')

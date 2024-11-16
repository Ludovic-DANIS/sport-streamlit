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
    df = None
    with st.sidebar:
        uploaded_file = st.file_uploader(label="Base de données", type=".csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            # Format date column
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
            df = df.sort_values(by='Date', ascending=False)
            df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')

    if df is not None:
        col_category, col_exercise = st.columns(2)
        with col_category:
            # Select a category
            categories = ['Tout'] + df['Catégorie'].unique().tolist()
            selected_category = st.selectbox("Choix de la catégorie", options=categories)

        with col_exercise:
            # Select an exercise
            exercise_container = st.empty()
            if selected_category=='Tout':
                selected_exercice = 'Tout'
            
            else:
                exercices = ['Tout'] + df[df['Catégorie']==selected_category]['Name'].unique().tolist()
                selected_exercice = exercise_container.selectbox("Choix de l'exercice", options=exercices)

        # Filter the dataframe. If "Tout" is selected for either category or subcategory, show all data of the given filter
        if selected_category == "Tout":
            filtered_df = df
        elif selected_exercice == "Tout":
            filtered_df = df[df['Catégorie'] == selected_category]
        else:
            filtered_df = df[(df['Catégorie'] == selected_category) & (df['Name'] == selected_exercice)]

        # Display
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()


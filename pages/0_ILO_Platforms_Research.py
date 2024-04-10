import streamlit as st
import pandas as pd
# import altair as alt
from folium.plugins import MarkerCluster
import pydeck as pdk
import plotly.express as px
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st.set_page_config(layout="wide")

data = pd.read_csv('./platforms-dataset.csv')

st.title('ILO digital labor platforms research')


st.subheader(" Map ")
st.markdown("""
        <iframe width="900" height="675" src="https://lookerstudio.google.com/embed/reporting/ee7fd553-6dc1-403b-8098-896e11ba26bf/page/p_xtl87dg7fd" frameborder="0" style="border:0" allowfullscreen sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
    """, unsafe_allow_html=True)


st.subheader('platforms started per year')
aggregated_data = data.groupby('Start').size()
st.bar_chart(aggregated_data, color='#3F8BD7')

# types of platforms started per year
st.subheader('types of platform started per year')
platform_types_data = data.groupby(['Start', 'Type (ILO)']).size().unstack()
st.bar_chart(platform_types_data, color=['#10A9B8', '#FFFF00', '#FF6341'])

def continent_chart():
    data = pd.read_csv('./platforms-dataset.csv')
    df = data.set_index("Continent")
    unique_continents = df.index.unique().tolist()
    selected_continents = st.multiselect("Choose continents", unique_continents, ["Africa", "Asia"])
    if not selected_continents:
        st.error("Please select at least one continent.")
    else:
        filtered_data = data[data['Continent'].isin(selected_continents)].groupby(['Start', 'Type (ILO)']).size().unstack()
        st.bar_chart(filtered_data, color=['#10A9B8', '#FFFF00', '#FF6341'])

# =================================================================================== #
# @st.cache_data
st.subheader('type of platform started per year per continent')

continent_chart()


st.subheader('Typology')
# Group by 'Typology' and 'Start', then count the occurrences
# counts = data.groupby(['Typology', 'Start']).size().reset_index(name='Count')

# # Display the new DataFrame
# st.dataframe(counts)

typology_df = data.pivot_table(index='Typology', columns='Start', aggfunc='size', fill_value=0)
typology_df.reset_index(inplace=True)
typology_df.drop_duplicates(subset='Typology', keep='first', inplace=True)
filtered_typology_df = typology_df[typology_df['Typology'].isin(['Online contracting intermediaries', 'Online marketplace with a threshold', 'Online marketplace', 'Situ intermediaries', 'Situ marketplace with a threshold', 'Situ marketplace'])]
sector_df = data.pivot_table(index='Sector (ILO definitions)', columns='Start', aggfunc='size', fill_value=0)
sector_df.reset_index(inplace=True)
sector_df.drop_duplicates(subset='Sector (ILO definitions)', keep='first', inplace=True)


sub_category_df = data.pivot_table(index='Sub-category', columns='Start', aggfunc='size', fill_value=0)
sub_category_df.reset_index(inplace=True)
sub_category_df.drop_duplicates(subset='Sub-category', keep='first', inplace=True)



def bubble_chart(pivot_df, main_column):
    # Assuming pivot_df is your pivoted DataFrame
    # Convert the DataFrame to a long format suitable for Plotly Express
    long_df = pivot_df.melt(id_vars=main_column, var_name='Year', value_name='Count')

    # Convert the 'Year' column to a numerical format suitable for a scatter plot
    # Handle non-numeric values by converting them to NaN
    long_df['Year'] = pd.to_numeric(long_df['Year'], errors='coerce')

    # Optionally, handle NaN values (e.g., by filling them with a default value or dropping rows)
    # Here, we're dropping rows with NaN values in the 'Year' column
    long_df.dropna(subset=['Year'], inplace=True)

    # Create the scatter plot
    fig = px.scatter(long_df, x='Year', y='Count', size='Count', color=main_column,
                     hover_name=main_column, log_x=True, size_max=50,)


    st.plotly_chart(fig, theme=None)

bubble_chart(filtered_typology_df, 'Typology')

bubble_chart(sector_df, 'Sector (ILO definitions)')
bubble_chart(sub_category_df, 'Sub-category')

counts = data.groupby(['Skill level (professional)', 'Matching method']).size().reset_index(name='Count')

# Create a bar chart to visualize the counts
fig = px.bar(counts, x='Skill level (professional)', y='Count', color='Matching method',
                title='Matching Method by Professional Skill Level',
                labels={'Count': 'Number of Occurrences'})

# Display the bar chart in the Streamlit app
st.plotly_chart(fig)



counts = data.groupby(['Skill level (digital)', 'Matching method']).size().reset_index(name='Count')

# Create a bar chart to visualize the counts
fig = px.bar(counts, x='Skill level (digital)', y='Count', color='Matching method',
                title='Matching Method by Digital Skill Level',
                labels={'Count': 'Number of Occurrences'})

# Display the bar chart in the Streamlit app
st.plotly_chart(fig)

# def bubble_chart():
#     counts = data['Typology'].value_counts().reset_index()
#     counts.columns = ['Typology', 'count', 'Start']

#     # Generate the scatter plot using the counts DataFrame
#     fig = px.scatter(counts, x='Start', y='count',
#                      size='count', color='Typology', hover_name='Typology', log_x=True, size_max=60)


#     # row_count = len(data)

#     # # Generate the scatter plot using the row count as the size parameter
#     # fig = px.scatter(data, x="Start", y=row_count,
#     #                  size=row_count, color="Type (ILO)",
#     #                  hover_name="Typology", log_x=True, size_max=60)

#     tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
#     with tab1:
#         st.plotly_chart(fig, theme="streamlit")
#     with tab2:
#         st.plotly_chart(fig, theme=None)

# bubble_chart()
# def get_chart():
#     # Load your CSV data into a DataFrame
#     # Replace 'your_data.csv' with the path to your CSV file

#     # Calculate the count of rows in the DataFrame
#     row_count = len(data)

#     # Generate the scatter plot using the DataFrame
#     # Adjust the parameters according to your requirements
#     fig = px.scatter(data, x="Start", y=6, # Use a constant value for y
#                     size=row_count, color="Type (ILO)",
#                     hover_name="Typology", log_x=True, size_max=60)

#     tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
#     with tab1:
#         st.plotly_chart(fig, theme="streamlit")
#     with tab2:
#         st.plotly_chart(fig, theme=None)

# # Call the function to display the chart
# get_chart()



# df = data.reset_index()
# # Calculate counts
# typology_counts = df['Typology'].value_counts()
# # Create a DataFrame with the counts
# typology_counts_df = typology_counts.reset_index()
# typology_counts_df.columns = ['Typology', 'Count']
# # Altair plot
# chart = alt.Chart(typology_counts_df).mark_bar().encode(
#     x='Count:Q',
#     y='Typology:N'  # Sort bars by frequency
# ).properties(
#     height=400,  # Adjust chart size
#     width=600
# )
# st.altair_chart(chart, use_container_width=True)
# st.subheader('Sector (ILO definitions)')
# # Calculate counts
# sector_counts = df['Sector (ILO definitions)'].value_counts()
# # Create a DataFrame with the counts
# sector_counts_df = sector_counts.reset_index()
# sector_counts_df.columns = ['Sector (ILO definitions)', 'Count']
# # Altair plot
# chart = alt.Chart(sector_counts_df).mark_bar().encode(
#     x='Count:Q',
#     y='Sector (ILO definitions):N'  # Sort bars by frequency
# ).properties(
#     height=400,  # Adjust chart size
#     width=600
# )


# st.altair_chart(chart, use_container_width=True)
# st.subheader('Sub-category')
# # Calculate counts
# category_counts = df['Sub-category'].value_counts()
# # Create a DataFrame with the counts
# category_counts_df = category_counts.reset_index()
# category_counts_df.columns = ['Sub-category', 'Count']
# # Altair plot
# chart = alt.Chart(category_counts_df).mark_bar().encode(
#     x='Count:Q',
#     y='Sub-category:N'  # Sort bars by frequency
# ).properties(
#     height=400,  # Adjust chart size
#     width=600
# )
# st.altair_chart(chart, use_container_width=True)
# col1, col2 , col3 = st.columns(3)
# col1.subheader('Type of work')
# # Calculate counts
# work_counts = df['Type of work'].value_counts()
# # Create a DataFrame with the counts
# work_counts_df = work_counts.reset_index()
# work_counts_df.columns = ['Type of work', 'Count']
# col1.dataframe(work_counts_df)
# col2.subheader('Size')
# # Calculate counts
# size_counts = df['Size'].value_counts()
# # Create a DataFrame with the counts
# size_counts_df = size_counts.reset_index()
# size_counts_df.columns = ['Size', 'Count']
# col2.dataframe(size_counts_df)
# col3.subheader('Worker provisions')
# # Calculate counts
# size_counts = df['Worker provisions'].value_counts()
# # Create a DataFrame with the counts
# size_counts_df = size_counts.reset_index()
# size_counts_df.columns = ['Worker provisions', 'Count']
# col3.dataframe(size_counts_df)
# # st.markdown('''
# #             ## Does more attacks mean more casualties ?
# #             #### Countries with Most Number of Attacks on Healthcare Facilities
# #             | Attacks : :large_yellow_circle:  |
# #             |-------------- |
# #             ''')
# container1 = col1.container(border=True)
# container1.subheader('Continent')
# # Create the pie chart
# chart = alt.Chart(data).mark_arc().encode(
#     theta=alt.Theta('count()', stack=True),
#     color=alt.Color('Continent:N', legend=alt.Legend(title="Continent")),
#     )
# # Display the chart
# container1.altair_chart(chart, theme="streamlit", use_container_width=True)
# # # @st.experimental_memo
# # level_counts = data['Level of operation'].value_counts()
# # # Creating the data source
# # source = pd.DataFrame(data)
# # # Creating the Altair chart
# # chart = alt.Chart(level_counts).mark_arc().encode(
# #     theta=alt.Theta(field="Level of operation", type="quantitative"),
# #     color=alt.Color(field="Level of operation", type="nominal"),
# # )
# # # Displaying the chart with the Streamlit theme
# # st.altair_chart(chart, theme="streamlit", use_container_width=True)
# # Read the CSV file into a DataFrame
# # data = pd.read_csv('./platforms-dataset.csv')
# container2 = col2.container(border=True)
# container2.subheader('Level of operation')
# # Create the pie chart
# chart = alt.Chart(data[data['Level of operation'].notnull()]).mark_arc().encode(
#     theta=alt.Theta('count()', stack=True),
#     color=alt.Color('Level of operation:N', legend=alt.Legend(title="Level of Operation")),
#     # tooltip=['Level of operation', alt.Tooltip('count()', title='Count')]
#     )
# # Display the chart
# container2.altair_chart(chart, theme="streamlit", use_container_width=True)
# container3 = col3.container(border=True)
# container3.subheader('Type (ILO)')
# # Create the pie chart
# chart = alt.Chart(data[data['Type (ILO)'].notnull()]).mark_arc().encode(
#     theta=alt.Theta('count()', stack=True),
#     color=alt.Color('Type (ILO):N', legend=alt.Legend(title="Type (ILO)")),
#     # tooltip=['Type (ILO)', alt.Tooltip('count()', title='Count')]
#     )
# # Display the chart
# container3.altair_chart(chart, theme="streamlit", use_container_width=True)
# container4 = col1.container(border=True)
# container4.subheader('Skill level (professional) ')
# # Create the pie chart
# chart = alt.Chart(data[(data['Skill level (professional)'].notnull()) & (data['Skill level (professional)'] != '-')]).mark_arc().encode(
#     theta=alt.Theta('count()', stack=True),
#     color=alt.Color('Skill level (professional):N', legend=alt.Legend(title="Skill level (professional)")),
#     )
# # Display the chart
# container4.altair_chart(chart, theme="streamlit", use_container_width=True)
# # Skill level (digital)
# container5 = col2.container(border=True)
# container5.subheader('Skill level (digital) ')
# # Create the pie chart
# chart = alt.Chart(data[(data['Skill level (digital)'].notnull()) & (data['Skill level (digital)'] != '-')]).mark_arc().encode(
#     theta=alt.Theta('count()', stack=True),
#     color=alt.Color('Skill level (digital):N', legend=alt.Legend(title="Skill level (digital)")),
#     )
# # Display the chart
# container5.altair_chart(chart, theme="streamlit", use_container_width=True)
# # Matching method
# container6 = col3.container(border=True)
# container6.subheader('Matching method ')
# # Create the pie chart
# chart = alt.Chart(data[(data['Matching method'].notnull()) & (data['Matching method'] != '-')]).mark_arc().encode(
#     theta=alt.Theta('count()', stack=True),
#     color=alt.Color('Matching method:N', legend=alt.Legend(title="Matching method")),
#     )
# # Display the chart
# container6.altair_chart(chart, theme="streamlit", use_container_width=True)
# # # Pie Chart With Labels
# # base = alt.Chart(data).encode(
# #     theta=alt.Theta("count()", stack=True), color=alt.Color("Continent:N", legend=None)
# # )
# # pie = base.mark_arc(outerRadius=140)
# # text = base.mark_text(radius=180, size=20).encode(text="Continent:N")
# # chart = pie + text
# # st.altair_chart(chart, theme="streamlit", use_container_width=True)
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
bubble_chart(typology_df, 'Typology')

bubble_chart(sector_df, 'Sector (ILO definitions)')
bubble_chart(sub_category_df, 'Sub-category')

data['Matching method'] = data['Matching method'].replace('-', 'Unknown', regex=True)

# Define the color mapping
color_map = {
    'Unknown': 'pink',
    # 'Algorithmic matching': 'red',
    'Free choice': 'blue',
    'Hand matching': 'lightblue'
}
# Assuming 'data' is your DataFrame
counts = data.groupby(['Skill level (digital)', 'Matching method']).size().reset_index(name='Count')

# Calculate the total count for each 'Skill level (digital)'
total_counts = data.groupby('Skill level (digital)').size().reset_index(name='Total Count')

# Merge the total counts with the original counts DataFrame
counts = counts.merge(total_counts, on='Skill level (digital)')

# Calculate the percentage for each 'Matching method' within each 'Skill level (digital)'
counts['Percentage'] = (counts['Count'] / counts['Total Count']) * 100

# Round the percentage to 1 decimal place
counts['Percentage'] = counts['Percentage'].round(1)

# Create a bar chart to visualize the counts
fig_counts = px.bar(counts, x='Skill level (digital)', y='Count', color='Matching method', text_auto=True,
                    title='Matching Method by Digital Skill Level',
                    labels={'Count': 'Number of Occurrences'},
                    color_discrete_map=color_map)

# Create a bar chart to visualize the rounded percentages
fig_percentage = px.bar(counts, x='Skill level (digital)', y='Percentage', color='Matching method', text_auto=True,
                        title='Matching Method by Digital Skill Level (Percentage)',
                        labels={'Percentage': 'Percentage of Occurrences'},
                        color_discrete_map=color_map)
fig_percentage.update_traces(textfont_size=16)
fig_counts.update_traces(textfont_size=16,)
# Create two tabs
tab1, tab2 = st.tabs(["Percentage of Occurrences", "Number of Occurrences"])

# Display the percentage chart in the first tab
with tab1:
    st.plotly_chart(fig_percentage, theme="streamlit")

# Display the count chart in the second tab
with tab2:
    st.plotly_chart(fig_counts, theme="streamlit")


# Assuming 'data' is your DataFrame
counts = data.groupby(['Skill level (professional)', 'Matching method']).size().reset_index(name='Count')

# Calculate the total count for each 'Skill level (professional)'
total_counts = data.groupby('Skill level (professional)').size().reset_index(name='Total Count')

# Merge the total counts with the original counts DataFrame
counts = counts.merge(total_counts, on='Skill level (professional)')

# Calculate the percentage for each 'Matching method' within each 'Skill level (professional)'
counts['Percentage'] = (counts['Count'] / counts['Total Count']) * 100

# Round the percentage to 1 decimal place
counts['Percentage'] = counts['Percentage'].round(1)

# Create a bar chart to visualize the counts
fig_counts = px.bar(counts, x='Skill level (professional)', y='Count', color='Matching method', text_auto=True,
                    title='Matching Method by Professional Skill Level',
                    labels={'Count': 'Number of Occurrences'},
                    color_discrete_map=color_map)

# Create a bar chart to visualize the rounded percentages
fig_percentage = px.bar(counts, x='Skill level (professional)', y='Percentage', color='Matching method', text_auto=True,
                        title='Matching Method by Professional Skill Level (Percentage)',
                        labels={'Percentage': 'Percentage of Occurrences'},
                    color_discrete_map=color_map)
fig_percentage.update_traces(textfont_size=16)
fig_counts.update_traces(textfont_size=16)


# Create two tabs
tab1, tab2 = st.tabs(["Percentage of Occurrences", "Number of Occurrences"])

# Display the percentage chart in the first tab
with tab1:
    st.plotly_chart(fig_percentage, theme="streamlit")

# Display the count chart in the second tab
with tab2:
    st.plotly_chart(fig_counts, theme="streamlit")


# # Assuming 'data' is your DataFrame
# data['Matching method'] = data['Matching method'].replace('-', 'Unknown', regex=True)

# # Define the color mapping
# color_map = {
#     'Unknown': 'pink',
#     'Algorithmic matching': 'red',
#     'Free choice': 'blue',
#     'Hand matching': 'lightblue'
# }

# # Group the data by 'Skill level (professional)' and 'Matching method', and count the occurrences
# counts_professional = data.groupby(['Skill level (professional)', 'Matching method']).size().reset_index(name='Count')

# # Calculate the total count for each 'Skill level (professional)'
# total_counts_professional = data.groupby('Skill level (professional)').size().reset_index(name='Total Count')

# # Merge the total counts with the original counts DataFrame
# counts_professional = counts_professional.merge(total_counts_professional, on='Skill level (professional)')

# # Calculate the percentage for each 'Matching method' within each 'Skill level (professional)'
# counts_professional['Percentage'] = (counts_professional['Count'] / counts_professional['Total Count']) * 100

# # Round the percentage to 1 decimal place
# counts_professional['Percentage'] = counts_professional['Percentage'].round(1)

# # Create a bar chart to visualize the counts for 'Skill level (professional)'
# fig_counts_professional = px.bar(counts_professional, x='Skill level (professional)', y='Count', color='Matching method', text_auto=True,
#                                 title='Matching Method by Professional Skill Level',
#                                 labels={'Count': 'Number of Occurrences'},
#                                 color_discrete_map=color_map)

# # Create a bar chart to visualize the rounded percentages for 'Skill level (professional)'
# fig_percentage_professional = px.bar(counts_professional, x='Skill level (professional)', y='Percentage', color='Matching method', text_auto=True,
#                                     title='Matching Method by Professional Skill Level (Percentage)',
#                                     labels={'Percentage': 'Percentage of Occurrences'},
#                                     color_discrete_map=color_map)

# # Repeat the above steps for 'Skill level (digital)'
# counts_digital = data.groupby(['Skill level (digital)', 'Matching method']).size().reset_index(name='Count')
# total_counts_digital = data.groupby('Skill level (digital)').size().reset_index(name='Total Count')
# counts_digital = counts_digital.merge(total_counts_digital, on='Skill level (digital)')
# counts_digital['Percentage'] = (counts_digital['Count'] / counts_digital['Total Count']) * 100
# counts_digital['Percentage'] = counts_digital['Percentage'].round(1)

# fig_counts_digital = px.bar(counts_digital, x='Skill level (digital)', y='Count', color='Matching method', text_auto=True,
#                            title='Matching Method by Digital Skill Level',
#                            labels={'Count': 'Number of Occurrences'},
#                            color_discrete_map=color_map)

# fig_percentage_digital = px.bar(counts_digital, x='Skill level (digital)', y='Percentage', color='Matching method', text_auto=True,
#                                title='Matching Method by Digital Skill Level (Percentage)',
#                                labels={'Percentage': 'Percentage of Occurrences'},
#                                color_discrete_map=color_map)

# # Display the charts in the Streamlit app
# st.plotly_chart(fig_counts_professional)
# st.plotly_chart(fig_percentage_professional)
# st.plotly_chart(fig_counts_digital)
# st.plotly_chart(fig_percentage_digital)


# # Assuming 'data' is your DataFrame
# data['Matching method'] = data['Matching method'].replace('-', 'Unknown', regex=True)

# # Define the color mapping
# color_map = {
#     'Algorithmic matching': 'red',
#     'Unknown': 'pink',
#     'Free choice': 'blue',
#     'Hand matching': 'lightblue'
# }

# # Group the data by 'Skill level (professional)' and 'Matching method', and count the occurrences
# counts = data.groupby(['Skill level (professional)', 'Matching method']).size().reset_index(name='Count')

# # Create a bar chart to visualize the counts
# fig = px.bar(counts, x='Skill level (professional)', y='Count', color='Matching method', text_auto=True,
#              title='Matching Method by Professional Skill Level',
#              labels={'Count': 'Number of Occurrences'},
#              color_discrete_map=color_map) # Apply the color mapping

# # Display the bar chart in the Streamlit app
# st.plotly_chart(fig)

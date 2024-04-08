
import pandas as pd
import pydeck as pdk
import streamlit as st
import altair as alt
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



data = pd.read_csv('./platforms-dataset.csv')

def mapping_demo():

    col1, col2 , col3 = st.columns(3)
    container1 = col1.container(border=True)
    container1.subheader('Continent')
    # Create the pie chart
    chart = alt.Chart(data).mark_arc().encode(
        theta=alt.Theta('count()', stack=True),
        color=alt.Color('Continent:N', legend=alt.Legend(title="Continent")),
        )
    # Display the chart
    container1.altair_chart(chart, theme="streamlit", use_container_width=True)
    # # @st.experimental_memo
    # level_counts = data['Level of operation'].value_counts()
    # # Creating the data source
    # source = pd.DataFrame(data)
    # # Creating the Altair chart
    # chart = alt.Chart(level_counts).mark_arc().encode(
    #     theta=alt.Theta(field="Level of operation", type="quantitative"),
    #     color=alt.Color(field="Level of operation", type="nominal"),
    # )
    # # Displaying the chart with the Streamlit theme
    # st.altair_chart(chart, theme="streamlit", use_container_width=True)
    # Read the CSV file into a DataFrame
    # data = pd.read_csv('./platforms-dataset.csv')
    container2 = col2.container(border=True)
    container2.subheader('Level of operation')
    # Create the pie chart
    chart = alt.Chart(data[data['Level of operation'].notnull()]).mark_arc().encode(
        theta=alt.Theta('count()', stack=True),
        color=alt.Color('Level of operation:N', legend=alt.Legend(title="Level of Operation")),
        # tooltip=['Level of operation', alt.Tooltip('count()', title='Count')]
        )
    # Display the chart
    container2.altair_chart(chart, theme="streamlit", use_container_width=True)
    container3 = col3.container(border=True)
    container3.subheader('Type (ILO)')
    # Create the pie chart
    chart = alt.Chart(data[data['Type (ILO)'].notnull()]).mark_arc().encode(
        theta=alt.Theta('count()', stack=True),
        color=alt.Color('Type (ILO):N', legend=alt.Legend(title="Type (ILO)")),
        # tooltip=['Type (ILO)', alt.Tooltip('count()', title='Count')]
        )
    # Display the chart
    container3.altair_chart(chart, theme="streamlit", use_container_width=True)
    container4 = col1.container(border=True)
    container4.subheader('Skill level (professional) ')
    # Create the pie chart
    chart = alt.Chart(data[(data['Skill level (professional)'].notnull()) & (data['Skill level (professional)'] != '-')]).mark_arc().encode(
        theta=alt.Theta('count()', stack=True),
        color=alt.Color('Skill level (professional):N', legend=alt.Legend(title="Skill level (professional)")),
        )
    # Display the chart
    container4.altair_chart(chart, theme="streamlit", use_container_width=True)
    # Skill level (digital)
    container5 = col2.container(border=True)
    container5.subheader('Skill level (digital) ')
    # Create the pie chart
    chart = alt.Chart(data[(data['Skill level (digital)'].notnull()) & (data['Skill level (digital)'] != '-')]).mark_arc().encode(
        theta=alt.Theta('count()', stack=True),
        color=alt.Color('Skill level (digital):N', legend=alt.Legend(title="Skill level (digital)")),
        )
    # Display the chart
    container5.altair_chart(chart, theme="streamlit", use_container_width=True)
    # Matching method
    container6 = col3.container(border=True)
    container6.subheader('Matching method ')
    # Create the pie chart
    chart = alt.Chart(data[(data['Matching method'].notnull()) & (data['Matching method'] != '-')]).mark_arc().encode(
        theta=alt.Theta('count()', stack=True),
        color=alt.Color('Matching method:N', legend=alt.Legend(title="Matching method")),
        )
    # Display the chart
    container6.altair_chart(chart, theme="streamlit", use_container_width=True)


st.set_page_config(page_title="Pie Charts", page_icon="🌍",layout="wide")
st.markdown("# Mapping Demo")
st.sidebar.header("Mapping Demo")
st.write()

mapping_demo()



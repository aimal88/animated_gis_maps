import streamlit as st
import wbdata
import pandas as pd
import plotly.express as px

# Set page config and add custom CSS for styling and spacing
st.set_page_config(page_title="Global Trends Explorer", layout="wide")
st.markdown("""
<style>
    .main {background-color: #f5f5f5; padding: 20px;}
    .section {padding: 20px 0px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# Sidebar: App Info, Options & Social Links
# -----------------------------------------
st.sidebar.header("**Welcome!**")

# About the app in an expander for a cleaner sidebar
with st.sidebar.expander("About this App"):
    st.markdown("""
    This web app visualizes global economic and demographic trends (1960–2023) using interactive maps.
    Explore the data with dynamic choropleth maps and line charts based on World Bank data.
    """)

# Sidebar options for map display
st.sidebar.markdown("### Map Options")
selected_map = st.sidebar.radio(
    "**Select Map to Display**", 
    ["GDP", "Total Population", "Net Migration"], 
    index=0
)

selected_projection = st.sidebar.selectbox(
    "Select Map Projection", 
    ["natural earth", "orthographic", "mercator", "equirectangular", "robinson", "mollweide"],
    index=0
)

selected_color_scale = st.sidebar.selectbox(
    "Select Color Scale", 
    ["Viridis", "Plasma", "Magma", "Cividis", "Inferno", "Turbo"],
    index=0
)

# Social Media Buttons
st.sidebar.markdown("### Connect with Me")
social_html = """
<div style="display: flex; justify-content: space-around; padding-top: 10px;">
    <a href="https://www.linkedin.com/in/aimal88" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="30">
    </a>
    <a href="https://www.kaggle.com/aimal8" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/Kaggle_logo.png" alt="Kaggle" width="30">
    </a>
    <a href="https://github.com/aimal88" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" alt="GitHub" width="30">
    </a>
    <a href="https://x.com/8_aimal" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/3670/3670151.png" alt="Twitter" width="30">
    </a>
</div>
"""
st.sidebar.markdown(social_html, unsafe_allow_html=True)

# -----------------------------------------
# Main Page: Title & Intro
# -----------------------------------------
st.title("Global Trends Explorer")
st.markdown("""
This interactive web app presents dynamic choropleth maps and line charts based on World Bank data.
<br><br>
Use the sidebar options to choose the map type, projection, and color scale.
""", unsafe_allow_html=True)

# Horizontal rule for separation
st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------------------
# Data Preparation
# -----------------------------------------
indicator = {
    'SP.POP.TOTL': 'total_population',   # Total Population
    'NY.GDP.PCAP.CD': 'gdp_per_capita',    # GDP per capita (Current US$)
    'SM.POP.NETM': 'net_migration'         # Net Migration
}

@st.cache_data
def load_data():
    data = wbdata.get_dataframe(indicator)
    data.reset_index(inplace=True)
    data.rename(columns={'country': 'Country', 'date': 'Year'}, inplace=True)
    data['Year'] = pd.to_numeric(data['Year'])
    df = data[(data['Year'] >= 1960) & (data['Year'] <= 2023)]
    df.sort_values(by="Year", ascending=True, inplace=True)
    return df

df = load_data()

# -----------------------------------------
# Function to Generate the Map
# -----------------------------------------
def create_map(map_type, df, projection, color_scale):
    if map_type == "GDP":
        fig = px.choropleth(
            df,
            animation_frame="Year",
            locations="Country",
            locationmode='country names',
            color="gdp_per_capita",
            hover_name="Country",
            color_continuous_scale=color_scale,
            title="GDP from 1960 to 2023",
            labels={'gdp_per_capita': 'GDP Per Capita US$'}
        )
    elif map_type == "Total Population":
        fig = px.choropleth(
            df,
            animation_frame="Year",
            locations="Country",
            locationmode='country names',
            color="total_population",
            hover_name="Country",
            color_continuous_scale=color_scale,
            title="Total Population from 1960 to 2023",
            labels={'total_population': 'Total Population'}
        )
    else:  # "Net Migration"
        fig = px.choropleth(
            df,
            animation_frame="Year",
            locations="Country",
            locationmode='country names',
            color="net_migration",
            hover_name="Country",
            color_continuous_scale=color_scale,
            title="Net Migration from 1960 to 2023",
            labels={'net_migration': 'Net Migration'}
        )

    fig.update_geos(projection_type=projection)
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font_color='black',
        title_font_size=18,
        font=dict(color='black', size=12),
        legend_title_font_color='black',
        legend_font_color='black',
        coloraxis_colorbar=dict(
            title_font_color='black',
            tickfont_color='black'
        )
    )
    return fig

# -----------------------------------------
# Display the Selected Map
# -----------------------------------------
st.markdown("<div class='section'></div>", unsafe_allow_html=True)
fig = create_map(selected_map, df, selected_projection, selected_color_scale)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# adding divider for spacing
st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------------------
# Line Chart Analysis Section
# -----------------------------------------
st.markdown("<div class='section'></div>", unsafe_allow_html=True)
st.markdown("### Line Chart Analysis")
st.markdown("Select one or more countries to view the trend over time for the selected indicator.")

# Create a list of available countries from the DataFrame
countries = sorted(df["Country"].unique())
selected_countries_line = st.multiselect("Select Countries", countries)

# Automatically use the same indicator as selected in the map
map_indicator_dict = {
    "GDP": "gdp_per_capita",
    "Total Population": "total_population",
    "Net Migration": "net_migration"
}
indicator_for_line = map_indicator_dict[selected_map]

# Automatically generate and display the line chart without needing a button click
df_line = df[df["Country"].isin(selected_countries_line)]
fig_line = px.line(
    df_line,
    x="Year",
    y=indicator_for_line,
    color="Country",
    title=f"{selected_map} Over Time"
)

# Update layout to ensure that all text (including axis titles and ticks) is black
fig_line.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    title_font_color='black',
    title_font_size=18,
    font=dict(color='black', size=12),
    legend_title_font_color='black',
    legend_font_color='black'
)
fig_line.update_xaxes(
    tickfont=dict(color='black'),
    title_font=dict(color='black'),
    title="Year"
)
fig_line.update_yaxes(
    tickfont=dict(color='black'),
    title_font=dict(color='black'),
    title=indicator_for_line.replace("_", " ").title()
)
# Update x-axis and y-axis tick labels and title fonts to black
fig_line.update_xaxes(tickfont=dict(color='black'), title_font=dict(color='black'))
fig_line.update_yaxes(tickfont=dict(color='black'), title_font=dict(color='black'))

st.plotly_chart(fig_line, use_container_width=True)
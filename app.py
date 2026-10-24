import streamlit as st

from utils.data import get_data
from sections.intro import show_intro
from sections.overview import show_overview
from sections.deep_dives import show_deep_dives
from sections.energy_context import show_energy_context
from sections.conclusions import show_conclusions
from utils.io import DATA_SOURCE, DATA_LICENSE

STUDENT_NAME = "Louis-Marie FORT"
STUDENT_GROUP = "Data & AI"
GITHUB_URL = "https://github.com/LouisMarieFort"


st.set_page_config(
    page_title="Europe's Data Centres and Electricity",
    layout="wide",
)

page = st.navigation([
    st.Page(show_intro, title="1. The map", default=True),
    st.Page(show_overview, title="2. The contrast"),
    st.Page(show_deep_dives, title="3. Trends and renewables"),
    st.Page(show_energy_context, title="4. The energy context"),
    st.Page(show_conclusions, title="5. What the data tells us"),
])

with st.sidebar:
    st.markdown("### Explore a country")

    df = get_data()

    available_countries = sorted(
        df.loc[
            df["year"].eq(2024) & df["dc_gwh"].notna(),
            "geo",
        ].unique()
    )

    st.selectbox(
        "Country with published data in 2024",
        options=available_countries,
        index=available_countries.index("FR")
        if "FR" in available_countries
        else 0,
        key="explore_country",
    )

    st.radio(
        "Metric to display",
        ["Absolute consumption (GWh)", "National share (%)"],
        key="global_metric"
    )

    st.caption(
        "This selection updates the country snapshot on page 2. "
    )


    st.divider()


    st.markdown("### EFREI Paris · Data Visualization and Analysis Project")
    st.write(f"**Student:** {STUDENT_NAME}")
    st.write(f"**Group:** {STUDENT_GROUP}")
    st.write("**Teacher:** Mano Joseph Mathew")

    st.caption(f"Sources: {DATA_SOURCE} — isoc_env_ict_nrg, nrg_cb_e, nrg_ind_ren.<br>License: {DATA_LICENSE}", unsafe_allow_html=True)
    
    

    st.link_button(
        "My GitHub",
        GITHUB_URL,
        use_container_width=True,
    )

page.run()

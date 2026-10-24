import pandas as pd
import streamlit as st

URLS = {
    "datacenters": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_env_ict_nrg?format=SDMX-CSV&compressed=true",
    "electricity": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e?format=SDMX-CSV&compressed=true",
    "renewables": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ren?format=SDMX-CSV&compressed=true",
}
DATA_SOURCE = "Eurostat (data.europa.eu)"
DATA_LICENSE = "Creative Commons Attribution 4.0 International (CC BY 4.0)"

@st.cache_data(show_spinner=False)
def fetch_and_cache(url):
    df = pd.read_csv(url, compression="gzip")
    return {"Sheet1": df}

def load_data():
    data = {}
    for name, url in URLS.items():
        data[name] = fetch_and_cache(url)
    return data
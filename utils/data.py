import streamlit as st

from utils.io import load_data
from utils.prep import make_tables


@st.cache_data(max_entries=1)
def get_data():
    raw = load_data()
    tables = make_tables(raw)
    return tables["merged"]

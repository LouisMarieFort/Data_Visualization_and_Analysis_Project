# EFREI Data Stories 2026: Can the energy transition keep up with digital demand?

## Project Overview / Question
As data-centre electricity demand grows, can the renewable electricity transition keep pace? 
This interactive data-storytelling dashboard explores the relationship between the growing electricity demand of data centres and the progress of the renewable energy transition across European countries (2020-2024).

**Author:** Louis-Marie FORT (Group: Data & AI)  
**Teacher:** Mano Joseph Mathew

## Audience and Story
This dashboard is designed for energy policy analysts, tech researchers, and public regulators seeking to understand the energy footprint of Europe's digital infrastructure. 

The narrative guides the user through five structured steps:
1. **The Map:** A geographical overview of data-centre electricity consumption across Europe.
2. **The Contrast:** A comparison between absolute electricity volume (GWh) and the national share (%), highlighting outliers like Ireland.
3. **Trends and Renewables:** A temporal analysis showing how demand has evolved from 2022 to 2024 across a constant panel of countries.
4. **The Energy Context:** An exploration of whether growing digital demand is matched by an increasing share of national renewable energy.
5. **Conclusions:** A synthesis of key findings, actionable insights, and transparent data limitations.

## Data Sources
All datasets are public and provided by Eurostat (accessed via data.europa.eu). Data is fetched dynamically via the Eurostat SDMX API.

| Eurostat code | Indicator used | Unit |
| --- | --- | --- |
| isoc_env_ict_nrg | Data-centre electricity consumption | GWh |
| nrg_cb_e | Final electricity consumption, FC / E7000 | GWh |
| nrg_ind_ren | Renewable share of gross electricity consumption, REN_ELC | % |

## Methodology
Data is loaded and cached efficiently using Streamlit's `@st.cache_data`. 
- **Filtering & Joins:** We isolate data-centre consumption (NACE code: `DATAC`) and merge it with final national electricity consumption using a Left Join on the `geo` and `year` dimensions. 
- **Calculations:** The data-centre share is calculated by dividing the data-centre GWh by the total national electricity GWh, avoiding division by zero.
- **Constant Panel Analysis:** To ensure unbiased trend analysis, the temporal charts comparing 2022 to 2024 strictly use a fixed panel of 18 countries that reported data consistently across all three years.

## Data Quality, Limitations and Ethics
- **Regulatory Bias:** Published data-centre values increased significantly from 2021 to 2024. This is largely due to expanding EU reporting mandates (mandatory for >1MW capacity starting in 2024) rather than purely organic growth.
- **Confidentiality:** 11 country-year records are marked as confidential ('C'). These are omitted from calculations but should not be interpreted as zeros.
- **Validation & Duplicates:** The dataset was checked for anomalies. No duplicate country-year records were found, and validation checks ensured no negative values for electricity consumption.
- **Scope of Renewables:** The renewable indicator measures the *national* grid's average share. It does not reflect the specific power purchase agreements (PPAs) or local grid capacity dedicated to individual data centres. 
- **Missing Metrics:** This dataset does not include carbon emissions, cooling water consumption, or nuclear energy shares.

## Run Locally (Reproducibility)
To run this application in a deterministic, clean environment:

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the Streamlit application (data is downloaded automatically via script):
   ```bash
   python -m streamlit run app.py
   ```

## Deliverables
- **Deployed App:** [Insert Streamlit Community Cloud URL here]
- **Repository:** [Insert GitHub URL here]
- **Demo Video:** [Insert YouTube/Loom URL here]

## Licenses
- **Code:** The Python code for this Streamlit application is licensed under the MIT License.
- **Data:** The datasets used in this project are provided by Eurostat and are subject to the European Commission's reuse policy, equivalent to the Creative Commons Attribution 4.0 International (CC BY 4.0) license.
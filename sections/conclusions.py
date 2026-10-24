import streamlit as st

from utils.data import get_data
from utils.viz import demand_renewables_change_chart, missing_data_chart


def show_conclusions():
    df = get_data()

    st.title("Can the energy transition keep up with digital demand?")

    st.subheader("What we found")

    st.write(
        "The question changes depending on the scale. "
        "Germany reports the largest data-centre electricity demand, "
        "but that demand represents a much greater share of national "
        "electricity consumption in Ireland."
    )

    st.write(
        "Demand is rising, even when we compare the same countries. "
        "Across 18 countries with published values in every year "
        "from 2022 to 2024, reported data-centre electricity "
        "consumption rose by 19.2%."
    )

    st.write(
        "The renewable transition did not simply stop as "
        "digital demand grew. "
        "In 7 of 11 comparable countries, "
        "the national weight of data centres and the renewable "
        "electricity share both increased between 2022 and 2024."
    )

    st.divider()

    st.subheader("So, is electricity keeping pace?")

    st.write(
        "While the data show that growing data-centre demand and progress "
        "in renewable electricity can coexist. They do not show "
        "whether enough electricity is available where and when "
        "data centres need it."
    )

    st.write(
        "A higher renewable share describes a national trend. "
        "To test whether supply is keeping pace with demand, "
        "we would also need changes in electricity generation "
        "measured in GWh and information on local grid capacity."
    )

    with st.expander("Data Quality & Limitations"):
        published = int(df["dc_gwh"].notna().sum())

        confidential = int(
            (
                df["dc_gwh"].isna()
                & df["CONF_STATUS"].eq("C")
            ).sum()
        )

        st.write(
            f"The downloaded data contain {published} published "
            f"country-year values and {confidential} confidential "
            "records. Confidential values are not zeros."
        )

        st.write(
            "The 18-country trend is not a complete European total. "
            "Countries without comparable data are absent from "
            "the renewable comparison."
        )

        st.write(
            "The renewable indicator does not include nuclear power "
            "and does not describe the electricity supplied to "
            "an individual data centre. None of these datasets "
            "measures local grid constraints or carbon emissions."
        )

        st.plotly_chart(
            missing_data_chart(df),
            use_container_width=True,
        )

        st.write(
            "The dataset was checked for anomalies. "
            "No duplicate country-year records were found, and validation checks "
            "ensured no negative values for electricity consumption."
        )


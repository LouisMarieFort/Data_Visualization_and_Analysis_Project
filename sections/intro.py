import streamlit as st

from utils.data import get_data
from utils.viz import binned_map_chart, ranking_chart


def show_intro():
    df = get_data()
    data = df.loc[df["year"] == 2024].copy()

    st.title("Where do Europe's data centres draw electricity?")
    st.write(
        "In 2024, reported data-centre electricity use varied widely "
        "across European countries."
    )

    st.plotly_chart(
        binned_map_chart(
            data,
            title="Reported data-centre electricity consumption — 2024",
        ),
        use_container_width=True,
    )

    published = int(data["dc_gwh"].notna().sum())
    confidential = sorted(
        data.loc[
            data["dc_gwh"].isna()
            & data["CONF_STATUS"].eq("C"),
            "geo",
        ].tolist()
    )

    st.markdown(
        "On this map, we can see that Germany, Ireland and Netherlands have the "
        "highest reported data-centre electricity consumption. "
        "The different categories show that there are big differences "
        "between countries in the amount of data-centre electricity used."
    )

    st.divider()

    st.subheader("How large are the differences?")

    st.plotly_chart(
        ranking_chart(
            data,
            metric="dc_gwh",
            top_n=15,
            title="Countries with the highest reported consumption — 2024",
        ),
        use_container_width=True,
    )

    st.markdown(
        "The ranking makes these differences clearer. Germany reports much "
        "higher data-centre electricity consumption than any other country shown, "
        "while Ireland and the Netherlands follow at considerably lower levels."
    )

    st.info(
        "But does this mean that Germany especially focuses on data-centres ? " \
        "We shall explore that in the next page."
    )

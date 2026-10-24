import streamlit as st

from utils.data import get_data
from utils.viz import (
    demand_renewables_change_chart,
    energy_context_scatter_chart,
)


def show_energy_context():
    df = get_data()

    st.title("Is renewable electricity keeping pace ?")

    st.write(
        "Data-centre demand is rising across the EU countries. "
        "What does the national renewable electricity context look like "
        "where that demand matters most?"
    )

    try:
        fig, current = energy_context_scatter_chart(df)
    except ValueError as error:
        st.info(str(error))
    else:
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            "Ireland is far apart from the other countries in terms "
            "of data-centre share. Yet countries with a small data-centre "
            "share can have very different renewable electricity shares, like Norway. "
            "In 2024, a larger digital footprint does not correspond to "
            "one clear renewable-energy profile."
        )

    st.divider()

    st.subheader("Did both indicators move in the same direction?")

    

    try:
        fig, changes = demand_renewables_change_chart(df)
    except ValueError as error:
        st.info(str(error))
    else:
        st.plotly_chart(fig, use_container_width=True)

        both_up = int(
            (
                changes["dc_change_pp"].gt(0)
                & changes["renewable_change_pp"].gt(0)
            ).sum()
        )

        demand_up_renewables_down = int(
            (
                changes["dc_change_pp"].gt(0)
                & changes["renewable_change_pp"].lt(0)
            ).sum()
        )

        st.write(
            "In 7 of the 11 comparable countries, the national weight of data "
            "centres and the renewable electricity share both increased "
            "between 2022 and 2024. Growing digital demand and renewable "
            "progress can coexist—but not every country followed that path."
            )

    st.markdown(
        "Renewables are gaining ground in many of these countries. "
        "But does a rising national share mean electricity supply "
        "is keeping pace with data-centre demand ?"
    )

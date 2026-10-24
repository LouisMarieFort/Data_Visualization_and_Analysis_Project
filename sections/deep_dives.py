import streamlit as st

from utils.data import get_data
from utils.viz import (
    constant_panel_chart,
    coverage_chart,
    country_growth_chart,
    country_growth_ranking_chart,
)


def show_deep_dives():
    df = get_data()

    st.title("Is data-centre electricity demand rising?")

    st.plotly_chart(
        coverage_chart(df),
        use_container_width=True,
    )

    st.markdown(
        "Published data-centre values increased "
        "from 6 countries in 2021 to 21 in 2022, then 27 in 2024. "
        "A rise in reporting coverage is not the same as a rise in "
        "electricity consumption."
    )

    with st.expander("Why did reporting expand?"):
        st.write(
            "EU rules made detailed energy reporting for services "
            "mandatory from reference year 2022. Reporting for the "
            "specific data-centre category became mandatory from "
            "reference year 2024 for reporting units with at least "
            "1 MW of total power capacity. It can explain some of the "
            "increase in published values."
        )

    st.subheader("Compare the same countries over time")
    st.write(
        "This chart follows only countries with a published "
        "data-centre value in every year from 2022 to 2024."
    )

    try:
        fig, panel, totals = constant_panel_chart(df)
    except ValueError as error:
        st.info(str(error))
    else:
        fig.update_yaxes(
            range=[35000, 45000],
            tick0=35000,
            dtick=2000,
        )

        st.plotly_chart(fig, use_container_width=True)

        start = totals.loc[
            totals["year"] == 2022, "dc_gwh"
        ].iloc[0]
        end = totals.loc[
            totals["year"] == 2024, "dc_gwh"
        ].iloc[0]

        change = (end / start - 1) * 100 if start > 0 else None
        country_count = panel["geo"].nunique()

        if change is None:
            st.markdown(
                f"**What we can observe —** Across the same "
                f"{country_count} reporting countries, the recorded "
                f"total was {start:,.0f} GWh in 2022 and "
                f"{end:,.0f} GWh in 2024."
            )
        else:
            st.markdown(
                "Across the same "
                f"{country_count} reporting countries, recorded "
                f"data-centre electricity consumption changed from "
                f"{start:,.0f} GWh in 2022 to {end:,.0f} GWh "
                f"in 2024 ({change:+.1f}%)."
            )

    st.divider()

    st.subheader("Was growth shared across countries?")
    st.write(
        "The chart above combines the same reporting countries in GWh. "
        "The chart below ranks each country's change relative to its "
        "own 2022 level."
    )

    try:
        ranking_fig, growth_data, excluded = (
            country_growth_ranking_chart(df)
        )
    except ValueError as error:
        st.info(str(error))
    else:
        if excluded:
            st.caption(
                f"This percentage ranking shows {len(growth_data)} "
                f"countries. Another {len(excluded)} had a published "
                "value of zero in 2022, so their percentage change "
                "cannot be calculated."
            )

        st.plotly_chart(
            ranking_fig,
            use_container_width=True,
        )

        increased = int(
            (growth_data["end_gwh"] > growth_data["start_gwh"]).sum()
        )
        decreased = int(
            (growth_data["end_gwh"] < growth_data["start_gwh"]).sum()
        )
        unchanged = int(
            (growth_data["end_gwh"] == growth_data["start_gwh"]).sum()
        )

    st.markdown(
        f"Consumption rose in {increased} of the {len(growth_data)} "
        f"countries shown, although the size of the increase varied considerably. "
        "Moldova remained almost unchanged, while Portugal recorded the "
        "largest relative rise."
    )


    st.markdown(
        "As data-centre electricity demand grows, "
        "what can national electricity and renewable-energy data tell "
        "us about the wider energy context ?"
    )

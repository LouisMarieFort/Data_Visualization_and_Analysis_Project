import streamlit as st

from utils.data import get_data
from utils.viz import comparison_chart, ranking_chart


def show_overview():
    df = get_data()
    data_2024 = df.loc[df["year"] == 2024].copy()

    st.title("The biggest consumer is not the biggest national share")
    
    st.subheader("Explore a specific country in 2024")

    selected_country = st.session_state.get("explore_country")

    country_data = df.loc[
        df["year"].eq(2024)
        & df["geo"].eq(selected_country)
    ]

    if country_data.empty:
        st.info("No 2024 data is available for this country.")
    else:
        country = country_data.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Data-centre electricity",
            f"{country['dc_gwh']:,.0f} GWh",
        )

        col2.metric(
            "Share of final electricity",
            f"{country['dc_share_pct']:.2f}%",
        )

        col3.metric(
            "National renewable share",
            f"{country['renewable_share_pct']:.1f}%"
            if country["renewable_share_pct"]
            == country["renewable_share_pct"]
            else "Not available",
        )
        
    st.divider()

    st.write(
        "Germany and Ireland show why electricity volume and national "
        "weight answer different questions."
    )

    comparison = data_2024.loc[
        data_2024["geo"].isin(["DE", "IE"])
    ].dropna(subset=["dc_gwh", "dc_share_pct"])

    if set(comparison["geo"]) == {"DE", "IE"}:
        germany = comparison.set_index("geo").loc["DE"]
        ireland = comparison.set_index("geo").loc["IE"]

        st.plotly_chart(
            comparison_chart(
                data_2024,
                countries=("DE", "IE"),
                title="Germany and Ireland: absolute consumption vs national share in 2024",
            ),
            use_container_width=True,
        )

    germany = comparison.set_index("geo").loc["DE"]
    ireland = comparison.set_index("geo").loc["IE"]
    
    st.write(
        f"In 2024, Germany reported {germany['dc_gwh']:,.0f} GWh "
        "of data-centre electricity consumption, compared with "
        f"{ireland['dc_gwh']:,.0f} GWh in Ireland. Yet data centres "
        f"accounted for {germany['dc_share_pct']:.2f}% of Germany's "
        "final electricity consumption and "
        f"{ireland['dc_share_pct']:.2f}% of Ireland's. "
        "This shows that in Ireland, data-centres are way more "
        "significant in the national electricity consumption, "
        "compared with Germany."
    )

    st.subheader("Does this contrast appear elsewhere?")

    # --- BLOC MANQUANT AJOUTÉ ICI ---
    metric = st.session_state.get("global_metric", "Absolute consumption (GWh)")

    selected_metric = (
        "dc_share_pct"
        if metric == "National share (%)"
        else "dc_gwh"
    )
    # --------------------------------

    st.plotly_chart(
        ranking_chart(
            data_2024,
            metric=selected_metric,
            top_n=15,
        ),
        use_container_width=True,
    )

    st.info(
        "Use the sidebar 'Metric to display' to switch between GWh and % and see how the ranking changes."
    )

    st.write(
        "Germany ranks first in absolute consumption, but Ireland is "
        "far ahead when it comes to national share. The ranking shows that other "
        "countries also have a different position between the two rankings. "
        "This shows that both metrics are important to understand the behaviour "
        "of every country when it comes to data-centres."
    )

    st.write(
        "These rankings show where data-centre electricity demand mattered most "
        "in 2024. But a single year cannot tell us whether that demand is growing. "
        "Did consumption change over time? And is it coherent with the renewable "
        "electricity objectives of EU countries?"
    )
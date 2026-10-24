import streamlit as st

from utils.data import get_data
from utils.viz import (
    comparison_chart,
    coverage_chart,
    heatmap_chart,
    line_chart,
    map_chart,
    missing_data_chart,
    ranking_chart,
    renewables_scatter,
    demand_renewables_timeline
)


st.set_page_config(
    page_title="Visualization Gallery",
    layout="wide",
)

st.title("Visualization Gallery")
st.caption("A standalone preview of every chart in utils/viz.py")

try:
    df = get_data()
except (FileNotFoundError, KeyError, ValueError) as error:
    st.error(f"Could not prepare the data: {error}")
    st.stop()

years = sorted(df["year"].dropna().unique().tolist())

if not years:
    st.error("No years are available in the prepared data.")
    st.stop()

year = st.selectbox(
    "Year for single-year charts",
    years,
    index=len(years) - 1,
)

year_df = df.loc[df["year"] == year].copy()

st.divider()
st.header("1. Map")

st.subheader("The same GWh data with more detail")

st.plotly_chart(
    map_chart(year_df, metric="dc_gwh", scale="log"),
    use_container_width=True,
)

st.caption(
    "The two maps show identical GWh values. The second uses "
    "logarithmic colours to distinguish lower values."
)


st.caption(
    "Uncoloured countries have no published value in this export. "
    "They should not be interpreted as zero."
)

st.divider()
st.header("2. Country rankings")

st.plotly_chart(
    ranking_chart(year_df, metric="dc_gwh", top_n=15),
    use_container_width=True,
)

st.plotly_chart(
    ranking_chart(year_df, metric="dc_share_pct", top_n=15),
    use_container_width=True,
)

st.divider()
st.header("3. Country trends")

available_countries = sorted(
    df.loc[df["dc_gwh"].notna(), "geo"].unique().tolist()
)

default_countries = [
    country
    for country in ("DE", "IE", "FR")
    if country in available_countries
]

selected_countries = st.multiselect(
    "Countries for trend charts",
    available_countries,
    default=default_countries,
)

if selected_countries:
    st.plotly_chart(
        line_chart(
            df,
            metric="dc_gwh",
            countries=selected_countries,
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        line_chart(
            df,
            metric="dc_share_pct",
            countries=selected_countries,
        ),
        use_container_width=True,
    )
else:
    st.info("Select at least one country to preview the trend charts.")

st.divider()
st.header("Data-centre demand and renewable electricity over time")

timeline_countries = st.multiselect(
    "Countries for the two-panel timeline",
    available_countries,
    default=[
        country
        for country in ("DE", "IE")
        if country in available_countries
    ],
    max_selections=4,
    key="demand_renewables_countries",
)

if timeline_countries:
    st.plotly_chart(
        demand_renewables_timeline(
            df,
            countries=timeline_countries,
        ),
        use_container_width=True,
    )

    st.caption(
        "The lower panel shows each country's national renewable "
        "electricity share. It does not measure the renewable share "
        "of electricity used by its data centres."
    )
else:
    st.info("Select at least one country to display the timeline.")


st.divider()
st.header("4. Two-country comparison")

published_countries = sorted(
    year_df.loc[
        year_df["dc_gwh"].notna()
        & year_df["dc_share_pct"].notna(),
        "geo",
    ].unique().tolist()
)

if len(published_countries) >= 2:
    default_pair = [
        country
        for country in ("DE", "IE")
        if country in published_countries
    ]

    if len(default_pair) < 2:
        default_pair = published_countries[:2]

    pair = st.multiselect(
        "Select exactly two countries",
        published_countries,
        default=default_pair,
        max_selections=2,
    )

    if len(pair) == 2:
        st.plotly_chart(
            comparison_chart(year_df, countries=tuple(pair)),
            use_container_width=True,
        )
    else:
        st.info("Select two countries to display the comparison.")
else:
    st.info("Fewer than two countries have comparable data for this year.")

st.divider()
st.header("5. Renewable electricity context")

complete_year = year_df.dropna(
    subset=["dc_share_pct", "renewable_share_pct"]
)

if complete_year.empty:
    st.info("No countries have both indicators for this year.")
else:
    st.plotly_chart(
        renewables_scatter(complete_year),
        use_container_width=True,
    )

st.caption(
    "This chart shows the national renewable electricity context, "
    "not the electricity supply of individual data centres."
)

st.divider()
st.header("6. Data coverage")

st.plotly_chart(
    coverage_chart(df),
    use_container_width=True,
)

st.plotly_chart(
    missing_data_chart(df),
    use_container_width=True,
)

st.divider()
st.header("7. Country-year heatmaps")

st.plotly_chart(
    heatmap_chart(df, metric="dc_gwh"),
    use_container_width=True,
)

st.plotly_chart(
    heatmap_chart(df, metric="dc_share_pct"),
    use_container_width=True,
)

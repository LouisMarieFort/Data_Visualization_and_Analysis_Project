import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import qualitative


ISO3 = {
    "AL": "ALB", "AT": "AUT", "BE": "BEL", "BG": "BGR",
    "CY": "CYP", "CZ": "CZE", "DE": "DEU", "DK": "DNK",
    "EE": "EST", "EL": "GRC", "ES": "ESP", "FI": "FIN",
    "FR": "FRA", "HR": "HRV", "HU": "HUN", "IE": "IRL",
    "IT": "ITA", "LT": "LTU", "LU": "LUX", "LV": "LVA",
    "MD": "MDA", "ME": "MNE", "MK": "MKD", "MT": "MLT",
    "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT",
    "RO": "ROU", "RS": "SRB", "SE": "SWE", "SI": "SVN",
    "SK": "SVK", "TR": "TUR",
}

LABELS = {
    "dc_gwh": "Data-centre electricity consumption (GWh)",
    "electricity_gwh": "National final electricity consumption (GWh)",
    "dc_share_pct": "Data-centre share of final electricity consumption (%)",
    "renewable_share_pct": "National renewable electricity share (%)",
}

BLUE = "#2563eb"
TEAL = "#0d9488"
ORANGE = "#f59e0b"


def _check_columns(df, *columns):
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")


def _check_single_year(df):
    _check_columns(df, "year")
    years = df["year"].dropna().unique()
    if len(years) != 1:
        raise ValueError("This chart requires data for one year.")
    return int(years[0])


def _check_metric(metric):
    if metric not in LABELS:
        raise ValueError("Unknown metric: ", metric)


def _style(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        font=dict(size=13),
        hovermode="closest",
    )
    return fig


def map_chart(df, metric="dc_gwh", title=None, scale="linear"):
    if metric not in ("dc_gwh", "dc_share_pct"):
        raise ValueError("Wrong metric. Must be 'dc_gwh' or 'dc_share_pct'.")

    if scale not in ("linear", "log"):
        raise ValueError("Supported scale must be linear or log.")

    if scale == "log" and metric != "dc_gwh":
        raise ValueError("The log colour scale is only available for GWh.")

    _check_columns(df, "geo", "year", metric)
    year = _check_single_year(df)

    data = df.dropna(subset=[metric]).copy()
    data["iso3"] = data["geo"].map(ISO3)

    unknown = sorted(data.loc[data["iso3"].isna(), "geo"].unique())
    if unknown:
        raise ValueError(f"Country codes missing from the map: {unknown}")

    if scale == "log":
        data["map_colour"] = np.log10(data["dc_gwh"].clip(lower=0) + 1)
        colour_column = "map_colour"
        legend_title = "GWh (log colours)"
    else:
        colour_column = metric
        legend_title = "GWh" if metric == "dc_gwh" else "%"

    hover_data = {
        "iso3": False,
        colour_column: False,
        metric: ":,.1f" if metric == "dc_gwh" else ":.2f",
    }

    for column in ("dc_gwh", "electricity_gwh", "dc_share_pct"):
        if column in data.columns and column != metric:
            hover_data[column] = (
                ":.2f" if column.endswith("_pct") else ":,.1f"
            )

    fig = px.choropleth(
        data,
        locations="iso3",
        locationmode="ISO-3",
        color=colour_column,
        hover_name="geo",
        hover_data=hover_data,
        scope="europe",
        color_continuous_scale="Blues",
        labels={**LABELS, "map_colour": "Colour scale"},
        title=title or f"Data-centre electricity in Europe — {year}",
    )

    fig.update_geos(
        scope="europe",
        showcoastlines=False,
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor="#e5e7eb",
    )

    if scale == "log" and not data.empty:
        maximum = data["dc_gwh"].max()
        ticks = [0, 10, 100, 1000, 10000, 20000]
        ticks = [value for value in ticks if value <= maximum]

        fig.update_layout(
            coloraxis_colorbar=dict(
                title=legend_title,
                tickvals=[np.log10(value + 1) for value in ticks],
                ticktext=[f"{value:,}" for value in ticks],
            )
        )
    else:
        fig.update_layout(
            coloraxis_colorbar=dict(title=legend_title)
        )

    return _style(fig, height=610)


def binned_map_chart(df, title=None):
    _check_columns(df, "geo", "year", "dc_gwh")
    year = _check_single_year(df)

    data = df.dropna(subset=["dc_gwh"]).copy()
    data["iso3"] = data["geo"].map(ISO3)

    unknown = sorted(data.loc[data["iso3"].isna(), "geo"].unique())
    if unknown:
        raise ValueError(f"Country codes missing from the map: {unknown}")

    bins = [
        "0 GWh",
        ">0–100 GWh",
        ">100–1,000 GWh",
        ">1,000–5,000 GWh",
        ">5,000 GWh",
    ]

    data["range"] = pd.cut(
        data["dc_gwh"],
        bins=[-0.001, 0, 100, 1000, 5000, float("inf")],
        labels=bins,
        include_lowest=True,
    )

    fig = px.choropleth(
        data,
        locations="iso3",
        locationmode="ISO-3",
        color="range",
        hover_name="geo",
        custom_data=["dc_gwh"],
        category_orders={"range": bins},
        color_discrete_map={
            "0 GWh": "#d1d5db",
            ">0–100 GWh": "#c6dbef",
            ">100–1,000 GWh": "#6baed6",
            ">1,000–5,000 GWh": "#2171b5",
            ">5,000 GWh": "#08306b",
        },
        scope="europe",
        title=title or f"Data-centre electricity consumption — {year}",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Data-centre consumption: %{customdata[0]:,.1f} GWh"
            "<extra></extra>"
        )
    )

    fig.update_geos(
        scope="europe",
        showcoastlines=False,
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor="#f3f4f6",
    )

    fig.update_layout(
    legend_title_text="Consumption (GWh)",
    legend=dict(
        orientation="v",
        x=0.755,
        xanchor="left",
        y=0.5,
        yanchor="middle",
        font=dict(size=15),
        title_font=dict(size=16),
    ),
    margin=dict(l=20, r=210, t=55, b=20),
)

    return _style(fig, height=1000)


def ranking_chart(df, metric="dc_share_pct", top_n=None, title=None):
    _check_metric(metric)
    _check_columns(df, "geo", "year", metric)
    _check_single_year(df)

    data = df.dropna(subset=[metric]).sort_values(
        metric, ascending=False
    ).copy()

    if top_n is not None:
        data = data.head(top_n)

    hover_data = {
        column: (
            ":.2f" if column.endswith("_pct") else ":,.1f"
        )
        for column in LABELS
        if column in data.columns and column != metric
    }

    fig = px.bar(
        data,
        x=metric,
        y="geo",
        orientation="h",
        hover_data=hover_data,
        labels={**LABELS, "geo": "Country"},
        title=title or LABELS[metric],
    )

    fig.update_traces(marker_color=BLUE)
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=data["geo"].iloc[::-1].tolist(),
    )

    return _style(fig, height=max(350, 38 * len(data) + 100))


def line_chart(df, metric="dc_gwh", countries=None, title=None):
    _check_metric(metric)
    _check_columns(df, "geo", "year", metric)

    data = df.copy()

    if countries is not None:
        data = data.loc[data["geo"].isin(countries)]

    data = data.dropna(subset=[metric]).sort_values(
        ["geo", "year"]
    )

    fig = px.line(
        data,
        x="year",
        y=metric,
        color="geo",
        markers=True,
        labels={**LABELS, "geo": "Country", "year": "Year"},
        title=title or f"{LABELS[metric]} over time",
    )

    fig.update_xaxes(dtick=1)
    return _style(fig)


def comparison_chart(df, countries=("DE", "IE"), title=None):
    _check_columns(df, "geo", "year", "dc_gwh", "dc_share_pct")
    year = _check_single_year(df)

    data = df.loc[df["geo"].isin(countries)].dropna(
        subset=["dc_gwh", "dc_share_pct"]
    )

    if set(data["geo"]) != set(countries):
        raise ValueError(
            f"Both countries must have published data for {year}."
        )

    data = data.set_index("geo").loc[list(countries)].reset_index()

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Absolute consumption (GWh)",
            "Share of national final consumption (%)",
        ),
    )

    fig.add_trace(
        go.Bar(
            x=data["geo"],
            y=data["dc_gwh"],
            marker_color=BLUE,
            text=[f"{value:,.0f}" for value in data["dc_gwh"]],
            textposition="outside",
            hovertemplate="%{x}: %{y:,.1f} GWh<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=data["geo"],
            y=data["dc_share_pct"],
            marker_color=TEAL,
            text=[
                f"{value:.2f}%" for value in data["dc_share_pct"]
            ],
            textposition="outside",
            hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        showlegend=False,
        title=title or f"Volume versus national share — {year}",
    )

    return _style(fig, height=410)


def renewables_scatter(df, title=None):
    _check_columns(
        df, "geo", "dc_share_pct", "renewable_share_pct"
    )

    data = df.dropna(
        subset=["dc_share_pct", "renewable_share_pct"]
    ).copy()

    hover_data = {}

    if "dc_gwh" in data.columns:
        hover_data["dc_gwh"] = ":,.1f"

    if "year" in data.columns:
        hover_data["year"] = True

    fig = px.scatter(
        data,
        x="dc_share_pct",
        y="renewable_share_pct",
        hover_name="geo",
        hover_data=hover_data,
        labels=LABELS,
        title=title or "Data-centre demand and renewable electricity",
    )

    fig.update_traces(
        marker=dict(size=13, color=TEAL, opacity=0.8)
    )

    return _style(fig)


def coverage_chart(df, title="Published data by year"):
    _check_columns(df, "geo", "year", "dc_gwh")

    coverage = (
        df.loc[df["dc_gwh"].notna()]
        .groupby("year")["geo"]
        .nunique()
        .reset_index(name="countries")
    )

    fig = px.bar(
        coverage,
        x="year",
        y="countries",
        text="countries",
        labels={
            "year": "Year",
            "countries": "Countries with published values",
        },
        title=title,
    )

    fig.update_traces(
        marker_color=ORANGE,
        textposition="outside",
    )
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(rangemode="tozero")

    return _style(fig, height=370)


def missing_data_chart(df, title="Published and confidential values"):
    _check_columns(df, "year", "dc_gwh", "CONF_STATUS")

    data = df[["year", "dc_gwh", "CONF_STATUS"]].copy()
    data["status"] = "Not published"
    data.loc[data["CONF_STATUS"].eq("C"), "status"] = "Confidential"
    data.loc[data["dc_gwh"].notna(), "status"] = "Published"

    counts = (
        data.groupby(["year", "status"])
        .size()
        .reset_index(name="observations")
    )

    fig = px.bar(
        counts,
        x="year",
        y="observations",
        color="status",
        barmode="stack",
        color_discrete_map={
            "Published": BLUE,
            "Confidential": ORANGE,
            "Not published": "#9ca3af",
        },
        labels={
            "year": "Year",
            "observations": "Country-year records",
            "status": "Status",
        },
        title=title,
    )

    fig.update_xaxes(dtick=1)
    return _style(fig, height=380)


def heatmap_chart(df, metric="dc_share_pct", title=None):
    _check_metric(metric)
    _check_columns(df, "geo", "year", metric)

    matrix = (
        df.pivot(index="geo", columns="year", values=metric)
        .sort_index()
    )

    fig = go.Figure(
        go.Heatmap(
            z=matrix.to_numpy(),
            x=matrix.columns.tolist(),
            y=matrix.index.tolist(),
            colorscale="Blues",
            colorbar=dict(
                title="GWh" if metric.endswith("_gwh") else "%"
            ),
            hovertemplate=(
                "Country: %{y}<br>"
                "Year: %{x}<br>"
                "Value: %{z:.2f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=title or f"{LABELS[metric]} by country and year"
    )

    return _style(
        fig,
        height=max(420, 28 * len(matrix) + 120),
    )


def demand_renewables_timeline(df, countries, title=None):
    _check_columns(
        df,
        "geo",
        "year",
        "dc_gwh",
        "renewable_share_pct",
    )

    if not countries:
        raise ValueError("Select at least one country.")

    if len(countries) > 4:
        raise ValueError("Select no more than four countries.")

    data = df.loc[df["geo"].isin(countries)].copy()
    data = data.sort_values(["geo", "year"])

    if data.empty:
        raise ValueError("No data is available for the selected countries.")

    duplicates = data.duplicated(["geo", "year"])

    if duplicates.any():
        raise ValueError("Each country and year must appear only once.")

    years = sorted(data["year"].dropna().unique().tolist())

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=(
            "Data-centre electricity consumption",
            "National renewable electricity share",
        ),
    )

    palette = qualitative.Plotly

    for index, country in enumerate(countries):
        country_data = data.loc[data["geo"] == country]
        color = palette[index % len(palette)]

        demand = country_data.dropna(subset=["dc_gwh"])
        renewables = country_data.dropna(
            subset=["renewable_share_pct"]
        )

        fig.add_trace(
            go.Scatter(
                x=demand["year"],
                y=demand["dc_gwh"],
                mode="lines+markers",
                name=country,
                legendgroup=country,
                line=dict(color=color, width=3),
                marker=dict(size=9),
                connectgaps=False,
                hovertemplate=(
                    f"{country}<br>"
                    "Year: %{x}<br>"
                    "Data-centre demand: %{y:,.1f} GWh"
                    "<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=renewables["year"],
                y=renewables["renewable_share_pct"],
                mode="lines+markers",
                name=country,
                legendgroup=country,
                showlegend=False,
                line=dict(color=color, width=3, dash="dot"),
                marker=dict(size=9),
                connectgaps=False,
                hovertemplate=(
                    f"{country}<br>"
                    "Year: %{x}<br>"
                    "National renewable share: %{y:.2f}%"
                    "<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    fig.update_yaxes(
        title_text="Data-centre demand (GWh)",
        rangemode="tozero",
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title_text="Renewable share (%)",
        rangemode="tozero",
        row=2,
        col=1,
    )
    fig.update_xaxes(
        title_text="Year",
        tickmode="array",
        tickvals=years,
        row=2,
        col=1,
    )

    fig.update_layout(
        title=title or "Data-centre demand and national renewable context",
        legend_title_text="Country",
        hovermode="x",
    )

    return _style(fig, height=650)


def constant_panel_chart(df, years=(2022, 2023, 2024)):
    _check_columns(df, "geo", "year", "dc_gwh")

    selected = df.loc[df["year"].isin(years)].copy()

    if selected.duplicated(["geo", "year"]).any():
        raise ValueError("Each country and year must appear only once.")

    complete = selected.dropna(subset=["dc_gwh"])

    eligible = (
        complete.groupby("geo")["year"]
        .nunique()
        .loc[lambda counts: counts == len(years)]
        .index
    )

    panel = complete.loc[complete["geo"].isin(eligible)].copy()

    if panel.empty:
        raise ValueError("No countries have published values for every year.")

    totals = (
        panel.groupby("year", as_index=False)["dc_gwh"]
        .sum()
        .sort_values("year")
    )

    fig = px.line(
        totals,
        x="year",
        y="dc_gwh",
        markers=True,
        title=f"Same {len(eligible)} reporting countries, {years[0]}–{years[-1]}",
        labels={
            "year": "Year",
            "dc_gwh": "Reported data-centre consumption (GWh)",
        },
    )

    fig.update_traces(
        line=dict(color=BLUE, width=4),
        marker=dict(size=11),
        hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>",
    )
    fig.update_xaxes(tickmode="array", tickvals=list(years))
    fig.update_yaxes(rangemode="tozero")

    return _style(fig, height=430), panel, totals


def country_energy_timeline(df, country):
    _check_columns(
        df,
        "geo",
        "year",
        "dc_gwh",
        "renewable_share_pct",
    )

    data = (
        df.loc[df["geo"] == country]
        .sort_values("year")
        .copy()
    )

    if data.empty or data["dc_gwh"].notna().sum() < 2:
        raise ValueError(
            "At least two published data-centre values are required."
        )

    years = sorted(data["year"].dropna().unique().tolist())

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.13,
        subplot_titles=(
            "Data-centre electricity consumption",
            "National renewable electricity share",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=data["year"],
            y=data["dc_gwh"],
            mode="lines+markers",
            name="Data centres",
            line=dict(color=BLUE, width=3),
            marker=dict(size=9),
            connectgaps=False,
            hovertemplate=(
                "Year: %{x}<br>"
                "Data centres: %{y:,.1f} GWh"
                "<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=data["year"],
            y=data["renewable_share_pct"],
            mode="lines+markers",
            name="National renewables",
            line=dict(color=TEAL, width=3),
            marker=dict(size=9),
            connectgaps=False,
            hovertemplate=(
                "Year: %{x}<br>"
                "National renewable share: %{y:.2f}%"
                "<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )

    fig.update_yaxes(
        title_text="GWh",
        rangemode="tozero",
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title_text="%",
        rangemode="tozero",
        row=2,
        col=1,
    )
    fig.update_xaxes(
        title_text="Year",
        tickmode="array",
        tickvals=years,
        row=2,
        col=1,
    )
    fig.update_layout(
        title=f"Electricity demand and renewable context — {country}",
        showlegend=False,
        hovermode="x",
    )

    return _style(fig, height=620)

def country_growth_chart(df, years=(2022, 2023, 2024)):
    _check_columns(df, "geo", "year", "dc_gwh")

    years = tuple(sorted(years))
    data = df.loc[df["year"].isin(years), ["geo", "year", "dc_gwh"]].copy()

    if data.duplicated(["geo", "year"]).any():
        raise ValueError("Each country and year must appear only once.")

    published = data.dropna(subset=["dc_gwh"])

    complete_countries = (
        published.groupby("geo")["year"]
        .nunique()
        .loc[lambda counts: counts == len(years)]
        .index
    )

    complete = published.loc[
        published["geo"].isin(complete_countries)
    ].copy()

    baseline = (
        complete.loc[complete["year"] == years[0], ["geo", "dc_gwh"]]
        .rename(columns={"dc_gwh": "baseline_gwh"})
    )

    complete = complete.merge(
        baseline,
        on="geo",
        validate="many_to_one",
    )

    excluded = sorted(
        complete.loc[complete["baseline_gwh"] <= 0, "geo"]
        .unique()
        .tolist()
    )

    indexed = complete.loc[complete["baseline_gwh"] > 0].copy()

    if indexed.empty:
        raise ValueError(
            "No country has a positive baseline and complete published data."
        )

    indexed["index_2022"] = (
        indexed["dc_gwh"] / indexed["baseline_gwh"] * 100
    )

    indexed = indexed.sort_values(["geo", "year"])

    fig = px.line(
        indexed,
        x="year",
        y="index_2022",
        color="geo",
        markers=True,
        custom_data=["dc_gwh"],
        labels={
            "year": "Year",
            "index_2022": f"Index ({years[0]} = 100)",
            "geo": "Country",
        },
        title="How did demand change across reporting countries?",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Index: %{y:.1f}<br>"
            "Consumption: %{customdata[0]:,.1f} GWh"
            "<extra></extra>"
        ),
        line=dict(width=2),
        marker=dict(size=7),
    )

    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="#94a3b8",
    )

    fig.update_xaxes(tickmode="array", tickvals=list(years))
    fig.update_layout(
        hovermode="closest",
        legend_title_text="Country",
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0,
        ),
    )

    return _style(fig, height=590), indexed, excluded

def country_growth_ranking_chart(df):
    _, indexed, excluded = country_growth_chart(df)

    first_year = int(indexed["year"].min())
    last_year = int(indexed["year"].max())

    start = indexed.loc[
        indexed["year"] == first_year,
        ["geo", "dc_gwh"],
    ].rename(columns={"dc_gwh": "start_gwh"})

    end = indexed.loc[
        indexed["year"] == last_year,
        ["geo", "dc_gwh"],
    ].rename(columns={"dc_gwh": "end_gwh"})

    data = start.merge(end, on="geo", validate="one_to_one")

    data["change_pct"] = (
        data["end_gwh"] / data["start_gwh"] - 1
    ) * 100

    country_names = {
        "AT": "Austria",
        "BE": "Belgium",
        "DE": "Germany",
        "FR": "France",
        "IE": "Ireland",
        "MD": "Moldova",
        "ME": "Montenegro",
        "NL": "Netherlands",
        "NO": "Norway",
        "PT": "Portugal",
        "SE": "Sweden",
    }

    data["country"] = data["geo"].map(country_names).fillna(
        data["geo"]
    )
    data["direction"] = data["change_pct"].apply(
        lambda value: "Increase" if value >= 0 else "Decrease"
    )
    data = data.sort_values("change_pct")

    fig = px.bar(
        data,
        x="change_pct",
        y="country",
        orientation="h",
        color="direction",
        color_discrete_map={
            "Increase": TEAL,
            "Decrease": ORANGE,
        },
        custom_data=["start_gwh", "end_gwh"],
        labels={
            "change_pct": f"Change from {first_year} to {last_year} (%)",
            "country": "Country",
        },
        title=f"How did consumption change from {first_year} to {last_year}?",
    )

    fig.update_traces(
        texttemplate="%{x:+.0f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Country: %{y}<br>"
            "Change: %{x:+.1f}%<br>"
            f"{first_year}: %{{customdata[0]:,.1f}} GWh<br>"
            f"{last_year}: %{{customdata[1]:,.1f}} GWh"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        showlegend=False,
        yaxis_title=None,
        bargap=0.28,
        margin=dict(l=125, r=75, t=55, b=45),
    )

    fig.update_xaxes(
        zeroline=True,
        zerolinecolor="#64748b",
    )

    return _style(fig, height=440), data, excluded


def energy_context_scatter_chart(df):
    _check_columns(
        df,
        "geo",
        "year",
        "dc_gwh",
        "dc_share_pct",
        "renewable_share_pct",
    )

    data = df.loc[
        df["year"].eq(2024),
        [
            "geo",
            "dc_gwh",
            "dc_share_pct",
            "renewable_share_pct",
        ],
    ].dropna().copy()

    if data.empty:
        raise ValueError(
            "No countries have all three indicators in 2024."
        )

    data = data.loc[data["dc_gwh"].ge(0)]

    fig = px.scatter(
        data,
        x="dc_share_pct",
        y="renewable_share_pct",
        size="dc_gwh",
        size_max=48,
        hover_name="geo",
        hover_data={
            "dc_share_pct": ":.2f",
            "renewable_share_pct": ":.1f",
            "dc_gwh": ":,.1f",
        },
        labels={
            "dc_share_pct": "Data-centre share of final electricity (%)",
            "renewable_share_pct": "National renewable electricity share (%)",
            "dc_gwh": "Data-centre consumption (GWh)",
        },
        title="Different demand, different renewable contexts — 2024",
    )

    fig.update_traces(
        marker=dict(
            color=TEAL,
            opacity=0.75,
            line=dict(color="white", width=1),
        )
    )

    return _style(fig, height=530), data


def demand_renewables_change_chart(df):
    _check_columns(
        df,
        "geo",
        "year",
        "dc_gwh",
        "dc_share_pct",
        "renewable_share_pct",
    )

    years = (2022, 2024)

    data = df.loc[
        df["year"].isin(years),
        [
            "geo",
            "year",
            "dc_gwh",
            "dc_share_pct",
            "renewable_share_pct",
        ],
    ].dropna().copy()

    data = data.loc[data["dc_gwh"].gt(0)]

    wide = data.pivot(
        index="geo",
        columns="year",
        values=["dc_share_pct", "renewable_share_pct"],
    )

    required = [
        ("dc_share_pct", 2022),
        ("dc_share_pct", 2024),
        ("renewable_share_pct", 2022),
        ("renewable_share_pct", 2024),
    ]

    if not all(column in wide.columns for column in required):
        raise ValueError(
            "The 2022 and 2024 indicators cannot be compared."
        )

    wide = wide.dropna(subset=required)

    if wide.empty:
        raise ValueError(
            "No countries have comparable data in 2022 and 2024."
        )

    changes = pd.DataFrame({
        "geo": wide.index,
        "dc_change_pp": (
            wide[("dc_share_pct", 2024)]
            - wide[("dc_share_pct", 2022)]
        ).to_numpy(),
        "renewable_change_pp": (
            wide[("renewable_share_pct", 2024)]
            - wide[("renewable_share_pct", 2022)]
        ).to_numpy(),
    })

    fig = px.scatter(
        changes,
        x="dc_change_pp",
        y="renewable_change_pp",
        hover_name="geo",
        hover_data={
            "dc_change_pp": ":+.2f",
            "renewable_change_pp": ":+.2f",
        },
        labels={
            "dc_change_pp": (
                "Change in data-centre national share "
                "(percentage points)"
            ),
            "renewable_change_pp": (
                "Change in national renewable share "
                "(percentage points)"
            ),
        },
        title="How did demand and renewable shares change? 2022–2024",
    )

    fig.update_traces(
        marker=dict(
            size=13,
            color=BLUE,
            opacity=0.85,
        )
    )

    fig.add_vline(
        x=0,
        line_color="#94a3b8",
        line_dash="dash",
    )

    fig.add_hline(
        y=0,
        line_color="#94a3b8",
        line_dash="dash",
    )

    return _style(fig, height=530), changes


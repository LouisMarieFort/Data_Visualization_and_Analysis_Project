import pandas as pd


YEARS = range(2020, 2025)


def _select_series(df: pd.DataFrame, filters, value_name, keep_flags = False,):
    required = {"geo", "TIME_PERIOD", "OBS_VALUE", *filters.keys()}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes pour {value_name} : {sorted(missing)}")

    selected = df.copy()
    for column, expected in filters.items():
        selected = selected.loc[selected[column] == expected]

    selected = selected.copy()
    selected["year"] = pd.to_numeric(
        selected["TIME_PERIOD"], errors="coerce"
    )
    selected = selected.loc[selected["year"].isin(YEARS)]

    if selected.empty:
        raise ValueError(
            f"Aucune observation trouvée pour {value_name} "
            f"avec les filtres {filters}"
        )

    selected[value_name] = pd.to_numeric(
        selected["OBS_VALUE"], errors="coerce"
    )

    columns = ["geo", "year", value_name]
    if keep_flags:
        columns += [col for col in ("OBS_FLAG", "CONF_STATUS")
                    if col in selected.columns]

    selected = selected[columns].copy()
    selected["year"] = selected["year"].astype(int)

    if selected.duplicated(["geo", "year"]).any():
        raise ValueError(
            f"Doublons pays–année dans {value_name} : "
            "vérifie les dimensions et les filtres."
        )

    return selected


def make_tables(raw: dict):
    dc = _select_series(
        raw["datacenters"]["Sheet1"],
        {"freq": "A", "unit": "GWH", "siec": "E7000",
         "nace_r2": "DATAC"},
        "dc_gwh",
        keep_flags=True,
    )

    electricity = _select_series(
        raw["electricity"]["Sheet1"],
        {"freq": "A", "nrg_bal": "FC", "siec": "E7000",
         "unit": "GWH"},
        "electricity_gwh",
    )

    renewables = _select_series(
        raw["renewables"]["Sheet1"],
        {"freq": "A", "nrg_bal": "REN_ELC", "unit": "PC"},
        "renewable_share_pct",
    )

    merged = dc.merge(
        electricity, on=["geo", "year"], how="left", validate="one_to_one"
    ).merge(
        renewables, on=["geo", "year"], how="left", validate="one_to_one"
    )

    valid_denominator = merged["electricity_gwh"] > 0
    merged["dc_share_pct"] = (
        merged["dc_gwh"]
        .div(merged["electricity_gwh"].where(valid_denominator))
        .mul(100)
    )

    return {
        "datacenters": dc,
        "electricity": electricity,
        "renewables": renewables,
        "merged": merged,
    }

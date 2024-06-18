""" Clean version for EUSS v1.0 dataset 
updated: 05/22/24
Predictive capacity models:
5bins:
  - 133310: Elec only, standard bins
  - 231606: Non-elec only, standard bins
7bins:
  - 134078: Elec only, seven bins
  - 238518: Non-elec only, seven bins
"""
from pathlib import Path
import argparse
import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import itertools


def load_model(model_file: Path, feature_names: list[str] | None = None):
    model = pickle.load(open(model_file, "rb"))
    # model.get_params()

    model.feature_names = model.get_booster().feature_names
    if model.feature_names is None and feature_names is not None:
        model.feature_names = feature_names

    assert set(model.classes_) == set(
        output_mapping.keys()
    ), f"mismatch between model.classes_ and output_mapping: \n{model.classes_} vs. {output_mapping.keys()}"

    return model

def yield_floor_area_dataframe():
    # https://github.com/NREL/resstock/blob/develop/measures/ResStockArguments/measure.rb
    df_fa = pd.DataFrame(
        data=[
            ("0-499", "Mobile Home", 298),
            ("0-499", "Single-Family Detached", 298),
            ("0-499", "Single-Family Attached", 273),
            ("0-499", "Multi-Family with 2 - 4 Units", 322),
            ("0-499", "Multi-Family with 5+ Units", 322),
            ("500-749", "Mobile Home", 634),
            ("500-749", "Single-Family Detached", 634),
            ("500-749", "Single-Family Attached", 625),
            ("500-749", "Multi-Family with 2 - 4 Units", 623),
            ("500-749", "Multi-Family with 5+ Units", 623),
            ("750-999", "Mobile Home", 881),
            ("750-999", "Single-Family Detached", 881),
            ("750-999", "Single-Family Attached", 872),
            ("750-999", "Multi-Family with 2 - 4 Units", 854),
            ("750-999", "Multi-Family with 5+ Units", 854),
            ("1000-1499", "Mobile Home", 1228),
            ("1000-1499", "Single-Family Detached", 1228),
            ("1000-1499", "Single-Family Attached", 1207),
            ("1000-1499", "Multi-Family with 2 - 4 Units", 1138),
            ("1000-1499", "Multi-Family with 5+ Units", 1138),
            ("1500-1999", "Mobile Home", 1698),
            ("1500-1999", "Single-Family Detached", 1698),
            ("1500-1999", "Single-Family Attached", 1678),
            ("1500-1999", "Multi-Family with 2 - 4 Units", 1682),
            ("1500-1999", "Multi-Family with 5+ Units", 1682),
            ("2000-2499", "Mobile Home", 2179),
            ("2000-2499", "Single-Family Detached", 2179),
            ("2000-2499", "Single-Family Attached", 2152),
            ("2000-2499", "Multi-Family with 2 - 4 Units", 2115),
            ("2000-2499", "Multi-Family with 5+ Units", 2115),
            ("2500-2999", "Mobile Home", 2678),
            ("2500-2999", "Single-Family Detached", 2678),
            ("2500-2999", "Single-Family Attached", 2663),
            ("2500-2999", "Multi-Family with 2 - 4 Units", 2648),
            ("2500-2999", "Multi-Family with 5+ Units", 2648),
            ("3000-3999", "Mobile Home", 3310),
            ("3000-3999", "Single-Family Detached", 3310),
            ("3000-3999", "Single-Family Attached", 3228),
            ("3000-3999", "Multi-Family with 2 - 4 Units", 3171),
            ("3000-3999", "Multi-Family with 5+ Units", 3171),
            ("4000+", "Mobile Home", 5587),
            ("4000+", "Single-Family Detached", 5587),
            ("4000+", "Single-Family Attached", 7414),
            ("4000+", "Multi-Family with 2 - 4 Units", 6348),
            ("4000+", "Multi-Family with 5+ Units", 6348),
        ],
        columns=["Geometry Floor Area", "Geometry Building Type RECS", "sqft"],
    )
    return df_fa

def yield_input_options(hc_list=None):
    input_options = {
        "Geometry Floor Area": [
            "0-499",
            "500-749",
            "750-999",
            "1000-1499",
            "1500-1999",
            "2000-2499",
            "2500-2999",
            "3000-3999",
            "4000+",
        ],
        "Geometry Building Type RECS": [
            "Mobile Home",
            "Multi-Family with 2 - 4 Units",
            "Multi-Family with 5+ Units",
            "Single-Family Attached",
            "Single-Family Detached",
        ], # SFA and SFD combined for ne models
        "Vintage": [
            "<1940",
            "1940s",
            "1950s",
            "1960s",
            "1970s",
            "1980s",
            "1990s",
            "2000s",
            "2010s",
            "2020s",
        ],  # We do not have 2020s yet
        "HVAC Cooling Type": ["Central AC", "Heat Pump", "None", "Room AC"],  # old
        "Has PV": ["No", "Yes"],
        "Clothes Dryer": [
            "Electric, 80% Usage",
            "Gas, 80% Usage",
            "Propane, 80% Usage",
            "Electric, 100% Usage",
            "Gas, 100% Usage",
            "Propane, 100% Usage",
            "Electric, 120% Usage",
            "Gas, 120% Usage",
            "Propane, 120% Usage",
            "None",
        ],  # old # has special_mapping
        "Water Heater Fuel": [
            "Electricity",
            "Fuel Oil",
            "Natural Gas",
            "Other Fuel",
            "Propane",
        ],  # has special_mapping
        "Cooking Range": [
            "Electric, 80% Usage",
            "Gas, 80% Usage",
            "Propane, 80% Usage",
            "Electric, 100% Usage",
            "Gas, 100% Usage",
            "Propane, 100% Usage",
            "Electric, 120% Usage",
            "Gas, 120% Usage",
            "Propane, 120% Usage",
            "None",
        ],  # old # has special_mapping
    }

    if hc_list is None:
        return input_options

    return {k: v for k, v in input_options.items() if k in hc_list}


def create_input_tsv(
    model_e, model_ne, dummy_file_e: Path, dummy_file_ne: Path, tsv_file: Path
) -> pd.DataFrame:
    """Create input tsv from model,
    Missing fields are handled by duplicating predictions from fields that are similar to the missing fields
    E.g., fuel oil and other fuels is copied from the combined results of non-electric fuels

    model : XGBoost model

    """
    print("\nTransforming model into a ResStock input tsv file ...")
    ## create intermediate tsv
    df_e = create_input_tsv_electric(model_e, dummy_file_e) # n = 1,620,000
    df_ne = create_input_tsv_nonelectric(model_ne, dummy_file_ne) # n = 405

    ## combine
    print("\n-- Combining intermediate tsvs together -- ")
    # add missing deps to df_ne ["HVAC Cooling Type", "Has PV", "Clothes Dryer", "Water Heater Fuel", "Cooking Range"]
    input_options = yield_input_options(hc_list=None)
    input_options["Vintage"].remove("2020s")
    df_ne2 = pd.DataFrame(
        data=itertools.product(*input_options.values()), columns=input_options.keys()
    )
    deps = [f"Dependency={x}" for x in df_ne2.columns]
    df_ne2.columns = deps
    df_ne2 = df_ne2.sort_values(by=deps).reset_index(drop=True)
    joint_deps = ["Geometry Floor Area", "Geometry Building Type RECS", "Vintage"]
    joint_deps = [f"Dependency={x}" for x in joint_deps]
    df_ne2 = pd.merge(df_ne2, df_ne, how="left", on=joint_deps)

    # QC
    diff = df_e[deps].sort_values(by=deps).compare(df_ne2[deps])
    if len(diff) > 0:
        print("df_e and df_ne2 do not have the same dep rows")
        breakpoint()
    
    opts = [x for x in df_ne2.columns if "Option=" in x]
    if (df_ne2[opts].sum(axis=1).round(1) != 1).sum() > 0:
        print("Error in duplicating rows in df_ne2 for missing dependencies")
        breakpoint()
    del df_ne

    # combine dfs
    df_e["Dependency=Heating Fuel"] = "Electricity"

    fuels = [
        "Fuel Oil",
        "Natural Gas",
        "Other Fuel",
        "Propane",
        "None",
        ] # old, missing wood
    df = [df_e]
    for fuel in fuels:
        df_ne22 = df_ne2.copy()
        df_ne22["Dependency=Heating Fuel"] = fuel
        df.append(df_ne22)

    df = pd.concat(df, axis=0)
    cols = sorted(df.columns)
    df = df[cols]

    # QC
    n_rows = 1620000*6
    assert len(df) == n_rows, f"final tsv does not have the expected number of rows: {n_rows}"
    if (df[opts].sum(axis=1).round(1).sum() != len(df)) or ((df[opts].sum(axis=1).round(1) != 1).sum() > 0):
        print("Error in duplicating rows in df_ne2 for missing dependencies")
        breakpoint()

    ## -- save to tsv file --
    df.to_csv(tsv_file, sep="\t", index=False, lineterminator="\r\n")
    print(f"** Electrical Panel Amp TSV exported to: {tsv_file}")


def create_input_tsv_electric(model, dummy_file):

    print("\n-- Intermediate tsv for ELECTRIC heating fuel -- ")
    ## -- process data to align with model inputs --
    input_options = yield_input_options(hc_list=None)

    df_fa = yield_floor_area_dataframe()
    df = pd.DataFrame(
        data=itertools.product(*input_options.values()), columns=input_options.keys()
    )

    dfi = df.merge(df_fa, on=["Geometry Floor Area", "Geometry Building Type RECS"])

    expected_missing_cols = {}
    input_cols_map = {
        "sqft": "sqft",  # numeric
        "Geometry Building Type RECS": "geometry_building_type_recs",
        "Vintage": "vintage",
        "HVAC Cooling Type": "hvac_cooling_type",
        "Has PV": "has_pv",
        "Clothes Dryer": "clothes_dryer_simp",
        "Water Heater Fuel": "water_heater_fuel_simp",
        "Cooking Range": "cooking_range_simp",
    }
    expected_missing_cols_ne = {}

    categorical_columns = list(input_cols_map.values())[1:]

    dfi = dfi[input_cols_map.keys()].rename(columns=input_cols_map)

    # special mapping for heating fuels:
    dfi = apply_special_mapping(dfi, "electric")

    dfi = pd.get_dummies(dfi, columns=categorical_columns, prefix_sep="__")
    delta = set(dfi.columns) - set(model.feature_names)
    if len(delta) != 0:
        if delta != expected_missing_cols:
            print(f"Expecting missing cols from model input data: {expected_missing_cols} ")
            print(f"but found these missing cols instead: {delta}")
            breakpoint()

        assert delta == expected_missing_cols, (
            f"Expecting missing cols from model input data: {expected_missing_cols}, "
            f"but found these missing cols instead: {delta}"
        )
    # add any missing cols
    for col in model.feature_names:
        if col not in dfi.columns:
            print(f" - adding dummy encoding column to df: {col}")
            dfi[col] = 0

    ## -- predict --
    panel_prob = model.predict_proba(dfi[model.feature_names])
    panel_labels = [f"Option={output_mapping[x]}" for x in model.classes_]

    ## -- combine --
    df = df.rename(columns=lambda x: f"Dependency={x}")
    dep_cols = df.columns.tolist()
    df[panel_labels] = panel_prob

    # df.to_csv(data_dir / "panel_1.csv") # TODO

    # [1] Combine bins
    # [1.1] Vintage: combine 2010s and 2020s into 2010s, use LBNL data to inform prevalence of 2010s vs. 2020s
    dfd = pd.read_csv(dummy_file, header=0).iloc[:, :-2]

    p2010s = dfd["vintage__2010s"].sum() / (
        dfd["vintage__2010s"].sum() + dfd["vintage__2020s"].sum()
    )
    df["weight"] = 1.0
    df.loc[df["Dependency=Vintage"] == "2010s", "weight"] = p2010s
    df.loc[df["Dependency=Vintage"] == "2020s", "weight"] = 1 - p2010s
    df.loc[df["Dependency=Vintage"] == "2020s", "Dependency=Vintage"] = "2010s"

    df[panel_labels] = df[panel_labels].mul(df["weight"], axis=0)
    df = df.groupby(dep_cols)[panel_labels].sum().reset_index()

    if (df[panel_labels].sum(axis=1).round(1) != 1).sum() > 0:
        print("Error in combining rows for Vintage")
        breakpoint()

    # df.to_csv(data_dir / "panel_2_after_vintage.csv") # TODO
    del dfd

    if (df[panel_labels].sum(axis=1).round(1) != 1).sum() > 0:
        print("Error in combining/duplicating rows for Electrical Panel Amp.tsv")
        breakpoint()

    # renormalize all probs so sum is closer to 1
    df[panel_labels] = df[panel_labels].div(df[panel_labels].sum(axis=1), axis=0).round(6)

    # save intermediate tsv    
    tsv_file = data_dir / f"intermediate_amp_electric - Model {model.model_num} - EUSS RR1.tsv"
    df.to_csv(tsv_file, sep="\t", index=False, lineterminator="\r\n")

    return df

def create_input_tsv_nonelectric(model, dummy_file):

    print("\n-- Intermediate tsv for NON-ELECTRIC heating fuel --")
    ## -- process data to align with model inputs --
    hc_list=["Geometry Floor Area", "Geometry Building Type RECS", "Vintage"]
    input_options = yield_input_options(hc_list=hc_list)

    df_fa = yield_floor_area_dataframe()
    df = pd.DataFrame(
        data=itertools.product(*input_options.values()), columns=input_options.keys()
    )

    dfi = df.merge(df_fa, on=["Geometry Floor Area", "Geometry Building Type RECS"])

    input_cols_map = {
        "sqft": "sqft",  # numeric
        "Geometry Building Type RECS": "geometry_building_type_recs_simp",
        "Vintage": "vintage",
    }
    expected_missing_cols = {}

    categorical_columns = list(input_cols_map.values())[1:]

    dfi = dfi[input_cols_map.keys()].rename(columns=input_cols_map)

    # special mapping for heating fuels:
    dfi = apply_special_mapping(dfi, "non_electric")

    dfi = pd.get_dummies(dfi, columns=categorical_columns, prefix_sep="__")
    delta = set(dfi.columns) - set(model.feature_names)
    if len(delta) != 0:
        if delta != expected_missing_cols:
            print(f"Expecting missing cols from model input data: {expected_missing_cols} ")
            print(f"but found these missing cols instead: {delta}")
            breakpoint()

        assert delta == expected_missing_cols, (
            f"Expecting missing cols from model input data: {expected_missing_cols}, "
            f"but found these missing cols instead: {delta}"
        )
    # add any missing cols
    for col in model.feature_names:
        if col not in dfi.columns:
            print(f" - adding dummy encoding column to df: {col}")
            dfi[col] = 0

    ## -- predict --
    panel_prob = model.predict_proba(dfi[model.feature_names])
    panel_labels = [f"Option={output_mapping[x]}" for x in model.classes_]

    ## -- combine --
    df = df.rename(columns=lambda x: f"Dependency={x}")
    dep_cols = df.columns.tolist()
    df[panel_labels] = panel_prob

    # df.to_csv(data_dir / "panel_1.csv") # TODO

    # [1] Combine bins
    # [1.1] Vintage: combine 2010s and 2020s into 2010s, use LBNL data to inform prevalence of 2010s vs. 2020s
    dfd = pd.read_csv(dummy_file, header=0).iloc[:, :-2]

    p2010s = dfd["vintage__2010s"].sum() / (
        dfd["vintage__2010s"].sum() + dfd["vintage__2020s"].sum()
    )
    df["weight"] = 1.0
    df.loc[df["Dependency=Vintage"] == "2010s", "weight"] = p2010s
    df.loc[df["Dependency=Vintage"] == "2020s", "weight"] = 1 - p2010s
    df.loc[df["Dependency=Vintage"] == "2020s", "Dependency=Vintage"] = "2010s"

    df[panel_labels] = df[panel_labels].mul(df["weight"], axis=0)
    df = df.groupby(dep_cols)[panel_labels].sum().reset_index()

    if (df[panel_labels].sum(axis=1).round(1) != 1).sum() > 0:
        print("Error in combining rows for Vintage")
        breakpoint()

    # df.to_csv(data_dir / "panel_2_after_vintage.csv") # TODO
    del dfd

    if (df[panel_labels].sum(axis=1).round(1) != 1).sum() > 0:
        print("Error in combining/duplicating rows for Electrical Panel Amp.tsv")
        breakpoint()

    # renormalize all probs so sum is closer to 1
    df[panel_labels] = df[panel_labels].div(df[panel_labels].sum(axis=1), axis=0).round(6)

    # save intermediate tsv    
    tsv_file = data_dir / f"intermediate_amp_nonelectric - Model {model.model_num} - EUSS RR1.tsv"
    df.to_csv(tsv_file, sep="\t", index=False, lineterminator="\r\n")

    return df

def undummify_input_data(df: pd.DataFrame, input_options: dict) -> pd.DataFrame:
    # undummy categorical columns
    cat_cols = [x for x in df.columns if x not in ["sqft", "dummy"]]
    dfd = undummify(df[cat_cols])

    # bin sqft
    para = "geometry_floor_area"
    bins = input_options["Geometry Floor Area"]
    bin_edges = [int(x.split("-")[0].split("+")[0]) for x in bins]
    dfd.loc[df["sqft"] >= bin_edges[-1], para] = bins[-1]
    for edge, label in zip(reversed(bin_edges[1:]), reversed(bins[:-1])):
        dfd.loc[df["sqft"] < edge, para] = label

    # remove "dummy" col - nothing to do

    return dfd


def undummify(df: pd.DataFrame, prefix_sep: str = "__") -> pd.DataFrame:
    cols2collapse = {
        item.split(prefix_sep)[0]: (prefix_sep in item) for item in df.columns
    }
    series_list = []
    for col, needs_to_collapse in cols2collapse.items():
        if needs_to_collapse:
            undummified = (
                df.filter(like=col)
                .idxmax(axis=1)
                .apply(lambda x: x.split(prefix_sep, maxsplit=1)[1])
                .rename(col)
            )
            series_list.append(undummified)
        else:
            series_list.append(df[col])
    undummified_df = pd.concat(series_list, axis=1)

    return undummified_df


def apply_special_mapping(dfi: pd.DataFrame, model_type: str) -> pd.DataFrame:
    """ translate resstock options to model input options """
    if model_type == "non_electric":
        dfi["geometry_building_type_recs_simp"] = dfi["geometry_building_type_recs_simp"].map(
            {
                "Mobile Home": "Mobile Home",
                "Multi-Family with 2 - 4 Units": "Multi-Family with 2 - 4 Units",
                "Multi-Family with 5+ Units": "Multi-Family with 5+ Units",
                "Single-Family Attached": "Single-Family",
                "Single-Family Detached": "Single-Family",
            }
        )

    dfi["vintage"] = dfi["vintage"].map(
        dict(
            zip(
                [
                    "<1940",
                    "1940s",
                    "1950s",
                    "1960s",
                    "1970s",
                    "1980s",
                    "1990s",
                    "2000s",
                    "2010s",
                    "2020s",
                ],
                [
                    "lt_1940",
                    "1940s",
                    "1950s",
                    "1960s",
                    "1970s",
                    "1980s",
                    "1990s",
                    "2000s",
                    "2010s",
                    "2020s",
                ],
            )
        )
    )
    if model_type == "electric":
        dfi["water_heater_fuel_simp"] = dfi["water_heater_fuel_simp"].map(
            {
                "Electricity": "Electricity",
                "Fuel Oil": "non_Electricity",
                "Natural Gas": "non_Electricity",
                "Other Fuel": "non_Electricity",
                "Propane": "non_Electricity",
            }
        )
        appliance_usage_map = {
            "Electric, 80% Usage": "Electric, 100% Usage",
            "Gas, 80% Usage": "non_Electricity",
            "Propane, 80% Usage": "non_Electricity",
            "Electric, 100% Usage": "Electric, 100% Usage",
            "Gas, 100% Usage": "non_Electricity",
            "Propane, 100% Usage": "non_Electricity",
            "Electric, 120% Usage": "Electric, 100% Usage",
            "Gas, 120% Usage": "non_Electricity",
            "Propane, 120% Usage": "non_Electricity",
            "None": "None",
        }

        dfi["clothes_dryer_simp"] = dfi["clothes_dryer_simp"].map(appliance_usage_map)
        dfi["cooking_range_simp"] = dfi["cooking_range_simp"].map(appliance_usage_map)
    return dfi


def apply_tsv_to_results(
    df: pd.DataFrame, tsv_file: Path, retain_proba: bool = False
) -> pd.DataFrame:
    """Apply tsv (derived from model) to ResStock result dataframe
    Args :
        df : pd.DataFrame
            dataframe of ResStock results_up00 file
        tsv_file : Path
            path to tsv_file
        retain_proba : bool
            if True, predicted output value is a distribution of output labels instead of a single label
            if False, predicted output value is a single label probablistically chosen based on output distribution
    """
    tsv = pd.read_csv(tsv_file, delimiter="\t", keep_default_na=False)

    dep_cols = [x for x in tsv.columns if x.startswith("Dependency=")]
    res_cols = [
        "build_existing_model."
        + x.removeprefix("Dependency=").lower().replace(" ", "_")
        for x in dep_cols
    ]
    option_cols = [x for x in tsv.columns if x.startswith("Option=")]
    panel_labels = [x.removeprefix("Option=") for x in option_cols]

    dff = df[res_cols].join(
        tsv.rename(
            columns=dict(zip(dep_cols + option_cols, res_cols + panel_labels))
        ).set_index(res_cols)[panel_labels],
        on=res_cols,
        how="left",
    )

    cond = df["completed_status"] == "Success"
    if dff.loc[cond, panel_labels].isna().sum().sum() != 0:
        print(f"Prediction in apply_tsv_to_results has NA values {dff.loc[cond & (dff[panel_labels].isna().sum(axis=1)!=0)]}")
        error_file = output_filedir / "error_panel_result.csv"
        print(f"A copy of the data is exported for review to {error_file}")
        dff.to_csv(error_file, index=False)
        breakpoint()

    if retain_proba:
        return pd.concat([df, dff[panel_labels]], axis=1)

    # random draw according to probability
    panel_prob_cum = np.cumsum(dff[panel_labels].values, axis=1)
    random_nums_uniform = np.random.default_rng(seed=8).uniform(0, 1, size=len(dff))
    panel_amp = np.array(
        [
            np.array(panel_labels)[num <= arr][0] if not np.isnan(arr.sum()) else np.nan
            for num, arr in zip(random_nums_uniform, panel_prob_cum)
        ]
    )
    panel_amp = pd.Series(panel_amp, index=dff.index).rename("predicted_panel_amp_bin")
    df_panel = pd.concat([df, panel_amp], axis=1)
    df_panel = panel_amp_unbin(df_panel)
    return df_panel

def panel_amp_unbin(df_panel):
    df_panel["predicted_panel_amp"] = df_panel["predicted_panel_amp_bin"]          
    df_panel.loc[(df_panel['predicted_panel_amp_bin'] == '<100') & (df_panel['build_existing_model.heating_fuel'] == 'Electricity'), "predicted_panel_amp"] = 90
    df_panel.loc[(df_panel['predicted_panel_amp_bin'] == '<100') & (df_panel['build_existing_model.heating_fuel'] != 'Electricity'), "predicted_panel_amp"] = 60
    df_panel.loc[df_panel['predicted_panel_amp_bin'] == '101-124', "predicted_panel_amp"] = 120
    df_panel.loc[df_panel['predicted_panel_amp_bin'] == '126-199', "predicted_panel_amp"] = 150
    df_panel.loc[(df_panel['predicted_panel_amp_bin'] == '201+') & (df_panel['build_existing_model.geometry_floor_area'].isin(['0-499','500-749', '750-999', '1000-1499','1500-1999','2000-2499','2500-2999'])), "predicted_panel_amp"] = 250
    df_panel.loc[(df_panel['predicted_panel_amp_bin'] == '201+') & (df_panel['build_existing_model.geometry_floor_area']== '3000-3999'), "predicted_panel_amp"] = 300
    df_panel.loc[(df_panel['predicted_panel_amp_bin'] == '201+') & (df_panel['build_existing_model.geometry_floor_area'] == '4000+'), "predicted_panel_amp"] = 400
    return df_panel

def extract_left_edge(val):
    # for sorting things like AMI
    if val is None:
        return np.nan
    if not isinstance(val, str):
        return val
    first = val[0]
    if first in ["<", ">"] or first.isdigit():
        vals = [
            int(x)
            for x in re.split("\-| |\%|\<|\+|\>|s|th|p|A|B|C| ", val)
            if re.match("\d", x)
        ]
        if len(vals) > 0:
            num = vals[0]
            if "<" in val:
                num -= 1
            if ">" in val:
                num += 1
            return num
    return val


def sort_index(df: pd.DataFrame, axis: str = "index", **kwargs) -> pd.DataFrame:
    """axis: ['index', 'columns']"""
    if axis in [0, "index"]:
        try:
            df = df.reindex(sorted(df.index, key=extract_left_edge, **kwargs))
        except TypeError:
            df = df.reindex(sorted(df.index, **kwargs))
        return df

    if axis in [1, "columns"]:
        col_index_name = df.columns.name
        try:
            cols = sorted(df.columns, key=extract_left_edge, **kwargs)
        except TypeError:
            cols = sorted(df.columns, **kwargs)
        df = df[cols]
        df.columns.name = col_index_name
        return df
    raise ValueError(f"axis={axis} is invalid")


def plot_output_saturation(
    df: pd.DataFrame, output_dir: Path, panel_metrics: list[str], sfd_only=False
):
    print(f"Plots output to: {output_dir}")
    cond = df["completed_status"] == "Success"
    if sfd_only:
        cond &= (
            df["build_existing_model.geometry_building_type_recs"]
            == "Single-Family Detached"
        )
        df = df.loc[cond]
        print(
            f"Plotting applies to {len(df)} valid Single-Family Detached samples only"
        )
    else:
        df = df.loc[cond]
        print(f"Plotting applies to {len(df)} valid samples only")

    for hc in [
        "build_existing_model.census_region",
        "build_existing_model.federal_poverty_level",
        "build_existing_model.area_median_income",
        "build_existing_model.geometry_floor_area_bin",
        "build_existing_model.geometry_building_type_recs",
        "build_existing_model.vintage",
    ]:
        _plot_bar(df, [hc], panel_metrics, output_dir=output_dir, sfd_only=sfd_only)

    for hc in [
        "build_existing_model.census_region",
        "build_existing_model.census_division",
        "build_existing_model.ashrae_iecc_climate_zone_2004",
        "build_existing_model.geometry_building_type_recs",  # dep
        "build_existing_model.state",
        "build_existing_model.vintage",  # dep
        "build_existing_model.vintage_acs",
        "build_existing_model.federal_poverty_level",
        "build_existing_model.area_median_income",
        "build_existing_model.tenure",
        "build_existing_model.geometry_floor_area_bin",
        "build_existing_model.geometry_floor_area",  # dep
        "build_existing_model.heating_fuel",  # dep
        "build_existing_model.water_heater_fuel",  # dep
        "build_existing_model.hvac_heating_type",
        "build_existing_model.hvac_cooling_type",  # dep
        "build_existing_model.has_pv", # dep
    ]:
        _plot_bar_stacked(df, [hc], panel_metrics, output_dir=output_dir, sfd_only=sfd_only)

    _plot_bar_stacked(
        df,
        ["build_existing_model.vintage", "build_existing_model.geometry_floor_area"],
        panel_metrics,
        output_dir=output_dir,
        sfd_only=sfd_only
    )
    _plot_bar_stacked(
        df,
        [
            "build_existing_model.census_region",
            "build_existing_model.geometry_building_type_recs",
        ],
        panel_metrics,
        output_dir=output_dir,
        sfd_only=sfd_only
    )


def _plot_bar(
    df: pd.DataFrame,
    groupby_cols: list[str],
    metric_cols: list[str],
    output_dir: Path | None = None,
    sfd_only: bool | None = None
):
    if sfd_only:
        dfi = df.loc[df["build_existing_model.geometry_building_type_recs"]=="Single-Family Detached"]
    else:
        dfi = df.copy()

    if "predicted_panel_amp_bin" in metric_cols:
        metric_cols = ["predicted_panel_amp_bin"]
        dfi = dfi[groupby_cols + metric_cols + ["building_id"]]
        dfi = dfi.groupby(groupby_cols + metric_cols)["building_id"].count().unstack()
    else:
        dfi = dfi.groupby(groupby_cols)[metric_cols].sum()
        metric_cols = ["predicted_panel_amp_expected_value"]
    dfi = sort_index(sort_index(dfi, axis=0), axis=1)

    fig, ax = plt.subplots()
    dfi.plot(kind="bar", ax=ax)
    if output_dir is not None:
        metric = "__by__".join(groupby_cols + metric_cols).replace("build_existing_model.", "")
        fig.savefig(output_dir / f"bar_{metric}.png", dpi=400, bbox_inches="tight")
        dfi.to_csv(output_dir / f"data__bar_{metric}.csv", index=True)
    plt.close()


def _plot_bar_stacked(
    df: pd.DataFrame,
    groupby_cols: list[str],
    metric_cols: list[str],
    output_dir: Path | None = None,
    sfd_only: bool | None = None
):
    if sfd_only:
        dfi = df.loc[df["build_existing_model.geometry_building_type_recs"]=="Single-Family Detached"]
    else:
        dfi = df.copy()

    if "predicted_panel_amp_bin" in metric_cols:
        metric_cols = ["predicted_panel_amp_bin"]
        dfi = dfi[groupby_cols + metric_cols + ["building_id"]]
        dfi = dfi.groupby(groupby_cols + metric_cols)["building_id"].count().unstack()
    else:
        dfi = dfi.groupby(groupby_cols)[metric_cols].sum()
        metric_cols = ["predicted_panel_amp_expected_value"]

    dfi = dfi.divide(dfi.sum(axis=1), axis=0)
    dfi = sort_index(sort_index(dfi, axis=0), axis=1)

    fig, ax = plt.subplots()
    dfi.plot(kind="bar", stacked=True, ax=ax)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    ax.set_title(f"Saturation of {metric_cols[0]}")
    if output_dir is not None:
        metric = "__by__".join(groupby_cols + metric_cols).replace("build_existing_model.", "")
        fig.savefig(
            output_dir / f"stacked_bar_{metric}.png", dpi=400, bbox_inches="tight"
        )
        dfi.to_csv(output_dir / f"data__stacked_bar_{metric[0]}.csv", index=True)
    plt.close()


def read_file(filename: str | Path, low_memory: bool = True, **kwargs) -> pd.DataFrame:
    """If file is large, use low_memory=False"""
    filename = Path(filename)
    if filename.suffix == ".csv":
        df = pd.read_csv(
            filename, low_memory=low_memory, keep_default_na=False, **kwargs
        )
    elif filename.suffix == ".parquet":
        df = pd.read_parquet(filename, **kwargs)
    else:
        raise TypeError(f"Unsupported file type, cannot read file: {filename}")
    return df


def get_model_parameters(model):
    
    if model == "5bins":
        model_file_e = "final_panel_model_rank_test_f1_weighted_133310.p"
        model_file_ne = "final_panel_model_rank_test_f1_weighted_231606.p"
        dummy_file_e = "train_data_with_continuous_panel_amp_133310.csv"
        dummy_file_ne = "train_data_with_continuous_panel_amp_231606.csv"
        output_mapping = {
            0: "100",
            1: "101-199",
            2: "200",
            3: "201+",
            4: "<100",  # "lt_100",
        }
    elif model == "7bins":
        # w/ simplified heating fuel
        model_file_e = "final_panel_model_rank_test_f1_weighted_134078.p"
        model_file_ne = "final_panel_model_rank_test_f1_weighted_238518.p"
        dummy_file_e = "train_data_with_continuous_panel_amp_134078.csv"
        dummy_file_ne = "train_data_with_continuous_panel_amp_238518.csv"
        output_mapping = {
            0: "100",
            1: "101-124",
            2: "125",
            3: "126-199",
            4: "200", 
            5: "201+",
            6: "<100",  # "lt_100",
        }
    else:
        raise ValueError(f"Unknown model={model}, valid: ['5bins', '7bins']")

    return [model_file_e, model_file_ne], [dummy_file_e, dummy_file_ne], output_mapping


def main(
    filename: str | None = None,
    retain_proba: bool = False,
    plot_only: bool = False,
    sfd_only: bool = False,
    export_result_as_map: bool = False,
):
    global local_dir, data_dir, output_filedir, output_mapping

    local_dir = Path(__file__).resolve().parent
    data_dir = local_dir / "model_20240517"

    if filename is None:
        filename = local_dir / "test_data" / "euss1_2018_results_up00_100.csv"
    else:
        filename = Path(filename)

    # Model specs
    model_num = "7bins"  # <-- [5bins, 7bins]
    model_files, dummy_files, output_mapping = get_model_parameters(model_num)

    model_file_e = data_dir / model_files[0]
    model_file_ne = data_dir / model_files[1]
    dummy_file_e = data_dir / dummy_files[0]
    dummy_file_ne = data_dir / dummy_files[1]
    tsv_file = data_dir / f"Electrical Panel Amp - Model {model_num} - EUSS RR1.tsv"

    msg = "Default: Probabilistic prediction based on distribution of labels"
    if retain_proba:
        msg = "Prediction as a distribution of labels"

    fp = "tsv_based"
    msg2 = "Prediction using tsv"
    msg3 = "Exporting prediction result by appending to input result file."
    if export_result_as_map:
        msg3 = "Exporting prediction result as a building_id map (lookup)."

    print(
        f"""
        ===============================================
        Predict panel capacity using MODEL {model_num}
        - {msg}
        - {msg2}
        - {msg3}
        ===============================================
        """
    )

    panel_metrics = ["predicted_panel_amp_bin", "predicted_panel_amp"]
    if retain_proba:
        panel_metrics = list(output_mapping.values())

    ext = f"model_{model_num}__{fp}__predicted_panels_probablistically_assigned"
    if retain_proba:
        ext = f"model_{model_num}__{fp}__predicted_panels_in_probability"

    output_filedir = filename.parent / "panel_capacity"
    output_filedir.mkdir(parents=True, exist_ok=True)
    output_filename = output_filedir / (filename.stem + "__" + ext + ".csv")
    plot_dir_name = "plots_sfd" if sfd_only else "plots"
    output_dir = filename.parent / plot_dir_name / ext
    output_dir.mkdir(parents=True, exist_ok=True)

    # If plotting only
    if plot_only:
        print(
            f"Plotting output {panel_metrics} only, using output_filename: {output_filename}"
        )
        if not output_filename.exists():
            raise FileNotFoundError(
                f"Cannot create plots, output_filename not found: {output_filename}, "
                "try running command without -p flag to create the file first"
            )
        df = pd.read_csv(output_filename, low_memory=False, keep_default_na=False)
        plot_output_saturation(df, output_dir, panel_metrics, sfd_only=sfd_only)
        sys.exit()

    # Prediction
    if not tsv_file.exists():
        # Load model
        feature_names = pd.read_csv(
            dummy_file_e, header=0, nrows=0
        ).columns.tolist()[:-2]
        model_e = load_model(model_file_e, feature_names)
        model_ne = load_model(model_file_ne, feature_names)
        model_e.model_num = model_num
        model_ne.model_num = model_num

        create_input_tsv(model_e, model_ne, dummy_file_e, dummy_file_ne, tsv_file=tsv_file)

    df = read_file(filename, low_memory=False)
    df = apply_tsv_to_results(df, tsv_file, retain_proba=retain_proba)

    ## -- export --
    if export_result_as_map:
        output_filename = output_filedir / ("panel_result__" + ext + ".csv")
        df[["building_id"]+panel_metrics].to_csv(output_filename, index=False)
    else:
        df.to_csv(output_filename, index=False)
    print(f"File output to: {output_filename}")

    ## -- plot --
    plot_output_saturation(df, output_dir, panel_metrics, sfd_only=sfd_only)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        action="store",
        default=None,
        nargs="?",
        help="Path to ResStock result file, e.g., results_up00.csv, "
        "defaults to test data: test_data/euss1_2018_results_up00_100.csv",
    )
    parser.add_argument(
        "-r",
        "--retain_proba",
        action="store_true",
        default=False,
        help="If true, output is retained as a probablistic distribution of all output labels "
        "and saturation plots give the expected saturation of output. "
        "Default is one output label per dwelling unit, PROBABLISTICALLY assigned.",
    )
    parser.add_argument(
        "-p",
        "--plot_only",
        action="store_true",
        default=False,
        help="Make plots only based on expected output file without regenerating output file",
    )
    parser.add_argument(
        "-d",
        "--sfd_only",
        action="store_true",
        default=False,
        help="Apply calculation to Single-Family Detached only (this is only on plotting for now)",
    )
    parser.add_argument(
        "-x",
        "--export_result_as_map",
        action="store_true",
        default=False,
        help="Whether to export panel prediction result as a building_id map only. "
        "Default to appending panel prediction result as new column(s) to input result file. ",
    )

    args = parser.parse_args()
    main(
        args.filename,
        retain_proba=args.retain_proba,
        plot_only=args.plot_only,
        sfd_only=args.sfd_only,
        export_result_as_map=args.export_result_as_map,
    )

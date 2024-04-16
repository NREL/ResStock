from pathlib import Path
import argparse
import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import itertools


def load_model(model_file):
    model = pickle.load(open(model_file, "rb"))
    model.feature_names = model.get_booster().feature_names
    
    return model

def create_input_tsv(model):
    """ Apply regression model to ResStock result dataframe
    Args : 
        df : pd.DataFrame
            dataframe of ResStock results_up00 file
        model : scikit-learn DecisionTree model
            regression model
        predict_proba : bool
            if True, use model.predict_proba(), else use model.predict()
        retain_proba : bool
            only applicable when predict_proba=True
            if True, predicted output value is a distribution of output labels instead of a single label
            if False, predicted output value is a single label probablistically chosen based on output distribution
    """
    ## -- process data to align with model inputs --
    input_options = {
        "Geometry Floor Area": ["0-499", "500-749", "750-999", "1000-1499", "1500-1999", "2000-2499", "2500-2999", "3000-3999", "4000+"],
        "Geometry Building Type RECS": ["Mobile Home", "Multi-Family with 2 - 4 Units", "Multi-Family with 5+ Units", "Single-Family Attached", "Single-Family Detached"],
        "Heating Fuel": ["Electricity", "Fuel Oil", "Natural Gas", "None", "Other Fuel", "Propane"],
        "Vintage": ["<1940", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s"],
    }

    # https://github.com/NREL/resstock/blob/develop/measures/ResStockArguments/measure.rb
    df_fa = pd.DataFrame(data=[
        ('0-499', "Mobile Home", 298),
        ('0-499', "Single-Family Detached", 298),
        ('0-499', "Single-Family Attached", 273),
        ('0-499', "Multi-Family with 2 - 4 Units", 322),
        ('0-499', "Multi-Family with 5+ Units", 322),
        
        ('500-749', "Mobile Home", 634),
        ('500-749', "Single-Family Detached", 634),
        ('500-749', "Single-Family Attached", 625),
        ('500-749', "Multi-Family with 2 - 4 Units", 623),
        ('500-749', "Multi-Family with 5+ Units", 623),

        ('750-999', "Mobile Home", 881),
        ('750-999', "Single-Family Detached", 881),
        ('750-999', "Single-Family Attached", 872),
        ('750-999', "Multi-Family with 2 - 4 Units", 854),
        ('750-999', "Multi-Family with 5+ Units", 854),

        ('1000-1499', "Mobile Home", 1228),
        ('1000-1499', "Single-Family Detached", 1228),
        ('1000-1499', "Single-Family Attached", 1207),
        ('1000-1499', "Multi-Family with 2 - 4 Units", 1138),
        ('1000-1499', "Multi-Family with 5+ Units", 1138),

        ('1500-1999', "Mobile Home", 1698),
        ('1500-1999', "Single-Family Detached", 1698),
        ('1500-1999', "Single-Family Attached", 1678),
        ('1500-1999', "Multi-Family with 2 - 4 Units", 1682),
        ('1500-1999', "Multi-Family with 5+ Units", 1682),

        ('2000-2499', "Mobile Home", 2179),
        ('2000-2499', "Single-Family Detached", 2179),
        ('2000-2499', "Single-Family Attached", 2152),
        ('2000-2499', "Multi-Family with 2 - 4 Units", 2115),
        ('2000-2499', "Multi-Family with 5+ Units", 2115),

        ('2500-2999', "Mobile Home", 2678),
        ('2500-2999', "Single-Family Detached", 2678),
        ('2500-2999', "Single-Family Attached", 2663),
        ('2500-2999', "Multi-Family with 2 - 4 Units", 2648),
        ('2500-2999', "Multi-Family with 5+ Units", 2648),

        ('3000-3999', "Mobile Home", 3310),
        ('3000-3999', "Single-Family Detached", 3310),
        ('3000-3999', "Single-Family Attached", 3228),
        ('3000-3999', "Multi-Family with 2 - 4 Units", 3171),
        ('3000-3999', "Multi-Family with 5+ Units", 3171),

        ('4000+', "Mobile Home", 5587),
        ('4000+', "Single-Family Detached", 5587),
        ('4000+', "Single-Family Attached", 7414),
        ('4000+', "Multi-Family with 2 - 4 Units", 6348),
        ('4000+', "Multi-Family with 5+ Units", 6348),
    ], columns=["Geometry Floor Area", "Geometry Building Type RECS", "sqft"])

    df = pd.DataFrame(data=itertools.product(*input_options.values()), 
                      columns=input_options.keys())

    dfi = df.merge(df_fa, on=["Geometry Floor Area", "Geometry Building Type RECS"])    

    input_cols_map = {
        "sqft": "sqft", # numeric
        "Geometry Building Type RECS": "geometry_building_type_recs_simp",
        "Heating Fuel": "heating_fuel",
        "Vintage": "vintage",
    }

    categorical_columns = list(input_cols_map.values())[1:]

    dfi = dfi[input_cols_map.keys()].rename(columns=input_cols_map)

    # special mapping for building type:
    dfi["geometry_building_type_recs_simp"] = dfi["geometry_building_type_recs_simp"].map({
        "Mobile Home": "Mobile Home",
        "Multi-Family with 2 - 4 Units": "Multi-Family with 2 - 4 Units",
        "Multi-Family with 5+ Units": "Multi-Family with 5+ Units",
        "Single-Family Attached": "Single-Family",
        "Single-Family Detached": "Single-Family",
    })

    # special mapping for heating fuels:
    dfi["heating_fuel"] = dfi["heating_fuel"].map({
        "Electricity": "Electricity",
        "Fuel Oil": "Fuel Oil",
        "Natural Gas": "Natural Gas",
        "Other Fuel": "Other",
        "Propane": "Propane",
        "None": "None",
    })

    dfi = pd.get_dummies(dfi, columns=categorical_columns, prefix_sep="__")
    # add any missing cols
    for col in model.feature_names: 
        if col not in dfi.columns:
            print(f" - adding dummy encoding column to df: {col}")
            dfi[col] = 0

    ## -- predict --
    panel_prob = model.predict_proba(dfi[model.feature_names], check_input=True)
    panel_labels = [f"Option={x}" for x in model.classes_]

    ## -- combine --
    df = df.rename(columns=lambda x: f"Dependency={x}")
    df[panel_labels] = panel_prob

    ## -- save to tsv file --
    print("** Electrical Panel Amp TSV exported: ")
    df.to_csv(local_dir / "Electrical Panel Amp.tsv", sep="\t", index=False, lineterminator="\r\n")

    return df

def apply_model_to_results(df, model, predict_proba=False, retain_proba=False):
    """ Apply regression model to ResStock result dataframe
    Args : 
        df : pd.DataFrame
            dataframe of ResStock results_up00 file
        model : scikit-learn DecisionTree model
            regression model
        predict_proba : bool
            if True, use model.predict_proba(), else use model.predict()
        retain_proba : bool
            only applicable when predict_proba=True
            if True, predicted output value is a distribution of output labels instead of a single label
            if False, predicted output value is a single label probablistically chosen based on output distribution
    """
    ## -- process data to align with model inputs --
    input_cols_map = {
        "upgrade_costs.floor_area_conditioned_ft_2": "sqft", # numeric
        "build_existing_model.geometry_building_type_recs": "geometry_building_type_recs_simp",
        "build_existing_model.heating_fuel": "heating_fuel",
        "build_existing_model.vintage": "vintage",
    }
    categorical_columns = list(input_cols_map.values())[1:]

    cond = df["completed_status"] == "Success"
    if df.index.name == "building_id":
        dfi = df.loc[cond, list(input_cols_map.keys())].rename(columns=input_cols_map)
    else:
        dfi = df.loc[cond, ["building_id"]+list(input_cols_map.keys())].reset_index(drop=True).rename(columns=input_cols_map)

    # special mapping for building type:
    dfi["geometry_building_type_recs_simp"] = dfi["geometry_building_type_recs_simp"].map({
        "Mobile Home": "Mobile Home",
        "Multi-Family with 2 - 4 Units": "Multi-Family with 2 - 4 Units",
        "Multi-Family with 5+ Units": "Multi-Family with 5+ Units",
        "Single-Family Attached": "Single-Family",
        "Single-Family Detached": "Single-Family",
    })

    # special mapping for heating fuels:
    dfi["heating_fuel"] = dfi["heating_fuel"].map({
        "Electricity": "Electricity",
        "Fuel Oil": "Fuel Oil",
        "Natural Gas": "Natural Gas",
        "Other Fuel": "Other",
        "Propane": "Propane",
        "None": "None",
    })

    dfii = pd.get_dummies(dfi, columns=categorical_columns, prefix_sep="__")
    if "building_id" in dfii.columns:
        dfii = dfii.drop(columns=["building_id"])
    # add any missing cols
    for col in model.feature_names: 
        if col not in dfii.columns:
            print(f" - adding dummy encoding column to df: {col}")
            dfii[col] = 0

    ## -- predict --
    if predict_proba:
        panel_prob = model.predict_proba(dfii[model.feature_names], check_input=True)
        panel_labels = model.classes_

        if retain_proba:
            dfii = dfi[["building_id"]].copy()
            dfii[panel_labels] = panel_prob
            df = df.merge(dfii, on="building_id")

        # random draw according to probability
        panel_prob_cum = np.cumsum(panel_prob, axis=1)
        random_nums_uniform = np.random.default_rng(seed=8).uniform(0,1, size=len(panel_prob))

        panel_amp = np.array([
            panel_labels[num<=arr][0] for num, arr in zip(random_nums_uniform, panel_prob_cum)
            ])
    else:
        panel_amp = model.predict(dfii[model.feature_names])

    if df.index.name == "building_id":
        df = pd.concat([df, pd.Series(panel_amp, index=dfi.index).rename("predicted_panel_amp")], axis=1)
    else:  
        df["predicted_panel_amp"] = df["building_id"].map(dict(zip(dfi["building_id"], panel_amp)))

    return df
    

def validate_model_with_dummy_data(model):
    df = pd.read_excel(local_dir / "helper files" / "model_input_example.xlsx", sheet_name="inputs", header=1)
    output = pd.read_excel(local_dir / "helper files" / "model_input_example.xlsx", sheet_name="outputs", dtype=str)

    # -- check predicted values against dummy data --
    panel_amp = model.predict(df[model.feature_names], check_input=True)
    check = panel_amp == np.array(output.iloc[:,0])
    assert len(check[check==False])==0, f"Predicted panel amperage does not match LBNL input and output dummy data: \n{check[check==False]}"
    print("Model validated against dummy data!")

def extract_left_edge(val):
    # for sorting things like AMI
    if val is None:
        return np.nan
    if not isinstance(val, str):
        return val
    first = val[0]
    if re.search(r"\d", val) or first in ["<", ">"] or first.isdigit():
        vals = [int(x) for x in re.split("\-| |\%|\<|\+|\>|s|th|p|A|B|C| ", val) if re.match("\d", x)]
        if len(vals) > 0:
            num = vals[0]
            if "<" in val:
                num -= 1
            if ">" in val:
                num += 1
            return num
    return val

def sort_index(df, axis="index", **kwargs):
    """ axis: ['index', 'columns'] """
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

def plot_output_saturation(df, output_dir, panel_metrics, sfd_only=False):
    print(f"Plots output to: {output_dir}")
    cond = df["completed_status"] == "Success"
    if sfd_only:
        # cond &= df["build_existing_model.ahs_region"]=="CBSA San Francisco-Oakland-Hayward, CA"
        cond &= df["build_existing_model.geometry_building_type_recs"]=="Single-Family Detached"
        df = df.loc[cond]
        print(f"Plotting applies to {len(df)} valid Single-Family Detached samples only")
    else:
        df = df.loc[cond]
        print(f"Plotting applies to {len(df)} valid samples only")

    for hc in [
        "build_existing_model.census_region",
        "build_existing_model.federal_poverty_level",
        "build_existing_model.tenure",
        "build_existing_model.geometry_floor_area_bin",
    ]:
    
        _plot_bar(df, [hc], panel_metrics, output_dir=output_dir)
  
    for hc in [
        "build_existing_model.census_region",
        "build_existing_model.census_division",
        "build_existing_model.ashrae_iecc_climate_zone_2004",
        "build_existing_model.geometry_building_type_recs",
        "build_existing_model.vintage",
        "build_existing_model.federal_poverty_level",
        "build_existing_model.tenure",
        "build_existing_model.geometry_floor_area_bin",
        "build_existing_model.geometry_floor_area",
    ]:
        _plot_bar_stacked(df, [hc], panel_metrics, output_dir=output_dir)
   

def _plot_bar(df, groupby_cols, metric_cols, output_dir=None):
    if "predicted_panel_amp" in metric_cols:
        dfi = df[groupby_cols+metric_cols+["building_id"]]
        dfi = dfi.groupby(groupby_cols+metric_cols)["building_id"].count().unstack()
    else:
        dfi = df.groupby(groupby_cols)[metric_cols].sum()
        metric_cols = ["predicted_panel_amp_expected_value"]
        breakpoint()

    fig, ax = plt.subplots()
    sort_index(sort_index(dfi, axis=0), axis=1).plot(kind="bar", ax=ax)
    if output_dir is not None:
        metric = "__by__".join(groupby_cols+metric_cols)
        fig.savefig(output_dir / f"bar_{metric}.png", dpi=400, bbox_inches="tight")

def _plot_bar_stacked(df, groupby_cols, metric_cols, output_dir=None):
    if "predicted_panel_amp" in metric_cols:
        dfi = df[groupby_cols+metric_cols+["building_id"]]
        dfi = dfi.groupby(groupby_cols+metric_cols)["building_id"].count().unstack()
    else:
        dfi = df.groupby(groupby_cols)[metric_cols].sum()
        metric_cols = ["predicted_panel_amp_expected_value"]

    dfi = dfi.divide(dfi.sum(axis=1), axis=0)

    fig, ax = plt.subplots()
    sort_index(sort_index(dfi, axis=0), axis=1).plot(kind="bar", stacked=True, ax=ax)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_title(f"Saturation of {metric_cols[0]}")
    if output_dir is not None:
        metric = "__by__".join(groupby_cols+metric_cols)
        fig.savefig(output_dir / f"stacked_bar_{metric}.png", dpi=400, bbox_inches="tight")


def read_file(filename, low_memory=True):
    """ If file is large, use low_memory=False"""
    filename = Path(filename)
    if filename.suffix == ".csv":
        df = pd.read_csv(filename, low_memory=low_memory)
    elif filename.suffix == ".parquet":
        df = pd.read_parquet(filename)
    else:
        raise TypeError(f"Unsupported file type, cannot read file: {filename}")
    return df


def main(filename=None, predict_proba=False, retain_proba=False, plot_only=False, sfd_only=False):
    global local_dir

    local_dir = Path(__file__).resolve().parent

    if filename is None:
        filename = local_dir / "test_data" / "euss1_2018_results_up00_100.csv"
    else:
        filename = Path(filename)

    # Load model
    model_file = local_dir / "model_20240327/final_panel_model_rank_test_f1_weighted_41138.p"
    model = load_model(model_file)
    validate_model_with_dummy_data(model)

    create_input_tsv(model)
    
    panel_metrics = ["predicted_panel_amp"]
    if retain_proba:
        panel_metrics = list(model.classes_)

    if predict_proba and retain_proba:
        ext = "predicted_panels_in_probability"
    elif predict_proba and not retain_proba:
        ext = "predicted_panels_probablistically_assigned"
    else:
        ext = "predicted_panels"

    output_filename = filename.parent / (filename.stem + "__" + ext + ".csv")
    plot_dir_name = "plots_sfd" if sfd_only else "plots"
    output_dir = filename.parent / plot_dir_name / ext
    output_dir.mkdir(parents=True, exist_ok=True)

    if plot_only:
        print(f"Plotting output {panel_metrics} only, using output_filename: {output_filename}")
        if not output_filename.exists():
            raise FileNotFoundError(f"Cannot create plots, output_filename not found: {output_filename}")
        df = pd.read_csv(output_filename, low_memory=False)
        plot_output_saturation(df, output_dir, panel_metrics, sfd_only=sfd_only)
        sys.exit()

    df = read_file(filename, low_memory=False)
    df = apply_model_to_results(df, model, predict_proba=predict_proba, retain_proba=retain_proba)

    ## -- export --
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
        "defaults to test data: test_data/euss1_2018_results_up00_100.csv"
        )
    parser.add_argument(
        "-b",
        "--predict_proba",
        action="store_true",
        default=False,
        help="Whether to use model.predict_proba() to predict output as a distribution of output labels",
    )
    parser.add_argument(
        "-r",
        "--retain_proba",
        action="store_true",
        default=False,
        help="Only apply in conjunction with --predict_proba flag. "
        "\nWhen applied, predicted output is retained as a distribution of output labels and saturation plots give the expected saturation of output. "
        "Otherwise, predicted output is drawn probablistically based on the distribution of output labels and saturation plots give near expected saturation of output (with stochasticity)",
    )
    parser.add_argument(
        "-p",
        "--plot_only",
        action="store_true",
        default=False,
        help="Make plots only based on expected output file",
    )
    parser.add_argument(
        "-d",
        "--sfd_only",
        action="store_true",
        default=False,
        help="Apply calculation to Single-Family Detached only (this is only on plotting for now)",
    )

    args = parser.parse_args()
    main(args.filename, predict_proba=args.predict_proba, retain_proba=args.retain_proba, plot_only=args.plot_only, sfd_only=args.sfd_only)

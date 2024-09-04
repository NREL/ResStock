"""
Get summary of upgrades:
file_name, upgrade_name, Success, Fail, Invalid
"""
import numpy as np
from pathlib import Path
import argparse
from typing import Optional

import pandas as pd

def parse_filename(file):
    suffixes = file.suffixes
    assert suffixes != [], f"{file=} has no suffixes."
    suffix = "".join(suffixes)
    file_name = file.stem.removesuffix(suffix)
    return file_name

def parse_suffix(file):
    suffixes = file.suffixes
    assert suffixes != [], f"{file=} has no suffixes."
    suffix = "".join(suffixes)
    return suffix

def read_file(file):
    suffix = parse_suffix(file)
    if suffix == ".csv" or suffix == ".csv.gz":
        return pd.read_csv(file, compression="infer", low_memory=False, keep_default_na=False)
    if suffix == ".parquet":
        return pd.read_parquet(file)
    raise ValueError(f"Unsupported {suffix=}")

def save_to_file(df, file):
    suffix = parse_suffix(file)
    breakpoint()
    if suffix == ".csv" or suffix == ".csv.gz":
        df.to_csv(file, compression="infer", index=False)
        return
    if suffix == ".parquet":
        df.to_parquet(file)
        return
    raise ValueError(f"Unsupported {suffix=}")

def get_summary(file_dir: Path, output_file: Optional[Path]=None, remove_failed: bool=False, remove_vacant: bool=False):
    file_list = sorted(file_dir.glob("*results_up*"))
    if remove_failed:
        print(" ** All files are to be modified by removing failed simulations in place...")
    if remove_vacant:
        print(" ** All files are to be modified by removing vacant units in place...")
        baseline_file = [x for x in file_list if "results_up00" in str(x)]
        assert len(baseline_file) == 1, f"Baseline file not found or ambiguous:\n{baseline_file=}"
        file_list = baseline_file + [x for x in file_list if x not in baseline_file]

    ref_table = []
    for file in file_list:
        df = read_file(file)
        file_name = parse_filename(file)
        if "results_up00" in file_name:
            upgrade_name = "baseline"
        else:
            upg_names = [x for x in df["apply_upgrade.upgrade_name"].dropna().unique() if x not in ["", None, np.nan]]
            assert len(upg_names) == 1, f"Difficulty extracting upgrade name: {upg_names}"
            upgrade_name = upg_names[0]

        completed_stats = df.groupby(["completed_status"])["building_id"].count()

        stats = pd.Series({
            "filename": file_name,
            "upgrade_name": upgrade_name
            })

        stats = pd.concat([stats, completed_stats])
        ref_table.append(stats)

        # modify file
        if remove_failed:
            n1 = len(df)
            df = df.loc[df["completed_status"]=="Success"].reset_index(drop=True)
            n2 = len(df)
            assert n2 > 0, "After removing failed simulations, df is empty."
            print(f"   Removed {n1-n2} failed simulations, n={n1} -> {n2}")
        if remove_vacant:
            n1 = len(df)
            if "results_up00" in file_name:
                bldgs = df.loc[df["build_existing_model.vacancy_status"] != "Vacant", "building_id"]
            df = df.loc[df["building_id"].isin(bldgs)].reset_index(drop=True)
            n2 = len(df)
            assert n2 > 0, "After removing vacant units, df is empty."
            print(f"   Removed {n1-n2} vacant units, n={n1} -> {n2}")
        # export file
        if remove_failed or remove_vacant:
            save_to_file(df, file)

        print(f"Processed: {file_name}")

    ref_table = pd.concat(ref_table, axis=1).transpose()
    print(ref_table)


    if output_file is None:
        output_file = file_dir / "summary_table.csv"
    ref_table.to_csv(output_file, index=False)

    print(f"Summary table output to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file_dir",
        action="store",
        help="Path to resstock results directory"
        )
    parser.add_argument(
        "output_file",
        nargs="?",
        action="store",
        default=None,
        help="Path to save the ref_table to, default to save file to file_dir as 'summmary_table.csv'"
        )
    parser.add_argument(
        "-f",
        "--remove_failed",
        action="store_true",
        default=False,
        help="Whether to modify file(s) in place by removing failed simulations",
    )
    parser.add_argument(
        "-v",
        "--remove_vacant",
        action="store_true",
        default=False,
        help="Whether to modify file(s) in place by removing vacant units",
    )

    args = parser.parse_args()
    file_dir = Path(args.file_dir)
    output_file = args.output_file
    if output_file is not None:
        output_file = Path(output_file)

    get_summary(file_dir, output_file=output_file, remove_failed=args.remove_failed, remove_vacant=args.remove_vacant)

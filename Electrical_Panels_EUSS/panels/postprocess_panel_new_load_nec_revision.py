
"""
Requires env with python >= 3.10
-**
Electrical Panel Project: Estimate existing and new load in homes using 2026 revised NEC per LBNL
Load Summing Method: 220.83
Maximum Demand Method: 220.87

NEC panel capacity = min. main circuit breaker size (A)

By: Lixi.Liu@nrel.gov, Ilan.Upfal@nrel.gov
Date: 07/09/2024
Updated: 07/09/2024

-----------------

[220.83] - Load Summing Method
# Revision: 2 kVA/sqft instead of 3, no A/B sections, new demand factors
Generally, sum the following loads and then apply tiered demand load factors to the total load (see CAVEATS)
1) general lighting and receptable loads at 2 VA/sqft;
2) at least 2 branch circuits for kitchen and 1 branch circuit for laundry at 1.5 kVA per branch; and
3) all appliances that are fastened in place and permanently connected:
   - HVAC (taken as the larger nameplate of space heating or cooling), 
   - water heaters,
   - clothes dryers, 
   - cooking ranges/ovens, 
   - dishwashers,
   - EVSE (individual branch circuit), 
   - hot tubs, pool heaters, pool pumps, well pumps, garbage disposals, garbage compactors, and 
   - other fixed appliances with at least a 1/4 HP (500W) nameplate rating.

Total Load = 100% of first 8 kVA existing load + 40% of remaining existing load + \
80% new EVSE + 80% new ER space heating + 50% all other new loads
This means: 
If adding HP and keeping existing ER as backup,
    - remove cooling from existing load
    - add HP at 50% (likely heating-dominant)
If new HVAC is HP+ER backup, 
    - remove heating and cooling from existing load
    - add ER at 80%, HP at 50% (likely heating-dominant)
If replacing existing heating with ER heating,
    - determine dominance unadjusted
    - if heating-dominant, remove cooling from existing, add ER at 80%
    - if cooling-dominant, no action

HVAC load includes:
    - includes 120V air handler for non-electric central furnace, e.g., if HP with secondary gas furance, HP ODU + 120V handler
    - HP heating load = HP + backup (even though for integrated backup, OS-HPXML assumes one of the two can be on at a time)
does not include:
    - shared heating/cooling
    - boiler pump

[220.87] - Maximum Demand Method
# Revision: net load change instead of new loads to add on top of 125% peak, demand factors from 220.83 applicable to net change
# Different ways to determine peak if preceding year data is incomplete or low resolution
Existing Peak = 125% x 15_min_electricity_peak (1-full year)
Net change = New Load - Existing Load replaced
Adjusted net change = 80% net EVSE + 80% net ER space heating + 50% all other net loads
Total Load = Existing Peak + Adjusted net change

Adjustment made if hourly data is used, if less than 1 year of data is available
Load can account for partial usage (per Parts III-IV)
"""

import pandas as pd
from pathlib import Path
import numpy as np
import math
import argparse
import sys
from itertools import chain
from typing import Optional

from plotting_functions import _plot_scatter, _plot_box
from clean_up00_file import get_housing_char_cols

# --- lookup ---
geometry_unit_aspect_ratio = {
    "Single-Family Detached": 1.8,
    "Single-Family Attached": 0.5556,
    "Multi-Family with 2 - 4 Units": 0.5556,
    "Multi-Family with 5+ Units": 0.5556,
    "Mobile Home": 1.8,
} #  = front_back_length / left_right_width #TODO: not used currently

KBTU_H_TO_W = 293.07103866

def get_nameplate_rating(df_rating, load_category, appliance, parameter="volt-amps"):
    row = df_rating.loc[(df_rating['load_category'] == load_category) & (df_rating['appliance'] == appliance)]
    return list(row[parameter])[0]

nameplate_rating = pd.read_csv("nameplate_rating_new_load.csv")
water_heater_electric_power_rating = get_nameplate_rating(nameplate_rating, 'water heater', 'electric')
water_heater_electric_tankless_1bath_power_rating = get_nameplate_rating(nameplate_rating, 'water heater', 'electric tankless, 1 bathroom')
water_heater_electric_tankless_2bath_power_rating = get_nameplate_rating(nameplate_rating, 'water heater', 'electric tankless, 2 bathrooms')
water_heater_electric_tankless_3bath_power_rating = get_nameplate_rating(nameplate_rating, 'water heater', 'electric tankless, 3+ bathrooms')
water_heater_heat_pump_power_rating = get_nameplate_rating(nameplate_rating, 'water heater', 'heat pump')
water_heater_heat_pump_120_power_rating = get_nameplate_rating(nameplate_rating, 'water heater', 'heat pump, 120V, shared')

washer_power_rating = get_nameplate_rating(nameplate_rating, "clothes washer", "electric")
dryer_elctric_ventless_power_rating = get_nameplate_rating(nameplate_rating, 'clothes dryer', 'electric ventless')
dryer_elctric_power_rating = get_nameplate_rating(nameplate_rating, 'clothes dryer', 'electric')
dryer_elctric_120_power_rating = get_nameplate_rating(nameplate_rating, 'clothes dryer', 'electric, 120V')
dryer_heat_pump_power_rating = get_nameplate_rating(nameplate_rating, 'clothes dryer', 'heat pump')
dryer_heat_pump_120_power_rating = get_nameplate_rating(nameplate_rating, 'clothes dryer', 'heat pump, 120V')

range_elctric_power_rating = get_nameplate_rating(nameplate_rating, 'range/oven', 'electric')
range_induction_power_rating = get_nameplate_rating(nameplate_rating, 'range/oven', 'induction')
range_elctric_120_power_rating = get_nameplate_rating(nameplate_rating, 'range/oven', 'electric, 120V')
range_induction_120_power_rating = get_nameplate_rating(nameplate_rating, 'range/oven', 'induction, 120V')

dishwasher_power_rating = get_nameplate_rating(nameplate_rating, "dishwasher", "standard")
hot_tub_spa_power_rating = get_nameplate_rating(nameplate_rating, 'hot tub/spa', 'electric')
pool_heater_power_rating = get_nameplate_rating(nameplate_rating, 'pool heater', 'electric, 27 kW')
pool_pump_1_and_half_hp_power_rating = get_nameplate_rating(nameplate_rating, 'pool pump', '1.5 HP')
pool_pump_2_hp_power_rating = get_nameplate_rating(nameplate_rating, 'pool pump', '2 HP')

well_pump_1_hp_power_rating = get_nameplate_rating(nameplate_rating, 'well pump', '1 HP')
well_pump_1_and_half_hp_power_rating = get_nameplate_rating(nameplate_rating, 'well pump', '1.5 HP')
ventilation_kitchen_power_rating = get_nameplate_rating(nameplate_rating, 'ventilation', 'kitchen, 300 cfm')
ventilation_bathroom_power_rating = get_nameplate_rating(nameplate_rating, 'ventilation', 'bathroom, 50 cfm')

EVSE_power_rating_level1 = get_nameplate_rating(nameplate_rating, 'electric vehicle charger', 'electric, level 1')
EVSE_power_rating_level2 = get_nameplate_rating(nameplate_rating, 'electric vehicle charger', 'electric, level 2')
garbage_disposal_three_quarters_hp_power_rating = get_nameplate_rating(nameplate_rating, 'garbage disposal', '3/4 HP')
garage_door_half_hp_power_rating = get_nameplate_rating(nameplate_rating, 'garage door opener', '1/2 HP')

# --- funcs ---

### -------- existing load specs --------
def _general_load_lighting(row):
    """General Lighting & Receptacle Loads. NEC 220.41
    Accounts for motors < 1/8HP and connected to lighting circuit is covered by lighting load
    Dwelling footprint area MUST include garage

    Args:
        row : row of Pd.DataFrame()
        by_perimeter: bool
            Whether calculation is based on 
    """
    if row["completed_status"] != "Success":
        return np.nan

    garage_depth = 24 # ft
    match row["build_existing_model.geometry_garage"]:
        case "1 Car":
            garage_width = 12
        case "2 Car":
            garage_width = 24
        case "3 Car":
            garage_width = 36
        case "None":
            garage_width = 0
        case _:
            garage_width = 0
    
    floor_area = float(row["upgrade_costs.floor_area_conditioned_ft_2"]) # already based on exterior dim (AHS)

    # calculate based on perimeter of footprint with receptables at every 6-feet
    aspect_ratio = geometry_unit_aspect_ratio[row["build_existing_model.geometry_building_type_recs"]]
    fb_length = math.sqrt(floor_area * aspect_ratio) # total as if single-story
    lr_width = floor_area / fb_length

    floor_area += garage_width*garage_depth

    n_receptables = 2*(fb_length+lr_width) // 6
    receptable_load = n_receptables * 20*120 # 20-Amp @ 120V
    # TODO: add other potential unit loads

    return 2 * floor_area


def _general_load_kitchen(row, n=2):
    """Small Appliance Branch Circuits. NEC 220-16(a)
        At least 2 small appliances branch circuits at 20A must be included. NEC 210-11(c)1

        NEMA 5-15 3-prong plug, max up to 72A (60% * 120V) per circuit
        bldgtype-dependent: branch up to # receptacles

        Small appliances:
            - refrigerator: 100-250W
            - freezer: 30-100W

    Args:
        n: int | "auto"
            number of branches for small appliances, minimum 2
    """
    if row["completed_status"] != "Success":
        return np.nan

    if n == "auto":
        n = 2  # start with min requirement
        # TODO: can expand based on building_type, vintage, and floor_area
    if n < 2:
        raise ValueError(
            f"{n=}, at least 2 small appliance/kitchen branch circuit for General Load"
        )
    return n * 1500


def _general_load_laundry(row, n=1):
    """Laundry Branch Circuit(s). NEC 210-11(c)2, 220-16(b), 220-4(c)
        At least 1 laundry branch circuit must be included.

    Args:
        n: int | "auto"
            number of branches for general laundry load (exclude dryer), minimum 1
    """
    if row["completed_status"] != "Success":
        return np.nan
    if n == "auto":
        n = 1
    return 1500*n


def _general_load_washer(row):
    """If washer is larger than laundry branch circuit, add
        Pecan St clothes washers: 600-1440 W (1165 wt avg)
        Pecan St gas dryers: 600-2760 W (800 wt avg)

    Args:
        n: int | "auto"
            number of branches for general laundry load (exclude dryer), minimum 1
    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.clothes_washer_presence"] == "Yes":
        if washer_power_rating > 1500:
            return washer_power_rating
        return 0
    return 0


def _fixed_load_water_heater(row, method):
    """
    NumberofBathrooms = NumberofBedrooms/2 + 0.5
    Bedrooms = [1, 2, 3, 4, 5]
    Bathrooms = [1, 1.5, 2, 2.5, 3]
    tankless = [1, 2, 2, 3+, 3+]
    """
    if row["completed_status"] != "Success":
        return np.nan

    if (row["build_existing_model.water_heater_in_unit"] == "Yes") and ((
        row["build_existing_model.water_heater_fuel"] == "Electricity")or(
        "Electric" in row["build_existing_model.water_heater_efficiency"]
        )):
        if row["build_existing_model.water_heater_efficiency"] == "Electric Tankless":
            if int(row["build_existing_model.bedrooms"]) == 1:
                return water_heater_electric_tankless_1bath_power_rating 
            if int(row["build_existing_model.bedrooms"]) in [2,3]:
                return water_heater_electric_tankless_2bath_power_rating
            if int(row["build_existing_model.bedrooms"]) in [4,5]:
                return water_heater_electric_tankless_3bath_power_rating
            raise ValueError(f'Unsupported {row["build_existing_model.bedrooms"]=}')
        if "Heat Pump" in row["build_existing_model.water_heater_efficiency"]:
            if "120V" in row["build_existing_model.water_heater_efficiency"] or "120 V" in row["build_existing_model.water_heater_efficiency"]:
                if method == "83":
                    return 0
                if method == "87":
                    return water_heater_heat_pump_120_power_rating
                raise ValueError(f"Unsupported {method=}")
            return water_heater_heat_pump_power_rating
        return water_heater_electric_power_rating
    return 0


def _fixed_load_dishwasher(row):
    """
    Dishwasher: 12-15A, 120V
        Amperage not super correlated with kWh rating, but will assume 12A for <=255kWh, and 15A else
    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.dishwasher"] == "None":
        return 0
    return dishwasher_power_rating


def _fixed_load_ventilations(row):
    """
    Per 2010 BAHSP / OS-HPXML defaults
    Bathroom fans: (code mandate)
        - one fan per bathroom, 50 cfm per fan, 0.3 W/cfm
        - NumberofBathrooms = NumberofBedrooms / 2 + 0.5
        - NumberofBathrooms * 15 W
    Kitchen exhaust: (recommended, likely overestimated, but could offset OTR microwave, which is not counted)
        - OS-HPXML: one fan per cooking range, 100 cfm per fan, 0.3 W/cfm (checked, 180W for 600 cfm hood)
        - 100 cfm is the min recommended and modeled in ResStock, seems too low
        - generally, https://www.greenbuildingadvisor.com/article/sizing-a-kitchen-exhaust-fan
            - 1 cfm per 10 Btu of gas range
            - 10 cfm per inch width of electric range (e.g., 280 cfm for 28")
            - 300 cfm is the general recommendation
        - we do not size cooking in BTU. Instead, annual energy consumption calculated per energy rating rated home (RESNET 301 2019)
        - Finalizing, 300 cfm * 0.3 W/cfm = 90W
    """
    if row["completed_status"] != "Success":
        return np.nan

    num_bathrooms = round(int(row["build_existing_model.bedrooms"])/2+0.5) # OS-HPXML default
    bathroom_vent = num_bathrooms * ventilation_bathroom_power_rating # W

    kitchen_vent = 0
    if row["build_existing_model.cooking_range"] != "None":
        kitchen_vent = ventilation_kitchen_power_rating # W

    return bathroom_vent + kitchen_vent # W


def _fixed_load_garage_door(row):
    """
    Garage door opener invented in 1926, did not rise in popularity until 1970s
    Per Kitsap, 35 million homes have garage door openers
    Number of attached garages modeled in ResStock: 44 million homes

    Assume all garages have a garage door opener

    https://www.google.com/search?q=how+many+garage+has+door+opener&client=safari&sca_esv=1e424f4fdf06d354&sca_upv=
    1&rls=en&ei=gxXvZsbZIci0wN4P6tC0uQw&oq=how+many+garage+has+do&gs_lp=Egxnd3Mtd2l6LXNlcnAiFmhvdyBtYW55IGdhcmFnZSB
    oYXMgZG8qAggAMgUQIRigATIFECEYoAEyBRAhGKABMgUQIRigATIFECEYoAEyBRAhGKsCMgUQIRirAjIFECEYqwIyBRAhGJ8FMgUQIRifBUi0gQ
    FQvAZYj3NwCngBkAECmAHyAaABpx6qAQY1LjIyLjK4AQPIAQD4AQGYAiWgAoUcwgIKEAAYsAMY1gQYR8ICCxAAGIAEGJECGIoFwgIKEAAYgAQYQ
    xiKBcICERAuGIAEGLEDGNEDGIMBGMcBwgILEAAYgAQYsQMYgwHCAg4QLhiABBixAxiDARiKBcICExAuGIAEGLEDGNEDGEMYxwEYigXCAg0QLhiA
    BBhDGOUEGIoFwgIFEAAYgATCAgsQABiABBixAxiKBcICCBAuGIAEGLEDwgILEC4YgAQYsQMY1ALCAg4QABiABBixAxiDARiKBcICCBAAGIAEGLE
    DwgIKEAAYgAQYRhj7AcICFhAAGIAEGEYY-wEYlwUYjAUY3QTYAQHCAgsQABiABBiGAxiKBcICBhAAGBYYHsICCBAAGIAEGKIEwgIIEAAYogQYiQ
    XCAggQABgWGAoYHpgDAIgGAZAGCLoGBggBEAEYE5IHBTE0LjIzoAex1AE&sclient=gws-wiz-serp
    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.geometry_garage"] == "None":
        return 0
    if row["build_existing_model.geometry_garage"] == "1 Car":
        return garage_door_half_hp_power_rating

    if row["build_existing_model.geometry_garage"] == "2 Car":
        return garage_door_half_hp_power_rating*2

    if row["build_existing_model.geometry_garage"] == "3 Car":
        return garage_door_half_hp_power_rating*3


def _fixed_load_garbage_disposal(row):
    """
    garbage disposal: 0.8 - 1.5 kVA (1.2kVA avg), typically second largest motor, after AC compressor
    Insinkerator: 1/3 - 1 HP (3/4 HP avg = 912 W)
    https://insinkerator.emerson.com/en-us/insinkerator-products/garbage-disposals/standard-series

    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["has_garbage_disposal"] == True:
        return garbage_disposal_three_quarters_hp_power_rating # .75 HP
            
    return 0


def _fixed_load_garbage_compactor(row):
    """
    We do not currently model compactor
    Ownership is ~ 3% as of 2013 (AHS)
    250 W
    """
    if row["completed_status"] != "Success":
        return np.nan

    return 0


def _fixed_load_hot_tub_spa(row):
    if row["completed_status"] != "Success":
        return np.nan

    if "Electric" in row["build_existing_model.misc_hot_tub_spa"]:
        return hot_tub_spa_power_rating
    return 0


def _fixed_load_well_pump(row):
    """ pump/motor nameplates taken from NEC tables based on HP, not PF needed """
    if row["completed_status"] != "Success":
        return np.nan
    
    if row["build_existing_model.misc_well_pump"] == "Typical Efficiency":
        if int(row["build_existing_model.bedrooms"]) in [1, 2, 3]:
            # up to 8 gpm of water need
            return well_pump_1_hp_power_rating
        if int(row["build_existing_model.bedrooms"]) in [4, 5]:
            # 9-18 gpm
            return well_pump_1_and_half_hp_power_rating 
        raise ValueError(f'Unsupported {row["build_existing_model.bedrooms"]=}')
    if row["build_existing_model.misc_well_pump"] == "None":
        return 0
    raise ValueError(f'Unsupported {row["build_existing_model.misc_well_pump"]=}')


def _special_load_dryer(row, method):
    """Clothes Dryers. NEC 220-18
    Use 5000 watts or nameplate rating whichever is larger (in another version, use DF=1 for # appliance <=4)
    240V, 22/24/30A breaker (vented), 30/40A (ventless heat pump), 30A (ventless electric)
    """
    if row["completed_status"] != "Success":
        return np.nan

    if "Electric" not in row["build_existing_model.clothes_dryer"] or row["build_existing_model.clothes_dryer"] == "None":
        return 0

    if "Heat Pump" in row["build_existing_model.clothes_dryer"]:
        if "120V" in row["build_existing_model.clothes_dryer"] or "120 V" in row["build_existing_model.clothes_dryer"]:
            if method == "83":
                return 0
            if method == "87":
                return dryer_heat_pump_120_power_rating
            raise ValueError(f"Unsupported {method=}")
        return dryer_heat_pump_power_rating
    if "120V" in row["build_existing_model.clothes_dryer"] or "120 V" in row["build_existing_model.clothes_dryer"]:
        if method == "83":
            return 0
        if method == "87":
            return dryer_elctric_120_power_rating
        raise ValueError(f"Unsupported {method=}")
    if "Ventless" in row["build_existing_model.clothes_dryer"]:
        return dryer_elctric_ventless_power_rating
    return dryer_elctric_power_rating


def _special_load_range_oven(row): 
    """ Derate cooking load based on Table 220.55 """

    if range_power <= 12000:
        range_power_w_df = min(range_power, 8000)
    elif range_power <= 27000:
        range_power_w_df = 8000 + 0.05*(max(0,range_power-12000)) # footnote 2
    else:
        raise ValueError(f"{range_power=} cannot exceed 27kW")
    
    return range_power_w_df


def _special_load_cooking_range_oven(row, method): 
    """ Assuming a single electric range (combined oven/stovetop) for each dwelling unit """
    if row["completed_status"] != "Success":
        return np.nan

    if "Electric" not in row["build_existing_model.cooking_range"] or row["build_existing_model.cooking_range"]=="None":
        return 0

    if "Induction" in row["build_existing_model.cooking_range"]:
        if "120V" in row["build_existing_model.cooking_range"] or "120 V" in row["build_existing_model.cooking_range"]:
            if method == "83":
                return 0
            if method == "87":
                return range_induction_120_power_rating
            raise ValueError(f"Unsupported {method=}")
        return range_induction_power_rating 

    if "120V" in row["build_existing_model.cooking_range"] or "120 V" in row["build_existing_model.cooking_range"]:
        if method == "83":
            return 0
        if method == "87":
            return range_elctric_120_power_rating
        raise ValueError(f"Unsupported {method=}")

    return range_elctric_power_rating 


def _special_load_space_heating_no_ahu(row) -> tuple[list]:
    if row["completed_status"] != "Success":
        return ([np.nan, np.nan, np.nan], [None, None, None])

    # shared heating is not part of dwelling unit's panel
    if row["build_existing_model.hvac_has_shared_system"] in ["Heating Only", "Heating and Cooling"]:
        return ([0, 0, 0], [None, None, None])

    # heating load
    heating_type = get_heating_type(row["build_existing_model.hvac_heating_efficiency"])
    secondary_heating_type = get_heating_type(row["build_existing_model.hvac_secondary_heating_efficiency"])

    heating_caps = [
        row["upgrade_costs.size_heating_system_primary_k_btu_h"],
        row["upgrade_costs.size_heating_system_secondary_k_btu_h"],
        row["upgrade_costs.size_heat_pump_backup_primary_k_btu_h"]
        ]
    system_types = [
        heating_type,
        secondary_heating_type,
        "Electric Resistance",
        ]

    heating_loads = [hvac_heating_conversion(x, system_type=y) for x, y in zip(heating_caps, system_types)]

    return (heating_loads, system_types)


def _special_load_space_cooling_no_ahu(row):
    if row["completed_status"] != "Success":
        return np.nan

    # shared cooling is not part of dwelling unit's panel
    if row["build_existing_model.hvac_has_shared_system"] in ["Cooling Only", "Heating and Cooling"]:
        return 0

    cooling_type = get_cooling_type(row["build_existing_model.hvac_cooling_type"])
    cooling_load = hvac_cooling_conversion(
        row["upgrade_costs.size_cooling_system_primary_k_btu_h"],
        system_type=cooling_type
    )
 
    return cooling_load


def _special_load_space_conditioning_itemized(row) -> tuple[float]:
    """ List of space conditioning loads
    Not accounting for humidifier
    """
    if row["completed_status"] != "Success":
        return tuple([np.nan for x in range(8)])
    
    heating_loads, system_types = _special_load_space_heating_no_ahu(row) # [pri, sec, hp_bkup]
    cooling_load = _special_load_space_cooling_no_ahu(row)

    heating_type = system_types[0]
    secondary_heating_type = system_types[1]
    heating_ahu, cooling_ahu = _get_air_handlers(row, heating_type, secondary_heating_type)

    # create (pri_hp, pri_er, sec_hp, sec_er, hp_bkup)
    heating_loads_hp_er = ()
    for heat_load, heat_type in zip(heating_loads[:2], system_types[:2]):
        if heat_type == "Electric Resistance":
            heating_loads_hp_er += (0, heat_load) # (hp, er)
        else:
            heating_loads_hp_er += (heat_load, 0)
    heating_loads_hp_er += (heating_loads[2],) # hp_bkup
    hvac_loads = heating_loads_hp_er + (heating_ahu, cooling_load, cooling_ahu)
    return hvac_loads


def apply_space_conditioning(row):
    """
    Calculate load_hvac and load_hvac_dominance
    Returns:
        load_hvac (max heating or cooling)
        hvac_dominance: ["heating", "cooling", "heating/cooling"]
    """
    heating_load = row[[
        "load_hvac_primary_heating_heat_pump",
        "load_hvac_primary_heating_electric_resistance",
        "load_hvac_secondary_heating_heat_pump",
        "load_hvac_secondary_heating_electric_resistance",
        "load_hvac_heat_pump_backup", 
        "load_hvac_heating_air_handler",
    ]].sum()
    cooling_load = row[[
        "load_hvac_cooling",
        "load_hvac_cooling_air_handler",
    ]].sum()

    if heating_load > cooling_load:
        return (heating_load, "heating")
    if heating_load < cooling_load:
        return (cooling_load, "cooling")
    if heating_load == cooling_load:
        return (cooling_load, "heating/cooling")
    return (np.nan, np.nan)

    if heating_load < cooling_load:
        return (cooling_load, "cooling")
    if heating_load == cooling_load:
        return (cooling_load, "heating/cooling")
    return (np.nan, np.nan)
    

def _special_load_heat_cool_air_handlers(row) -> tuple[float]:
    heating_type = get_heating_type(row["build_existing_model.hvac_heating_efficiency"])
    secondary_heating_type = get_heating_type(row["build_existing_model.hvac_secondary_heating_efficiency"])
    heat_ahu, cool_ahu = _get_air_handlers(row, heating_type, secondary_heating_type)
    return (heat_ahu, cool_ahu)


def _special_load_pool_heater(row):
    """NEC 680.9
    https://twphamilton.com/wp/wp-content/uploads/doc033548.pdf
    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.misc_pool_heater"] == "Electricity":
        return pool_heater_power_rating
    if row["build_existing_model.misc_pool_heater"] in ["None", "Natural Gas", "Other Fuel"]:
        return 0
    raise ValueError(f'Unknown {row["build_existing_model.misc_pool_heater"]=}')


def _special_load_pool_pump(row):
    """NEC 680
    In ResStock, the pool pump options are 0.75-1 HP, which are erroneously coded.
    According to this BA report, a standard single-speed HP is 1.5-2 HP.
    https://www.nrel.gov/docs/fy12osti/54242.pdf
    Mapping:
        "1.0 HP Pump": 2-HP
        "0.75 HP Pump": 1.5-HP
    1HP = 746W
    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.misc_pool_pump"] == "0.75 HP Pump":
        return pool_pump_1_and_half_hp_power_rating
    if row["build_existing_model.misc_pool_pump"] == "1.0 HP Pump":
        return pool_pump_2_hp_power_rating
    if row["build_existing_model.misc_pool_pump"] == "None":
        return 0
    raise ValueError(f'Unknown {row["build_existing_model.misc_pool_pump"]=}')


def _special_load_evse(row, method):
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.electric_vehicle"] == "None":
        return 0
    if "Level 1" in row["build_existing_model.electric_vehicle"]:
        if method == "83":
            return 0
        if method == "87":
            return EVSE_power_rating_level1
        raise ValueError(f"Unsupported {method=}")
    if "Level 2" in row["build_existing_model.electric_vehicle"]:
        return EVSE_power_rating_level2


def _special_load_heat_pump_backup(row):
    if row["completed_status"] != "Success":
        return np.nan

    heat_pump_backup = hvac_heating_conversion(
        row["upgrade_costs.size_heat_pump_backup_primary_k_btu_h"], 
        system_type="Electric Resistance"
        )
    return heat_pump_backup


### -------- new load specs --------
def _new_load_evse(row, option_columns, method):
    if row["completed_status"] != "Success":
        return np.nan

    for opt_col in option_columns:
        if "Electric Vehicle" in row[opt_col] and "Level 1" in row[opt_col]:
            if method == "83":
                return 0
            if method == "87":
                return EVSE_power_rating_level1
            raise ValueError(f"Unsupported {method=}")
        if "Electric Vehicle" in row[opt_col] and "Level 2" in row[opt_col]:
            return EVSE_power_rating_level2

    return 0

def _new_load_pool_heater(row, option_columns):
    if row["completed_status"] != "Success":
        return np.nan

    for opt_col in option_columns:
        if "Misc Pool Heater" in row[opt_col] and "Electricity" in row[opt_col]:
            return pool_heater_power_rating

    return 0


def _new_load_hot_tub_spa(row, option_columns):
    if row["completed_status"] != "Success":
        return np.nan

    for opt_col in option_columns:
        if "Misc Hot Tub Spa" in row[opt_col] and "Electricity" in row[opt_col]:
            return hot_tub_spa_power_rating 

    return 0


def _new_load_range_oven(row, option_columns, method):
    if row["completed_status"] != "Success":
        return np.nan

    for opt_col in option_columns:
        if "Cooking Range" in row[opt_col] and "Electric" in row[opt_col]:
            if "Induction" in row[opt_col]:
                if "120V" in row[opt_col] or "120 V" in row[opt_col]:
                    if method == "83":
                        return 0
                    if method == "87":
                        return range_induction_120_power_rating
                    raise ValueError(f"Unsupported {method=}")
                return range_induction_power_rating
            if "120V" in row[opt_col] or "120 V" in row[opt_col]:
                if method == "83":
                    return 0
                if method == "87":
                    return range_elctric_120_power_rating
                raise ValueError(f"Unsupported {method=}")
            return range_elctric_power_rating 

    return 0


def _new_load_dryer(row, option_columns, method):
    if row["completed_status"] != "Success":
        return np.nan

    for opt_col in option_columns:
        if "Clothes Dryer" in row[opt_col] and "Electric" in row[opt_col]:
            if "Heat Pump" in row[opt_col]:
                if "120V" in row[opt_col] or "120 V" in row[opt_col]:
                    if method == "83":
                        return 0
                    if method == "87":
                        return dryer_heat_pump_120_power_rating
                    raise ValueError(f"Unsupported {method=}")
                return dryer_heat_pump_120_power_rating
            if "120V" in row[opt_col] or "120 V" in row[opt_col]:
                if method == "83":
                    return 0
                if method == "87":
                    return dryer_elctric_120_power_rating
                raise ValueError(f"Unsupported {method=}")
            if "Ventless" in row[opt_col]:
                return dryer_elctric_ventless_power_rating
            return dryer_elctric_power_rating

    return 0


def _new_load_water_heating(row, option_columns, method):
    if row["completed_status"] != "Success":
        return np.nan

    for opt_col in option_columns:
        if "Water Heater Efficiency" in row[opt_col] and "Electric" in row[opt_col]: 
            if "Electric Tankless" in row[opt_col]:
                if int(row["build_existing_model.bedrooms"]) == 1:
                    return water_heater_electric_tankless_1bath_power_rating 
                if int(row["build_existing_model.bedrooms"]) in [2,3]:
                    return water_heater_electric_tankless_2bath_power_rating
                if int(row["build_existing_model.bedrooms"]) in [4,5]:
                    return water_heater_electric_tankless_3bath_power_rating
                raise ValueError(f'Unsupported {row["build_existing_model.bedrooms"]=}')
            if "Heat Pump" in row[opt_col]:
                if "120V" in row[opt_col] or "120 V" in row[opt_col]:
                    if method == "83":
                        return 0
                    if method == "87":
                        return water_heater_heat_pump_120_power_rating
                    raise ValueError(f"Unsupported {method=}")
                return water_heater_heat_pump_power_rating
            return water_heater_electric_power_rating

    return 0


def _new_load_space_conditioning_itemized(row, option_columns) -> tuple[float]:
    if row["completed_status"] != "Success":
        return tuple([np.nan for x in range(10)])

    # heating load
    heating_type = None
    secondary_heating_type = None
    backup_heating_type = None
    for opt_col in option_columns:
        if ("HVAC Heating Efficiency" in row[opt_col]):
            heating_type = get_heating_type(row[opt_col])

        if ("HVAC Secondary Heating Efficiency" in row[opt_col]):
            secondary_heating_type = get_heating_type(row[opt_col])

    # TODO: this is not a fail-safe solution
    if heating_type == "Heat Pump":
        if "existing" in row["apply_upgrade.upgrade_name"].lower():
            backup_heating_type = get_heating_type(row["build_existing_model.hvac_heating_efficiency"])
        else:
            backup_heating_type = "Electric Resistance"

    heating_caps = [
        row["upgrade_costs.size_heating_system_primary_k_btu_h"],
        row["upgrade_costs.size_heating_system_secondary_k_btu_h"],
        row["upgrade_costs.size_heat_pump_backup_primary_k_btu_h"]
        ]
    system_types = [
        heating_type,
        secondary_heating_type,
        backup_heating_type,
        ]

    heating_loads = [hvac_heating_conversion(x, system_type=y) for x, y in zip(heating_caps, system_types)]

    if heating_type == "Heat Pump":
        if row["build_existing_model.hvac_has_ducts"] == "Yes":
            cooling_has_ducts = heating_has_ducts = True
        else:
            cooling_has_ducts = heating_has_ducts = False
    else:
        heating_has_ducts = _get_heating_has_ducts(row)
        cooling_has_ducts = _get_cooling_has_ducts(row)

    # cooling load
    cooling_type = None
    for opt_col in option_columns:
        if ("HVAC Cooling Efficiency" in row[opt_col]):
            cooling_type = get_cooling_type(row[opt_col])

    cooling_load = hvac_cooling_conversion(
        row["upgrade_costs.size_cooling_system_primary_k_btu_h"],
        system_type=cooling_type
    )
    heating_ahu, cooling_ahu = _get_air_handlers(row, heating_type, secondary_heating_type)

    # create [pri_hp, pri_er, sec_hp, sec_er, hp_bkup]
    heating_loads_hp_er = []
    for heat_load, heat_type in zip(heating_loads[:2], system_types[:2]):
        if heat_type == "Electric Resistance":
            heating_loads_hp_er += [0, heat_load] # (hp, er)
        else:
            heating_loads_hp_er += [heat_load, 0]
    heating_loads_hp_er.append(heating_loads[2]) # hp_bkup

    hvac_loads = tuple(heating_loads_hp_er + [heating_ahu, cooling_load, cooling_ahu, heating_has_ducts, cooling_has_ducts])
    return hvac_loads


### -------- util funcs --------
def _get_heating_has_ducts(row) -> bool:
    return True if row["build_existing_model.hvac_heating_type"] in ["Ducted Heat Pump", "Ducted Heating"] else False

def _get_cooling_has_ducts(row) -> bool:
    return True if row["build_existing_model.hvac_cooling_type"] in ["Central AC", "Ducted Heat Pump"] else False

def _get_air_handlers(row, heating_type, secondary_heating_type) -> (float, float):
    """Typically you need more volume of air to cool the house than to heat it. 
    So the cooling requirements determine the size of the air handler. 
    However the air handler comes with the furnace. 
    So the air handler size determines the furnace size.

    Current logic: 
    - if gas furnace with CAC, use gas furnace (based on heat cap only, 120V)
    - if electric furnace with CAC, take max of heat/cool to determine AHU
    - if no ducted heating, use CAC (based on cool cap only)
    """
    if heating_type == "Heat Pump":
        if row["build_existing_model.hvac_has_ducts"] == "Yes":
            cooling_has_ducts = heating_has_ducts = True
        else:
            cooling_has_ducts = heating_has_ducts = False
    else:
        heating_has_ducts = _get_heating_has_ducts(row)
        cooling_has_ducts = _get_cooling_has_ducts(row)

    heat_ahu, cool_ahu = 0, 0

    if heating_has_ducts:
        if heating_type == "fuel" or secondary_heating_type == "fuel":
            # if dual fuel, retain old 120V AHU
            heat_ahu = hvac_120V_air_handler(row["upgrade_costs.size_heating_system_primary_k_btu_h"])
        else:
            heat_ahu = hvac_240V_air_handler(row["upgrade_costs.size_heating_system_primary_k_btu_h"])

    if cooling_has_ducts:
        if heating_has_ducts:
            if heating_type == "fuel" or secondary_heating_type == "fuel":
                # gas furnace with CAC, use gas furnace
                cool_ahu = heat_ahu
            else:
                cool_ahu = heat_ahu = max(
                    heat_ahu, 
                    hvac_240V_air_handler(row["upgrade_costs.size_cooling_system_primary_k_btu_h"])
                    )
        else:
            cool_ahu = hvac_240V_air_handler(row["upgrade_costs.size_cooling_system_primary_k_btu_h"])

    return (heat_ahu, cool_ahu)

def get_cooling_type(cool_eff) -> Optional[str]:
    if "Room AC" in cool_eff:
        return "Room AC"
    if "AC" in cool_eff:
        return "Central AC"
    if "Heat Pump" in cool_eff:
        return "Heat Pump"
    if cool_eff in ["None", "Shared Cooling"]:
        return None
    if cool_eff == "Evaporative Cooler":
        raise ValueError(f"Unsupported: {cool_eff=}")
    raise ValueError("Unknown cooling type")
    

def get_heating_type(heat_eff) -> Optional[str]:
    if ("ASHP" in heat_eff) or ("MSHP" in heat_eff):
        return "Heat Pump"
    if ("Electric" in heat_eff):
        return "Electric Resistance"
    if ("GSHP" in heat_eff):
        raise ValueError(f"Unsupported: {heat_eff=}")
    if heat_eff in ["None", "Shared Heating"]:
        return None
    return "fuel"


def hvac_240V_air_handler(nom_cap) -> float:
    ahu_volt = get_nameplate_rating(nameplate_rating, 'space heating/cooling', 'electric air handler', parameter="voltage")
    amp_para = get_nameplate_rating(nameplate_rating, 'space heating/cooling', 'electric air handler', parameter="amperage").split(",")
    ahu_amp = max(float(amp_para[2]), float(amp_para[0])*float(nom_cap) + float(amp_para[1]))
    return ahu_volt * ahu_amp


def hvac_120V_air_handler(nom_cap) -> float:
    ahu_volt = get_nameplate_rating(nameplate_rating, 'space heating', 'fuel air handler', parameter="voltage")
    amp_para = get_nameplate_rating(nameplate_rating, 'space heating', 'fuel air handler', parameter="amperage").split(",")
    ahu_amp = max(float(amp_para[2]), float(amp_para[0])*float(nom_cap) + float(amp_para[1]))
    return ahu_volt * ahu_amp


def apply_va_linear_regression(nom_cap, load_category, appliance) -> float:
    volt = get_nameplate_rating(nameplate_rating, load_category, appliance, parameter="voltage")
    amp_para = get_nameplate_rating(nameplate_rating, load_category, appliance, parameter="amperage").split(",")
    amp = float(amp_para[0])*float(nom_cap) + float(amp_para[1])
    return volt * amp


def hvac_heating_conversion(nom_heat_cap, system_type=None) -> float:
    """ 
    Relationship between either minimum breaker or minimum circuit amp (x voltage) and nameplate capacity
    nominal conditions refer to AHRI standard conditions: 47F?
    Args :
        nom_heat_cap : float
            nominal heating capacity in kbtu/h
        system_type : str
            system type
        heating_eff : str
            heating efficiency
    Returns : 
        W = Amp*V
    """ 
    if system_type is None or system_type in ["None", "fuel"]:
        return 0

    nom_heat_cap = float(nom_heat_cap)
    if "Heat Pump" in system_type:
        return apply_va_linear_regression(nom_heat_cap, "space heating", "heat pump")
    if system_type == "Electric Resistance":
        return nom_heat_cap * KBTU_H_TO_W
    raise ValueError(f"Unknown {system_type=}")


def hvac_cooling_conversion(nom_cool_cap, system_type=None) -> float:
    """ 
    Relationship between either minimum breaker or minimum circuit amp (x voltage) and nameplate capacity
    nominal conditions refer to AHRI standard conditions: 95F?
    Args :
        nom_cool_cap : float
            nominal cooling capacity in kbtu/h
        system_type : str
            system type
    Returns : 
        W = Amp*V
    """
    if system_type is None or system_type == "None":
        return 0

    nom_cool_cap = float(nom_cool_cap)
    if "Heat Pump" in system_type:
        return apply_va_linear_regression(nom_cool_cap, "space cooling", "heat pump")
    elif system_type == "Central AC":
        return apply_va_linear_regression(nom_cool_cap, "space cooling", "central ac")
    elif system_type == "Room AC":
        return apply_va_linear_regression(nom_cool_cap, "space cooling", "room ac")
    else:
        raise ValueError(f"Unknown {system_type=}")


def standard_amperage(x: float) -> int:
    """Convert min_amp_col into standard panel size
    http://www.naffainc.com/x/CB2/Elect/EHtmFiles/StdPanelSizes.htm
    """
    if pd.isnull(x):
        return np.nan

    # TODO: refine
    standard_sizes = np.array([
        50, 100, 125, 150, 200, 225,
        250])
    standard_sizes = np.append(standard_sizes, np.arange(300, 1250, 50))
    factors = standard_sizes / x

    cond = standard_sizes[factors >= 1]
    if len(cond) == 0:
        print(
            f"WARNING: {x} is higher than the largest standard_sizes={standard_sizes[-1]}, "
            "double-check NEC calculations"
        )
        return math.ceil(x / 100) * 100

    return cond[0]


def read_file(filename: str, low_memory: bool =True, sort_bldg_id: bool = False, **kwargs) -> pd.DataFrame:
    """ If file is large, use low_memory=False"""
    filename = Path(filename)
    if filename.suffix in [".csv", ".gz"]:
        df = pd.read_csv(filename, low_memory=low_memory, keep_default_na=False, **kwargs)
    elif filename.suffix == ".parquet":
        df = pd.read_parquet(filename)
    else:
        raise TypeError(f"Unsupported file type, cannot read file: {filename}")

    if sort_bldg_id:
        df = df.sort_values(by="building_id").reset_index(drop=True)

    return df


def bin_panel_sizes(df_column: pd.Series) -> pd.Series:
    df_out = df_column.copy()
    df_out.loc[df_column<100] = "<100"
    df_out.loc[(df_column>100) & (df_column<125)] = "101-124"
    df_out.loc[(df_column>125) & (df_column<200)] = "126-199"
    df_out.loc[df_column>200] = "200+"
    df_out = df_out.astype(str)

    return df_out



def generate_plots(df: pd.DataFrame, dfo: pd.DataFrame, output_dir: Path, sfd_only: bool = False, upgrade_num: str = ""):
    msg = " for Single-Family Detached only" if sfd_only else ""
    print(f"generating plots{msg}...")
    HC_list = [
        "build_existing_model.census_region",
        "build_existing_model.census_division",
        "build_existing_model.geometry_building_type_recs",  # dep
        "build_existing_model.state",
        # "build_existing_model.vintage",  # dep
        "build_existing_model.vintage_acs",
        "build_existing_model.federal_poverty_level",
        "build_existing_model.area_median_income",
        "build_existing_model.tenure",
        "build_existing_model.geometry_floor_area_bin",
        # "build_existing_model.geometry_floor_area",  # dep
        "build_existing_model.heating_fuel",  # dep
        "build_existing_model.water_heater_fuel",  # dep
        "build_existing_model.hvac_heating_type",
        "build_existing_model.hvac_cooling_type",  # dep
    ]
    dfo = dfo.join(df.set_index("building_id")[HC_list], on="building_id", how="left")
    upgrade_name = [x for x in dfo["apply_upgrade.upgrade_name"].unique() if x not in [None, "", np.nan]][0]

    _plot_scatter(dfo, "amp_total_pre_upgrade_A_220_83", "amp_total_pre_upgrade_A_220_87", 
        title=f"{upgrade_name}\nPre-upgrade comparison", output_dir=output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)
    _plot_scatter(dfo, "amp_total_post_upgrade_A_220_83", "amp_total_post_upgrade_A_220_87", 
        title=f"{upgrade_name}\nPost-upgrade comparison", output_dir=output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)
    _plot_scatter(dfo, "amp_total_pre_upgrade_A_220_83", "amp_total_post_upgrade_A_220_83", 
        title=f"{upgrade_name}\nNEC 220.83", output_dir=output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)
    _plot_scatter(dfo, "amp_total_pre_upgrade_A_220_87", "amp_total_post_upgrade_A_220_87", 
        title=f"{upgrade_name}\nNEC 220.87", output_dir=output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)
    print("scatter plots completed.")
    for metric in [
        "amp_total_pre_upgrade_A_220_83", 
        "amp_total_pre_upgrade_A_220_87",
        "amp_total_post_upgrade_A_220_83", 
        "amp_total_post_upgrade_A_220_87",
        ]:
        for hc in HC_list:
            _plot_box(dfo, metric, hc, output_dir=output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)
    print(f"plots output to: {output_dir}")


def existing_load_labels() -> list[str]:
    existing_loads_labels = existing_load_labels_replaceable() + [
        "load_lighting",
        "load_kitchen",
        "load_laundry",
        "load_washer",
        "load_dishwasher",
        "load_others", # disposal, garage doors, ventilations, 
        "load_well_pump",
        "load_pool_pump",
    ]
    return existing_loads_labels


def existing_load_labels_replaceable() -> list[str]:
    existing_loads_labels = [
        "load_hvac_primary_heating_heat_pump",
        "load_hvac_primary_heating_electric_resistance",
        "load_hvac_secondary_heating_heat_pump",
        "load_hvac_secondary_heating_electric_resistance",
        "load_hvac_heat_pump_backup",
        "load_hvac_heating_air_handler",
        "load_hvac_cooling",
        "load_hvac_cooling_air_handler",

        "load_water_heater",
        "load_dryer",
        "load_range_oven",
        "load_hot_tub_spa",
        "load_pool_heater",
        "load_evse",
    ]
    return existing_loads_labels


def apply_existing_loads(row, method: str, n_kit: int = 2, n_ldr: int = 1) -> list[float]:
    """ Load summing method """
    if row["completed_status"] != "Success":
        return [np.nan for x in range(22)]

    hvac_loads = _special_load_space_conditioning_itemized(row) # n=8

    existing_loads = list(hvac_loads) + [
            _fixed_load_water_heater(row, method),
            _special_load_dryer(row, method),
            _special_load_cooking_range_oven(row, method),
            _fixed_load_hot_tub_spa(row),
            _special_load_pool_heater(row),
            _special_load_evse(row, method),

            _general_load_lighting(row), # sqft
            _general_load_kitchen(row, n=n_kit), # consider logic based on sqft
            _general_load_laundry(row, n=n_ldr), # consider logic based on sqft (up to 2)
            _general_load_washer(row),
            _fixed_load_dishwasher(row),
                _fixed_load_garbage_disposal(row)+
                # _fixed_load_garbage_compactor(row)+
                _fixed_load_garage_door(row)+
                _fixed_load_ventilations(row),
            _fixed_load_well_pump(row),
            _special_load_pool_pump(row),
            
        ]

    return existing_loads


def apply_existing_loads_replaceable(row, method: str) -> list[float]:
    """ Load summing method """
    if row["completed_status"] != "Success":
        return [np.nan for x in range(14)]

    hvac_loads = _special_load_space_conditioning_itemized(row) # n=8

    existing_loads = list(hvac_loads) + [
            _fixed_load_water_heater(row, method),
            _special_load_dryer(row, method),
            _special_load_cooking_range_oven(row, method),
            _fixed_load_hot_tub_spa(row),
            _special_load_pool_heater(row),
            _special_load_evse(row, method),
        ] # no largest motor load

    return existing_loads


def apply_demand_factor(x, threshold=8000):
    """
    Split load into the following tiers and apply associated multiplier factor
        If threshold == 8000:
            <= 8kVA : 1.00
            > 8kVA : 0.4
    """
    return (
        1 * min(threshold, x) +
        0.4 * max(0, x - threshold)
    )

def apply_demand_factor_existing_and_new(all_load: pd.Series, frac_existing: pd.Series, threshold=8000) -> pd.Series:
    """
    100% first 8 kVA existing and new load + 40% remaining existing + 50% remaining new
    """
    return (
        1 * np.minimum(threshold, all_load) + 
        0.4 * np.maximum(0, (all_load-threshold)*frac_existing) +
        0.5 * np.maximum(0, (all_load-threshold)*(1-frac_existing))
    )


def apply_demand_factor_220_83_existing(row) -> float | list[float]:
    """Apply demand factor to existing loads per 220.83 """
    threshold = 8000 # VA

    # 220.83 100% of 1st 8kVA existing load + 40% of remainder existing load
    all_loads = [x for x in row.index if x.startswith("load_") and "hvac" not in x]
    all_loads.append("load_hvac")
    total_load = row[all_loads].sum()
    total_load = apply_demand_factor(total_load, threshold=threshold)

    return total_load


def calculate_total_load_post_upgrade(df_post, df_df, cond_upgraded) -> pd.Series:
    """ 
    all_other_adjusted = 100% first 8 kVA existing and new load + 40% remaining existing + 50% remaining new others 
    special_adjusted = 80% of new EVSE + 80% of new central ER heating (if heating-dominant)
    """

    df_post = df_post[df_df.columns]
    # True where existing and new loads are being aggregated for 8 kVA
    cond_df = pd.DataFrame(False, columns=df_df.columns, index=df_df.index)
    cond_df_existing = cond_df.mask(df_df==1, True)
    existing = df_post.mask(~cond_df_existing).sum(axis=1)
    cond_df_new = cond_df.mask(df_df==0.5, True)
    new_other = df_post.mask(~cond_df_new).sum(axis=1)
    all_other = existing + new_other
    frac_existing = existing / all_other
    all_other_adjusted = apply_demand_factor_existing_and_new(all_other, frac_existing)

    special_adjusted = (df_post*df_df).mask((cond_df_new | cond_df_existing)).sum(axis=1)
    return all_other_adjusted + special_adjusted


def calculate_new_loads(df: pd.DataFrame, dfu: pd.DataFrame, method: str, result_as_map: bool = False)-> pd.DataFrame:
    ## apply new load
    # 1 add necessary baseline HC
    HC_list = [
        "build_existing_model.hvac_heating_type",
        "build_existing_model.hvac_cooling_type",
        "build_existing_model.hvac_has_ducts",
        "build_existing_model.bedrooms",
        "build_existing_model.geometry_building_type_recs",
        "build_existing_model.hvac_heating_efficiency",
    ]
    HC_list = [x for x in HC_list if x not in dfu]
    new_load_cols = [x for x in dfu.columns if "new_load" in x]
    df_up = dfu.drop(columns=new_load_cols).copy()
    if HC_list:
        df_up = df_up.join(df.set_index(["building_id"])[HC_list], on=["building_id"], how="left")

    # 2 obtain valid list of upgrade option columns
    option_columns = [x for x in dfu.columns if x.startswith("upgrade_costs.option") and x.endswith("name")]
    option_cols = []
    upgrade_options = []
    for opt_col in option_columns:
        upgrade_option = [x for x in dfu[opt_col].unique() if x != "" and not pd.isna(x)]
        if upgrade_option:
            assert len(upgrade_option) == 1, f"{upgrade_option=} has more than one option."
            option_cols.append(opt_col)
            upgrade_options.append(upgrade_option[0])

    # 3 convert upgrade options to nameplate power ratings
    # [1] Heating and cooling
    hvac_labels = [
        "new_load_hvac_primary_heating_heat_pump",
        "new_load_hvac_primary_heating_electric_resistance",
        "new_load_hvac_secondary_heating_heat_pump",
        "new_load_hvac_secondary_heating_electric_resistance",
        "new_load_hvac_heat_pump_backup",
        "new_load_hvac_heating_air_handler",
        "new_load_hvac_cooling",
        "new_load_hvac_cooling_air_handler",
        "new_load_hvac_heating_has_ducts",
        "new_load_hvac_cooling_has_ducts",
    ]
    df_up[hvac_labels] = df_up.apply(lambda x: _new_load_space_conditioning_itemized(x, option_cols), axis=1).to_list()

    # [2] Water heating
    wh_option_cols, _ = get_upgrade_columns_and_options(option_cols, upgrade_options, "Water Heater Efficiency")
    df_up["new_load_water_heater"] = df_up.apply(lambda x: _new_load_water_heating(x, wh_option_cols, method), axis=1)

    # [3] Appliances
    dryer_option_cols, _ = get_upgrade_columns_and_options(option_cols, upgrade_options, "Clothes Dryer")
    df_up["new_load_dryer"] = df_up.apply(lambda x: _new_load_dryer(x, dryer_option_cols, method), axis=1)

    cooking_option_cols, _ = get_upgrade_columns_and_options(option_cols, upgrade_options, "Cooking Range")
    df_up["new_load_range_oven"] = df_up.apply(lambda x: _new_load_range_oven(x, cooking_option_cols, method), axis=1)

    hot_tub_spa_option_cols, _ = get_upgrade_columns_and_options(option_cols, upgrade_options, "Misc Hot Tub Spa")
    df_up["new_load_hot_tub_spa"] = df_up.apply(lambda x: _new_load_hot_tub_spa(x, hot_tub_spa_option_cols), axis=1)

    pool_heater_option_cols, _ = get_upgrade_columns_and_options(option_cols, upgrade_options, "Misc Pool Heater")
    df_up["new_load_pool_heater"] = df_up.apply(lambda x: _new_load_pool_heater(x, pool_heater_option_cols), axis=1)

    ev_option_cols, _ = get_upgrade_columns_and_options(option_cols, upgrade_options, "Electric Vehicle")
    df_up["new_load_evse"] = df_up.apply(lambda x: _new_load_evse(x, ev_option_cols, method), axis=1)

    # Project-specific: add EV load explicitly (for part II of TEA)
    EVSE_level = 1 # <--- 0, 1, 2
    if EVSE_level == 0:
        print("No EVSE postprocessing")
    if EVSE_level == 1: #and method == "87":
        print(f"Adding {EVSE_level=} for {method=}")
        cond = df_up["build_existing_model.geometry_building_type_recs"].isin([
            "Single-Family Detached",
            "Single-Family Attached",
            "Mobile Home",
            ])
        df_up.loc[cond, "new_load_evse"] = EVSE_power_rating_level1
    if EVSE_level == 2:
        print(f"Adding {EVSE_level=} for {method=}")
        cond = df_up["build_existing_model.geometry_building_type_recs"].isin([
            "Single-Family Detached",
            "Single-Family Attached",
            "Mobile Home",
            ])
        df_up.loc[cond, "new_load_evse"] = EVSE_power_rating_level2
    if EVSE_level not in [0, 1, 2]:
        raise ValueError(f"Unsupported {EVSE_level=}")

    # Nullify 0 values
    new_load_cols = [x for x in df_up.columns if "new_load" in x]
    df_up[new_load_cols] = df_up[new_load_cols].replace(0, np.nan)

    if result_as_map:
        df_up = df_up[["building_id"] + new_load_cols]
    else:
        df_up = df_up.drop(columns=HC_list)

    return df_up


def get_upgrade_columns_and_options(option_columns, upgrade_options, parameter):
    columns = [] # 'upgrade_costs.option_<>_name'
    options = [] # e.g., 'ASHP, SEER 15, 9.0 HSPF' if parameter = 'HVAC Heating Efficiency'
    for col, upgrade_option in zip(option_columns, upgrade_options):
        if parameter in upgrade_option:
            options.append(upgrade_option.split("|")[1])
            columns.append(col)
    return columns, options


def calculate_changes_in_existing_loads(df_existing, df_new, existing_as_backup=False):
    """ Separate existing loads that have been replaced and 
    existing loads that are remaining.

    Returns:
    df_replaced: pd.DataFrame
        Subset of existing loads that have been replaced
    df_remaining: pd.DataFrame
        Existing loads with replaced loads set to 0
    df_net: pd.DataFrame
        New loads - existing loads
    loads_upgraded: list[str]
        List of name of loads that have been replaced/upgraded
    """
    new_loads = [x for x in df_new.columns if x.startswith("new_load") and "has_ducts" not in x]
    upgradable_loads = [x.removeprefix("new_") for x in new_loads]
    other_loads = [x for x in df_existing.columns if x not in upgradable_loads+["load_hvac", "load_hvac_determinant"]]
    df_upgraded = df_new[new_loads].rename(columns=dict(zip(new_loads, upgradable_loads)))
    cond_upgraded = df_upgraded>0

    # consolidate HVAC
    up_hvac_loads = [x for x in upgradable_loads if "hvac" in x]
    up_non_hvac_loads = [x for x in upgradable_loads if x not in up_hvac_loads]

    # initialize demand factor df for non-hvac loads
    df_df = pd.DataFrame(1, columns=up_non_hvac_loads, index=df_upgraded.index)
    df_df = df_df.mask(cond_upgraded[up_non_hvac_loads]).fillna(0.5)  # 50% new loads
    df_df["load_evse"] = df_df["load_evse"].mask(cond_upgraded["load_evse"]).fillna(0.8) # 80% EVSE

    # 1. determine HVAC determinant in post-upgrade HVAC
    df_hvac = df_upgraded[up_hvac_loads].copy()
    df_hvac.update(df_existing[up_hvac_loads], overwrite=False) # post-upgrade HVAC system
    df_hvac[["post_load_hvac_unadjusted", "post_load_hvac_determinant"]] = df_hvac.apply(
        lambda x: apply_space_conditioning(x), axis=1).to_list()
    df_hvac = pd.concat([
        df_hvac,
        df_new[["new_load_hvac_heating_has_ducts", "new_load_hvac_cooling_has_ducts"]].fillna(False),
        ], axis=1)
    df_hvac["hvac_upgraded"] = False
    cond = df_hvac["post_load_hvac_unadjusted"] != df_existing["load_hvac"]
    df_hvac.loc[cond, "hvac_upgraded"] = True

    # 2. assign demand factors
    # Initialize
    df_hvac_df = pd.DataFrame(0, columns=up_hvac_loads, index=df_hvac.index)

    # cooling-dominant
    cond = df_hvac["post_load_hvac_determinant"]=="cooling" 
    for col in ["load_hvac_cooling", "load_hvac_cooling_air_handler"]:
        # existing cooling is dominant
        df_hvac_df.loc[cond, col] = 1

    # new cooling is dominant
    col = "load_hvac_cooling"
    cond2 = df_upgraded[col]>0
    df_hvac_df.loc[(cond & cond2), col] = 0.5

    col = "load_hvac_cooling_air_handler"
    cond3 = df_upgraded[col]>0
    df_hvac_df.loc[(cond & cond3), col] = 0.5

    # heating-dominant
    cond = df_hvac["post_load_hvac_determinant"].str.contains("heating")
    heating_cols = [x for x in up_hvac_loads if "heating" in x or "backup" in x]
    for col in heating_cols:
        # existing heating is dominant
        df_hvac_df.loc[cond, col] = 1

    # new heating is dominant
    col = "load_hvac_primary_heating_heat_pump"
    cond2 = df_upgraded[col]>0
    df_hvac_df.loc[(cond & cond2), col] = 0.5

    col = "load_hvac_primary_heating_electric_resistance"
    cond3 = df_upgraded[col]>0
    df_hvac_df.loc[(cond & cond3), col] = 0.8

    col = "load_hvac_secondary_heating_heat_pump"
    if existing_as_backup:
        # TODO: this is not a fail-safe solution
        cond_upgraded[col] = False # existing heating as secondary
    else:
        cond4 = df_upgraded[col]>0
        df_hvac_df.loc[(cond & cond4), col] = 0.5

    col = "load_hvac_secondary_heating_electric_resistance"
    if existing_as_backup:
        # TODO: this is not a fail-safe solution
        cond_upgraded[col] = False # existing heating as secondary
    else:
        cond5 = df_upgraded[col]>0
        df_hvac_df.loc[(cond & cond5), col] = 0.8

    col = "load_hvac_heat_pump_backup"
    if existing_as_backup:
        cond_upgraded[col] = False # existing heating as heat pump backup
    else:
        cond6 = df_upgraded[col]>0
        df_hvac_df.loc[(cond & cond6), col] = 0.8

    col = "load_hvac_heating_air_handler"
    cond7 = df_upgraded[col]>0
    df_hvac_df.loc[(cond & cond7), col] = 0.5

    # record which loads are upgraded (with HVAC consolidated)
    loads_upgraded = pd.concat([
        df_hvac["hvac_upgraded"].rename("load_hvac"),
        cond_upgraded[up_non_hvac_loads],
        ], axis=1).apply(lambda x: list(x[x].index), axis=1).rename("loads_upgraded") 

    # consolidate where end uses are upgraded in df_existing
    cond_upgraded = pd.concat([
        cond_upgraded,
        pd.DataFrame(False, columns=other_loads, index=cond_upgraded.index)
        ], axis=1)
    # consolidate demand factors
    df_df = pd.concat([
        df_hvac_df, 
        df_df[up_non_hvac_loads],
        pd.DataFrame(1, columns=other_loads, index=df_df.index)
        ], axis=1)

    # consolidate post-upgrade electric end use loads
    df_post = df_upgraded[up_non_hvac_loads].copy()
    df_post.update(df_existing[up_non_hvac_loads], overwrite=False)
    df_post = pd.concat([
        df_hvac[up_hvac_loads],
        df_post,
        df_existing[other_loads],
        df_hvac["post_load_hvac_determinant"],
        ], axis=1)

    return (df_post, df_df, cond_upgraded, loads_upgraded)


### -------- load method calcs --------
def calculate_new_load_total_220_83(dfi: pd.DataFrame, dfu: pd.DataFrame, n_kit: int = 2, n_ldr: int = 1, explode_result: bool = False, result_as_map: bool = False) -> pd.DataFrame:
    """
    NEC 220.83 - Load summing method
        Total loads = existing loads - loads removed + new loads
        Total loads get discounted based on whether additional space conditioning is added: (A)=No or (B)=Yes

    NEC 220.83 (A) where additional AC or space-heating IS NOT being installed
        - Total load = existing + new loads, 100% 1st 8kVA of total, 40% remainder of total
        - Used if upgrade has no electric space conditioning
    
    NEC 220.83 (B) where additional AC or space-heating IS being installed
        - 100% HVAC load + 100% 1st 8kVA other loads + 40% remainder of other
        - Used if upgrade has electric space conditioning, includes ER heating -> HP

    """
    print("Performing NEC 220.83 (load-summing) calculations...")
    df = dfi.copy()

    existing_as_backup = False
    if "existing" in dfu["apply_upgrade.upgrade_name"].replace("", np.nan).dropna().unique()[0].lower():
        existing_as_backup = True

    ## New loads
    df_new = calculate_new_loads(df, dfu, "83", result_as_map=True)
    new_loads = [x for x in df_new.columns if "new_load" in x]

    # Existing loads
    existing_loads = existing_load_labels()
    df_existing = pd.DataFrame(
        df.apply(lambda x: apply_existing_loads(x, "83", n_kit=n_kit, n_ldr=n_ldr), axis=1).to_list(),
        index = df.index, columns=existing_loads
        )
    df_existing[["load_hvac", "load_hvac_determinant"]] = df_existing.apply(
        lambda x: apply_space_conditioning(x), axis=1).to_list()

    # Total pre-upgrade load
    total_load_pre = "load_total_pre_upgrade_VA_220_83"
    total_amp_pre = "amp_total_pre_upgrade_A_220_83"
    df_result = pd.DataFrame(index=df_existing.index)
    df_result[total_load_pre] = df_existing.apply(lambda x: apply_demand_factor_220_83_existing(x), axis=1)
    df_result[total_amp_pre] = df_result[total_load_pre] / 240

    # Change in existing loads
    df_post, df_df, cond_upgraded, loads_upgraded = calculate_changes_in_existing_loads(
        df_existing, df_new, existing_as_backup=existing_as_backup
        )

    # QC
    diff = df_existing[existing_loads].compare(df_post[existing_loads])
    assert len(diff) > 0, "No difference between existing loads and post-upgrade loads"

    # Total post-upgrade load: 100% of 1st 8 kVA existing + 40% remaining existing + \
    # 80% new (EVSE | ER heating) + 50% new others
    total_load_post = "load_total_post_upgrade_VA_220_83"
    total_amp_post = "amp_total_post_upgrade_A_220_83"
    
    df_result[total_load_post] = calculate_total_load_post_upgrade(df_post, df_df, cond_upgraded)
    df_result[total_amp_post] = df_result[total_load_post] / 240

    df_result = pd.concat([
        df_new["building_id"],
        dfu["apply_upgrade.upgrade_name"],
        df_existing,
        df_result[[total_load_pre, total_amp_pre]],
        loads_upgraded.rename(loads_upgraded.name+"_83"),
        df_new[new_loads].rename(columns=lambda x: x+"_83"),
        df_post["post_load_hvac_determinant"].rename("post_load_hvac_determinant_83"),
        df_result[[total_load_post, total_amp_post]],
        ], axis=1)


    if explode_result:
        cols = df_result.columns
    else:
        cols = ["building_id", "apply_upgrade.upgrade_name", total_load_pre, total_amp_pre, total_load_post, total_amp_post]

    if result_as_map:
        return df_result[cols]

    return dfu.join(df_result[cols].drop(columns=["apply_upgrade.upgrade_name"]).set_index("building_id"), on="building_id")


def calculate_new_load_total_220_87(df: pd.DataFrame, dfu: pd.DataFrame, n_kit: int = 2, n_ldr: int = 1, explode_result: bool = False, result_as_map: bool = False) -> pd.DataFrame:
    """ Maximum demand method 
        - "report_simulation_output.peak_electricity_annual_total_w": timestep -- not available in EUSS RR1
        - "qoi_report.qoi_hourly_peak_magnitude_use_kw": peak of hourly aggregates, different from above
        - EUSS RR1 uses "qoi_report.qoi_peak_magnitude_use_kw"
    """
    print("Performing NEC 220.87 (max-load) calculations...")

    existing_as_backup = False
    if "existing" in dfu["apply_upgrade.upgrade_name"].replace("", np.nan).dropna().unique()[0].lower():
        existing_as_backup = True

    # New Loads
    df_new = calculate_new_loads(df, dfu, "87", result_as_map=True)
    new_loads = [x for x in df_new.columns if "new_load" in x]

    # Existing loads
    existing_loads = existing_load_labels()
    df_existing = pd.DataFrame(
        df.apply(lambda x: apply_existing_loads(x, "83", n_kit=n_kit, n_ldr=n_ldr), axis=1).to_list(),
        index = df.index, columns=existing_loads
        )
    df_existing[["load_hvac", "load_hvac_determinant"]] = df_existing.apply(
        lambda x: apply_space_conditioning(x), axis=1).to_list()

    # Total pre-upgrade load
    total_load_pre = "load_total_pre_upgrade_VA_220_87"
    total_amp_pre = "amp_total_pre_upgrade_A_220_87"
    peak_col = "report_simulation_output.peak_electricity_annual_total_w"
    if peak_col in df.columns:
        conversion = 1
    else:
        peak_col = "qoi_report.qoi_peak_magnitude_use_kw"
        if peak_col in df.columns:
            conversion = 1000
        else:
            raise ValueError("No suitable electricity peak column found.")
    print(f"Peak electricity column used: {peak_col}")

    df_result = pd.DataFrame(index=df_new.index)
    df_result[total_load_pre] = df[peak_col].astype(float) * conversion * 1.25 # VA
    df_result.loc[df["build_existing_model.vacancy_status"]=="Vacant", total_load_pre] = np.nan
    df_result[total_amp_pre] = df_result[total_load_pre] / 240 # amp

    ## Change in existing loads
    total_load_pre_upgrade = df_existing.apply(lambda x: apply_demand_factor_220_83_existing(x), axis=1)
    df_post, df_df, cond_upgraded, loads_upgraded = calculate_changes_in_existing_loads(
        df_existing, df_new, existing_as_backup=existing_as_backup
        )
    total_load_post_upgrade = calculate_total_load_post_upgrade(df_post, df_df, cond_upgraded)

    ## Total post-upgrade load
    total_load_post = "load_total_post_upgrade_VA_220_87"
    total_amp_post = "amp_total_post_upgrade_A_220_87"
    net_load_change = "net_change_in_load_total_VA_220_87"
    df_result[net_load_change] = total_load_post_upgrade - total_load_pre_upgrade
    df_result[total_load_post] = df_result[total_load_pre] + df_result[net_load_change]
    df_result[total_amp_post] = df_result[total_load_post] / 240

    df_result = pd.concat([
        df_new["building_id"],
        dfu["apply_upgrade.upgrade_name"],
        df_existing,
        df_result[[total_load_pre, total_amp_pre]],
        loads_upgraded.rename(loads_upgraded.name+"_87"),
        df_new[new_loads].rename(columns=lambda x: x+"_87"),
        df_post["post_load_hvac_determinant"].rename("post_load_hvac_determinant_87"),
        df_result[[net_load_change, total_load_post, total_amp_post]],
        ], axis=1)

    if explode_result:
        cols = df_result.columns
    else:
        cols = ["building_id", "apply_upgrade.upgrade_name", net_load_change, total_load_pre, total_amp_pre, total_load_post, total_amp_post]

    if result_as_map:
        return df_result[cols]

    return dfu.join(df_result[cols].drop(columns=["apply_upgrade.upgrade_name"]).set_index("building_id"), on="building_id")


def assign_garbage_disposal(df):
    """ Garbage disposal was invented in 1938 (Insinkable) and is in 52% of homes as of 2013 (AHS) """
    n_samples = round(len(df)*0.52)
    df["has_garbage_disposal"] = False
    cond = df["build_existing_model.vintage_acs"]!="<1940"
    selected = df.loc[cond, "building_id"].sample(n=n_samples, random_state=1)
    cond = df["building_id"].isin(selected)
    df.loc[cond, "has_garbage_disposal"] = True

    return df


def fix_well_pump(df):
    """ ResStock version specific 
    Currently well pump (12.7%) is randomly assigned to units.
    In 2013 AHS, well pump is said to serve up to 5 units.
    Well water is more common in SF, and actually in metro area
    https://onlinelibrary.wiley.com/doi/full/10.1111/1752-1688.13135
    Removing assignment from multi-family 5+ units (this would drop saturation by about 2.3%)
    """
    cond = df["build_existing_model.geometry_building_type_recs"]=="Multi-Family with 5+ Units"
    df.loc[cond, "build_existing_model.misc_well_pump"] = "None"

    return df


def main(
    baseline_filename: str | None = None, 
    upgrade_filename: str | None = None, 
    plot: bool = False, sfd_only: bool = False, explode_result: bool = False, result_as_map: bool = False):
    if baseline_filename is None:
        baseline_filename = (
            Path(__file__).resolve().parent
            / "test_data"
            / "euss1_2018_results_up00_100.csv" # "euss1_2018_results_up00_400plus.csv"
        )
    else:
        baseline_filename = Path(baseline_filename)


    if upgrade_filename is None:
        upgrade_filename = (
            Path(__file__).resolve().parent
            / "test_data"
            / "euss1_2018_results_up07_100.csv" # min-eff electrification package
        )
    else:
        upgrade_filename = Path(upgrade_filename)

    output_filedir = upgrade_filename.parent / "nec_calculations_revision"
    output_filedir.mkdir(parents=True, exist_ok=True) 
    ext = ""
    if explode_result:
        ext = "_exploded"
    if result_as_map:
        output_filename = output_filedir / (upgrade_filename.stem.split(".")[0] + f"__res_map__2026nec_new_load{ext}" + upgrade_filename.suffix)
    else:
        output_filename = output_filedir / (upgrade_filename.stem.split(".")[0] + f"__2026nec_new_load{ext}" + upgrade_filename.suffix)

    upgrade_num = [x for x in 
        list(chain(*[x.split(".") for x in upgrade_filename.stem.split("_")]))
        if "up" in x][0]
    plot_dir_name = f"plots_sfd" if sfd_only else f"plots"
    output_dir = upgrade_filename.parent / plot_dir_name / "nec_calculations_revision" / upgrade_num
    output_dir.mkdir(parents=True, exist_ok=True) 

    plot_later = False
    if plot:
        if not output_filename.exists():
            plot_later = True
        else:
            df = read_file(baseline_filename, compression="infer", low_memory=False)
            dfo = read_file(output_filename, low_memory=False)
            for col in [ 
                "amp_total_pre_upgrade_A_220_83",  
                "amp_total_pre_upgrade_A_220_87",
                "amp_total_post_upgrade_A_220_83",  
                "amp_total_post_upgrade_A_220_87",
            ]:
                dfo[col] = dfo[col].replace("", np.nan).astype(float)
            generate_plots(df, dfo, output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)
            sys.exit()
        
    df = read_file(baseline_filename, compression="infer", low_memory=False, sort_bldg_id=True)
    dfu = read_file(upgrade_filename, compression="infer", low_memory=False, sort_bldg_id=True)
    dfu = dfu[dfu["completed_status"]=="Success"].reset_index(drop=True)
    df = df[df["completed_status"]=="Success"].reset_index(drop=True)

    # Format
    columns = [x for x in df.columns if "build_existing_model" in x]
    df[columns] = df[columns].fillna("None")
    columns = [x for x in dfu.columns if x.startswith("upgrade_costs.option") and x.endswith("name")]
    dfu[columns] = dfu[columns].fillna("")

    # QC
    bldgs_no_bl = set(dfu["building_id"]) - set(df["building_id"])
    if bldgs_no_bl:
        print(f"WARNING: {len(bldgs_no_bl)} buildings have upgrade but no baseline: {bldgs_no_bl}")
    valid_bldgs = sorted(set(dfu["building_id"]).intersection(set(df["building_id"])))
    df = df[df["building_id"].isin(valid_bldgs)].reset_index(drop=True)
    dfu = dfu[dfu["building_id"].isin(valid_bldgs)].reset_index(drop=True)
    assert (dfu["building_id"] == df["building_id"]).prod() == 1, "Ordering of building_id does not match between upgrade and baseline"

    # # Project-specific (this is to rectify the mistake of using supplemental sizing for HP backup)
    # # To be turned on for 30k run results
    # if "existing" in dfu["apply_upgrade.upgrade_name"].replace("", np.nan).dropna().unique()[0].lower():
    #     dfu["upgrade_costs.size_heating_system_secondary_k_btu_h"] = np.nan
    #     cond = df["build_existing_model.hvac_heating_type"]=="Non-Ducted Heating"
    #     dfu.loc[cond, "upgrade_costs.size_heating_system_secondary_k_btu_h"] = \
    #         df.loc[cond, "upgrade_costs.size_heating_system_primary_k_btu_h"]
        
    #     dfu["upgrade_costs.size_heat_pump_backup_primary_k_btu_h"] = np.nan
    #     cond = df["build_existing_model.hvac_heating_type"]=="Ducted Heating"
    #     dfu.loc[cond, "upgrade_costs.size_heat_pump_backup_primary_k_btu_h"] = \
    #         df.loc[cond, "upgrade_costs.size_heating_system_primary_k_btu_h"]

    ## Assign garbage disposal to post-1940 homes randomly so ownership is 52% of dwelling units per 2013 AHS
    df = assign_garbage_disposal(df)

    ## Remove well pump from MF 5+
    df = fix_well_pump(df)

    # --- NEW LOAD calcs ---
    # NEC 220.83 - Load Summing Method
    # NEC 220.87 - Maximum Demand Method
    df1 = calculate_new_load_total_220_83(df, dfu, n_kit=2, n_ldr=1, explode_result=explode_result, result_as_map=result_as_map)
    df2 = calculate_new_load_total_220_87(df, dfu, n_kit=2, n_ldr=1, explode_result=explode_result, result_as_map=True)
    cols_to_drop = [x for x in df2.columns if "load_" in x and "87" not in x]+["apply_upgrade.upgrade_name"]
    dfo = df1.join(df2.set_index("building_id").drop(columns=cols_to_drop), on="building_id")
    dfo = pd.concat([dfo, df["has_garbage_disposal"]], axis=1)

    # --- save to file ---
    if output_filename.suffix == ".csv":
        dfo.to_csv(output_filename, index=False)
    elif output_filename.suffix == ".parquet":
        dfo.to_parquet(output_filename)
    print(f"File output to: {output_filename}")

    if plot_later:
        generate_plots(df, dfo, output_dir, sfd_only=sfd_only, upgrade_num=upgrade_num)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "baseline_filename",
        action="store",
        default=None,
        nargs="?",
        help="Path to ResStock baseline result file, e.g., results_up00.csv, "
        "defaults to test data: test_data/euss1_2018_results_up00_100.csv"
        )
    parser.add_argument(
        "upgrade_filename",
        action="store",
        default=None,
        nargs="?",
        help="Path to ResStock upgrade result file, e.g., results_up01.csv, "
        "defaults to test data: test_data/euss1_2018_results_up01_100.csv"
        )
    parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        default=False,
        help="Make plots based on expected output file without regenerating output_file",
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
        "--explode_result",
        action="store_true",
        default=False,
        help="Whether to export intermediate calculations as part of the results (useful for debugging)",
    )
    parser.add_argument(
        "-m",
        "--result_as_map",
        action="store_true",
        default=False,
        help="Whether to export NEC calculation result as a building_id map only. "
        "Default to appending NEC result as new column(s) to input result file. ",
    )

    args = parser.parse_args()
    if args.baseline_filename and not args.upgrade_filename:
        msg = "missing positional argument upgrade_filename, see --help"
        raise ValueError(msg)
    print("======================================================")
    print("New load calculation using 2026 proposed REVISION to NEC 220.83 and 220.87")
    print("======================================================")
    main(
        args.baseline_filename, args.upgrade_filename,
        plot=args.plot, sfd_only=args.sfd_only, explode_result=args.explode_result, result_as_map=args.result_as_map
        )

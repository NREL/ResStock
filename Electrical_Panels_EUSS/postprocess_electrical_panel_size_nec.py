"""
Requires env with python >= 3.10
-**
Electrical Panel Project: Estimate panel capacity using NEC (2023)
Standard method: 220 Part III. Feeder and Service Load Calculations
Optional method: 220 Part IV. Optional Feeder and Service Load Calculations

NEC panel capacity = min. main circuit breaker size (A)

By: Lixi.Liu@nrel.gov
Date: 02/01/2023

Updated: Ilan.Upfal@nrel.gov
Date: 3/3/2023

-----------------
kW = kVA * PF, kW: working (active) power, kVA: apparent (active + reactive) power, PF: power factor
For inductive load, use PF = 0.8 (except cooking per 220.55, PF=1)
Reactive power is phantom in that there may be current draw or voltage drop but no power is actually dissipated
(Inductors and capacitors have this behavior)

Continous load := max current continues for 3+ hrs
Branch circuit rating for continous load >= 1.25 x nameplate rating, but not applicable to load calc

-----------------

[1.1] STANDARD LOAD CALCULATION METHOD (new construction):

Overview:
Total Demand Load = General Load + Fixed Load + Special Load
Total Amperage = Total Demand / Circuit Voltage

Electrical circuit voltage = 
    * 240V for single-phase 120/240V service (most common)
    * 208V for three-phase 208/120V service

* General Load: 
    - lighting/recepticles + kitchen general + laundry general
    - Includes bathroom exhaust fans, most ceiling fans
    - Tiered demand factors for total General Load
* Fixed (fastened-in-place) Appliance Load: 
    - Water heater, dishwasher, garbage disposal, garbage compactor, 
    - Attic fan, central vacumm systems, microwave ...
    - At least 1/4 HP (500W), permanently fastened in place
    - ALWAYS exclude 3 special appliances: dryer, range, space heating & cooling 
    - Demand factor for total Fixed Load based on # of >=500W fixed appliances
* Special Appliance Load:
    - Clothes dryer, 
    - Range/oven,
    - Larger of space heating or cooling, 
    - Motor (usually AC compressor if cooling is larger, next is garbage disposal)
    - Hot tub (1.5-6kW + 1.5kW water pump), pool heater (~3kW), pool pump (0.75-1HP), well pump (0.5-5HP)
    - Demand factor depends on special appliance

Detailed description:
1. General Lighting and Receptacle Load (NEC 220.41):
    *general lighting:
        accounts for:
            - general-use receptacle outlets of 20 A including dedicated branch circuits for bathrooms, countertops, work surfaces and garages
            - outdoor receptacle outlets
            - lighting outlets
            - motors less than 1/8 hp and connected to lighting circuit
        floor area is defined as (220.5(c)):
            - outside dimensions of dwelling unit
            - excludes "open porches or unfinished areas not adaptable for future use as a habitable room or occupiable space"
            - includes garage as of 2023
        general lighting load = 3 VA/ft^2

    *small appliance circuit load (NEC 220.52)
        small-appliance circuit load (NEC 220.52 (A))
            - 1500 VA per 2-wire small-appliance circuit
            - minimum of 2 small-appliance circuits per dwelling (NEC 210.11 (C)(1))
        laundry circuit load (NEC 220.52 (B))
            - 1500 VA per 2-wire small-appliance circuit
            - minimum of 1 laundry circuit per dwelling (NEC 210.11 (C)(1))

    *demand factor (NEC 220.45)
        - Up to 3,000 VA @ 100%
        - 3,000 VA to 120,000 VA @ 35%
        - Over 120,000 VA @ 25%

2. Special loads:
    *electric cooking appliances (NEC 220.55)
        applies to:
            - cooking appliances which are fastened in place and rated above 1750 W
        home with single cooking appliance: (Table 220.55)
            - for 1 appliance rated @ 12 kW or less: demand load = 8 kW or nameplate rating
            - for 1 appliance rated over 12 kW: add 5% onto 8 kW per additional kW over 8 kW
        home with multiple cooking appliances: (Table 220.55)
            - if all same rating: same as above
            - if different ratings: group by less than 3 1/2 and over 3 1/2 and apply relevant demand factors

    *dryer (NEC 220.54)
        Load is either 5 kW (VA) or nameplate rating whichever is greater for each dryer
        DF of 100% for first 4 dryers, 85% for 5th, 75% for 6th ...
    
    *space heating and air-conditioning
        omit the smaller of the heating and cooling loads (NEC 220.60)
        space heating (220.51)
            - applies to fixed space heating
            - 100% of connected load
        air-conditioning equipment (NEC 220.50 (B))
            - use full load

    *electric vehicle supply equipment (NEC 220.57)
        - 7200 W or nameplate rating whichever is larger
        - Level 1 (slow): 1.2kW @ 120V (no special circuit) - receptacle plugs
        - Level 2 (fast): 6.2-19.2kW (7.6kW avg) @ 240V (likely dedicated circuit)
            -> same as 240V appliance plugs
            -> 80% of installed chargers are Level 2 (Market share in residential)

    *add 25% of largest motor load not already included (NEC 440.33)
    
3. Appliance load (NEC 220.53)
    applies to:
        - fastened in place appliances
        - 1/4 hp or greater, or 500 W or greater
    apply a demand factor of 75% if 4 or more
    125% for continuous loads

[1.2] OPTIONAL METHOD (new construction) (NEC 220.82): 
For New constructions dwellings, min 100 A service 
First 10 kVA at 100% and remainder at 40% of sum of OTHER_LOADS :=
    - 3 VA/ft^2 for outside dimensions of dwelling not including garage, unfinished porches, unused or unfinished spaces
    - 1500 VA per laundry and small appliance branch
    - nameplate rating of:
        - fastened in place appliances, permanently connected or on specific circuit
        - ranges, wall-mounted ovens, counter-mounted cooking units
        - clothes dryers not connected to laundry circuit
        - water heaters
        - all permanenty connected motors not listed in this section
and largest of:
    - 100% of nameplate of AC
    - 100% of nameplate of heat pump with no supplemental heating
    - 100% of nameplate of heat pump compressor and 65% of supplemental electric heat for central space-heating system unless they are prevented from running simultaneously
    - 65% of nameplate rating of electric space heating if less than four seperately controlled units
    - 40% of nameplate rating of electric space heat if more than four seperately controlled units 
    - 100% of nameplate rating of electric thermal storage or other heating sustme which is expected to run continuously at max load

[2.1] OPTIONAL METHOD (new load) (NEC 220.83):
For determining whether existing panel is of sufficient capacity to serve additional load
First 8 kVA at 100% and remainder at 40% of sum of OTHER_LOADS 
and largest of (
    - 100% of nameplate of AC
    - 100% of nameplate of central electric space heating
    - 100% of space heating units if less than 4 separately controlled (what about 4+? TODO)
    - Follow 220.82(c)(3) on heat pump (?, TODO)
    ) if has additional AC or electric heating,
    else 0


"""

import pandas as pd
from pathlib import Path
import numpy as np
import math
import argparse
import sys

from plotting_functions import plot_output, plot_output_saturation
from clean_up00_file import get_housing_char_cols

# --- lookup ---
geometry_unit_aspect_ratio = {
    "Single-Family Detached": 1.8,
    "Single-Family Attached": 0.5556,
    "Multi-Family with 2 - 4 Units": 0.5556,
    "Multi-Family with 5+ Units": 0.5556,
    "Mobile Home": 1.8,
} #  = front_back_length / left_right_width #TODO: check to see if it gets recalculated


hvac_fan_motor = 3*115*0.87 # 3A x 115V x PF (condenser fan motor) # TODO check value
hvac_blower_motor = 460 # TODO check value
KBTU_H_TO_W = 293.07103866

# --- funcs ---

def apply_demand_factor_to_general_load(x):
    """
    Split load into the following tiers and apply associated multiplier factor
        <= 3kVA : 1.00
        > 3kVA & <= 120kVA : 0.35
        > 120kVA : 0.25
    """
    return (
        1 * min(3000, x)
        + 0.35 * (max(0, min(120000, x) - 3000))
        + 0.25 * max(0, x - 120000)
    )

def apply_demand_factor_to_general_load_optm(x, threshold_load=10000):
    """
    Split load into the following tiers and apply associated multiplier factor
        If threshold_load == 1000:
            <= 10kVA : 1.00
            > 10kVA : 0.4

        For new_load calc per NEC 220.83, threshold_load=8000
    """
    return (
        1 * min(threshold_load, x) +
        0.4 * max(0, x - threshold_load)
    )

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
    
    floor_area = row["upgrade_costs.floor_area_conditioned_ft_2"] # already based on exterior dim (AHS)

    # calculate based on perimeter of footprint with receptables at every 6-feet
    aspect_ratio = geometry_unit_aspect_ratio[row["build_existing_model.geometry_building_type_recs"]]
    fb_length = math.sqrt(floor_area * aspect_ratio) # total as if single-story
    lr_width = floor_area / fb_length

    floor_area += garage_width*garage_depth

    n_receptables = 2*(fb_length+lr_width) // 6
    receptable_load = n_receptables * 20*120 # 20-Amp @ 120V
    # TODO: add other potential unit loads

    return 3 * floor_area

def _general_load_lighting_optm(row): 
    """Not including open porches, garages, unused or unfinished spaces not adaptable for future use"""
    if row["completed_status"] != "Success":
        return np.nan

    return 3 * row["upgrade_costs.floor_area_conditioned_ft_2"]

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
        """
        if (row["build_existing_model.misc_extra_refrigerator"] != "None") or (
            row["build_existing_model.misc_freezer"] != "None"
        ):
            n += 2  # 2 additional branches added for misc refrigeration (outside kitchen) #TODO: This is incorrect, small appliance branch circuits can only supply loads in the kitchen
        """
    if n < 2:
        raise ValueError(
            f"n={n}, at least 2 small appliance/kitchen branch circuit for General Load"
        )
    return n * 1500

def _general_load_laundry(row, n=1):
    """Laundry Branch Circuit(s). NEC 210-11(c)2, 220-16(b), 220-4(c)
        At least 1 laundry branch circuit must be included.

        Pecan St clothes washers: 600-1440 W (1165 wt avg)
        Pecan St gas dryers: 600-2760 W (800 wt avg)

    Args:
        n: int | "auto"
            number of branches for general laundry load (exclude dryer), minimum 1
    """
    if row["completed_status"] != "Success":
        return np.nan
    
    if n == "auto":
        if "Single-Family" in row["build_existing_model.geometry_building_type_recs"]:
            n = 1165 # TODO, can expand based on floor_area, vintage, etc
        elif row["build_existing_model.clothes_washer_presence"] == "Yes":
            # for non-SF, if there's in-unit WD, then there's a branch
            n = 1165
        else:
            n = 0

        if "Electric" not in row["build_existing_model.clothes_dryer"] and row["build_existing_model.clothes_dryer"] != "None":
            n += 800 # add additional laundry circuit for non-electric dryer
    
    if "Single-Family" in row["build_existing_model.geometry_building_type_recs"] and n < 1:
        raise ValueError(f"n={n}, at least 1 laundry branch circuit for Laundry Load")
   
    return max(1500, n)

def _fixed_load_water_heater(row):
    if row["completed_status"] != "Success":
        return np.nan

    # TODO: water heater in unit -- if discounting here, need it removed from peak load
    if (row["build_existing_model.water_heater_in_unit"] == "Yes") & ((
        row["build_existing_model.water_heater_fuel"] == "Electricity")|(
        "Electric" in row["build_existing_model.water_heater_efficiency"]
        )):
        if row["build_existing_model.water_heater_efficiency"] == "Electric Tankless":
            return 24000 * 1 # 18-36k
        if "Heat Pump" in row["build_existing_model.water_heater_efficiency"]:
            return 5000 * 0.97
        return 5500 * 1
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
    if (
        "270" in row["build_existing_model.dishwasher"]
        or "290" in row["build_existing_model.dishwasher"]
        or "318" in row["build_existing_model.dishwasher"]
    ):
        return 1800 * 0.99
    return 1440 * 0.99

def _fixed_load_garbage_disposal(row):
    """
    garbage disposal: 0.8 - 1.5 kVA (1.2kVA avg), typically second largest motor, after AC compressor

    pump/motor nameplates taken from NEC tables based on HP, not PF needed

    We do not currently model disposal, will use vintage and floor area as proxy for now
    there could be a jurisdition restriction as well as dep to dwelling type

    Garbage disposal became available in 1940s and lives in ~ 50% US households according to:
    https://www.michaelsplumbingorlando.com/a-brief-history-of-the-garbage-disposal-what-you-shouldnt-throw-down-it/

    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.vintage"] in [
        "1940-59",
        "1960-79",
        "1980-99",
        "2000-09",
        "2010s",
    ]:
        if row["build_existing_model.geometry_floor_area"] in ["0-499"]:
            return 0
        elif row["build_existing_model.geometry_floor_area"] in ["500-749", "750-999"]:
            return 500  # 1/3 HP
        elif row["build_existing_model.geometry_floor_area"] in [
            "1000-1499",
            "1500-1999",
            "2000-2499",
        ]:
            return 650  # 1/2 HP
        else:
            return 912 # .75 HP
    return 0

def _fixed_load_garbage_compactor(row):
    """
    We do not currently model compactor
    "Ownership dropped to under 3.5% across the nation by 2009" according to:
    https://www.familyhandyman.com/article/what-ever-happened-to-the-trash-compactor/
    """
    if row["completed_status"] != "Success":
        return np.nan

    return 0

def _fixed_load_hot_tub_spa(row):
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.misc_hot_tub_spa"] == "Electric":
        return 11520 * 1
    return 0

def _fixed_load_well_pump(row):
    """ pump/motor nameplates taken from NEC tables based on HP, not PF needed """
    if row["completed_status"] != "Success":
        return np.nan

    # TODO: verify
    if row["build_existing_model.misc_well_pump"] != "None":
        return 2000 
    return 0

def _special_load_electric_dryer(row):
    """Clothes Dryers. NEC 220-18
    Use 5000 watts or nameplate rating whichever is larger (in another version, use DF=1 for # appliance <=4)
    240V, 22/24/30A breaker (vented), 30/40A (ventless heat pump), 30A (ventless electric)
    """
    if row["completed_status"] != "Success":
        return np.nan

    if "Electric" not in row["build_existing_model.clothes_dryer"] or row["build_existing_model.clothes_dryer"] == "None":
        return 0

    if "Ventless" in row["build_existing_model.clothes_dryer"]:
        rating = 5400 * 1
    else:
        rating = 5600 * 1

    return max(5000, rating)

def _special_load_electric_range(row): 
    """ Assuming a single electric range (combined oven/stovetop) for each dwelling unit """
    range_power = _special_load_electric_range_nameplate(row)

    if range_power <= 12000:
        range_power_w_df = min(range_power, 8000)
    elif range_power <= 27000:
        range_power_w_df = 8000 + 0.05*(max(0,range_power-12000)) # footnote 2
    else:
        raise ValueError(f"range_power={range_power} cannot exceed 27kW")
    
    return range_power_w_df


def _special_load_electric_range_nameplate(row): 
    """ Assuming a single electric range (combined oven/stovetop) for each dwelling unit """
    if row["completed_status"] != "Success":
        return np.nan

    if "Electric" not in row["build_existing_model.cooking_range"] or row["build_existing_model.cooking_range"]=="None":
        return 0

    if "Induction" in row["build_existing_model.cooking_range"]:
        # range-oven: 10-13.6kW rating (240V, 40A) or 8.4kW (240V, 50A) or 8kW (240V, 40A)
        # cooktop: 11-12kW rating (240V, 30/50A) or 15.4kW rating (240V, 40A), 7.2-8.6kW (240V, 30/45A)
        # electric wall oven: 4.5kW (120V, 30A or 240V, 20/30A)
        # For induction cooktop + electric wall oven = 11+0.65*4.5 = 14kW 
        return 12000  # 40*240 or 14000 #TODO: This should be the full nameplate rating (max connected load) of an electric induction range

    ## Electric, non-induction
    # range-oven: 10-12.1-13.5kW (240V, 40A)
    # cooktop: 9.2kW (240V, 40A), 7.7-10.5kW (240V, 40/50A), 7.4kW (240V, 40A)
    # For cooktop + wall oven = 11+0.65*4.5 = 14kW or 0.65*(8+4.5) = 8kW
    return 12000  # or 12500 #TODO: This should be the full nameplate rating (max connected load) of an electric non-induction range


def hvac_heating_conversion(nom_heat_cap, system_type=None):
    """ 
    Relationship between either minimum breaker or minimum circuit amp (x voltage) and nameplate capacity
    nominal conditions refer to AHRI standard conditions: 47F?
    Args :
        nom_heat_cap : float
            nominal heating capacity in kbtu/h
        system_type : str
            system type
    Returns : 
        W = Amp*V
    """
    if system_type == "Ducted Heat Pump":
        return (0.6*nom_heat_cap + 7.2471) * 230 * 0.84
    if system_type == "Non-Ducted Heat Pump":
        return (0.8*nom_heat_cap + 2.2825) * 230 * 0.84

    return nom_heat_cap * KBTU_H_TO_W

def hvac_cooling_conversion(nom_cool_cap, system_type=None):
    """ 
    Relationship between either minimum breaker or minimum circuit amp (x voltage) and nameplate capacity
    nominal conditions refer to AHRI standard conditions: 95F?
    Args :
        nom_cool_cap : float
            nominal cooling capacity in kbtu/h
        system_type : str
            system type
    Returns : 
        W = Amp*V*PF
    """
    if system_type == "Ducted Heat Pump":
        return (0.6*nom_cool_cap + 7.2471) * 230 * 0.96
    if system_type == "Non-Ducted Heat Pump":
        return (1*nom_cool_cap + 0.2909) * 230 * 0.96
    if system_type == "Central AC":
        return (0.7*nom_cool_cap + 1.8978) * 230 * 0.96
    if system_type == "Room AC":
        return (0.4*nom_cool_cap + 3.4647) * 230 * 0.96

    return nom_cool_cap * KBTU_H_TO_W

def _special_load_space_heating(row):
    if row["completed_status"] != "Success":
        return np.nan

    if ((row["build_existing_model.heating_fuel"] == "Electricity") | (
        "ASHP" in row["build_existing_model.hvac_heating_efficiency"]
        ) | (
        "MSHP" in row["build_existing_model.hvac_heating_efficiency"]
        ) | (
        "GSHP" in row["build_existing_model.hvac_heating_efficiency"]
        ) | (
        "Electric" in row["build_existing_model.hvac_heating_efficiency"]
        ) | (
        "Electricity" in row["build_existing_model.hvac_shared_efficiencies"]
        )): 

        heating_cols = [
            row["upgrade_costs.size_heating_system_primary_k_btu_h"],
            row["upgrade_costs.size_heating_system_secondary_k_btu_h"],
            row["upgrade_costs.size_heat_pump_backup_primary_k_btu_h"]
            ]
        system_cols = [
            row["build_existing_model.hvac_heating_type"],
            row["build_existing_model.hvac_secondary_heating_efficiency"],
            "Electric", # TODO this depends on package
            ]

        heating_load = sum(
            [hvac_heating_conversion(x, system_type=y) for x, y in zip(heating_cols, system_cols)]
        )
    else:
        heating_load = 0

    
    if row["build_existing_model.hvac_has_ducts"] == "Yes":
        heating_load += hvac_fan_motor

    return heating_load


def _special_load_space_cooling(row):
    if row["completed_status"] != "Success":
        return np.nan, False

    cooling_load = hvac_cooling_conversion(
        row["upgrade_costs.size_cooling_system_primary_k_btu_h"],
        system_type=row["build_existing_model.hvac_heating_type"]
    )
    cooling_motor = cooling_load
    cooling_is_window_unit = True
    if row["build_existing_model.hvac_has_ducts"] == "Yes":
        cooling_load += hvac_fan_motor + hvac_blower_motor
        cooling_is_window_unit = False

    if cooling_is_window_unit:
        cooling_motor /= (int(row["build_existing_model.bedrooms"]) + 1)
    
    return cooling_load, cooling_motor


def _special_load_space_conditioning(row):
    """Heating or Air Conditioning. NEC 220-19.
    Take the larger between heating and cooling. Demand Factor = 1
    Include the air handler when using either one. (guessing humidifier too?)
    For heat pumps, include the compressor and the max. amount of electric heat which can be energized with the compressor running

    1 Btu/h = 0.29307103866W

    Returns:
        max(loads) : int
            special_load_for_heating_or_cooling
        cooling_motor : float
            size of cooling motor,
            = size_cooling_system_primary if central
            = approximate size of window AC if not central
            = 0 when heating is max load
    """
    if row["completed_status"] != "Success":
        return np.nan, np.nan

    heating_load = _special_load_space_heating(row)
    cooling_load, cooling_motor = _special_load_space_cooling(row)
    
    # combine
    loads = np.array([heating_load, cooling_load])

    return max(loads), cooling_motor # Always include cooling motor in largest motor at 25%


def _special_load_motor(row):
    """Largest motor (only one). NEC 220-14, 430-24
    Multiply the largest motor volt-amps x 25%
    Usually the air-conditioner compressor is the largest motor. Use if special_load is space cooling.
    Else use he next largest motor, usually garbage disposal
    """
    if row["completed_status"] != "Success":
        return np.nan

    _, cooling_motor = _special_load_space_conditioning(row)

    motor_size = max(
        cooling_motor,
        _fixed_load_garbage_disposal(row),
        _special_load_pool_pump(row, apply_df=False),
        _fixed_load_well_pump(row),
    )

    return 0.25 * motor_size


def _special_load_pool_heater(row, apply_df=True): # This is a continuous load so 125% factor must be applied
    """NEC 680.9
    https://twphamilton.com/wp/wp-content/uploads/doc033548.pdf
    """
    if row["completed_status"] != "Success":
        return np.nan

    if isinstance(row["build_existing_model.misc_pool_heater"], str) and "Electric" in row["build_existing_model.misc_pool_heater"]:
        return 3000
    return 0

def _special_load_pool_pump(row, apply_df=True):
    """NEC 680
    Pool pump (0.75-1HP), 15A or 20A, 120V or 240V
    1HP = 746W
    """
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.misc_pool_pump"] == "1.0 HP Pump":
        return 1 * 746 #TODO: Once an estimate has been established we can use Table 430.247 to determine connected load
    if row["build_existing_model.misc_pool_pump"] == "0.75 HP Pump":
        return 0.75 * 746 #TODO: Once an estimate has been established we can use Table 430.247 to determine connected load
    return 0

def _special_load_EVSE(row):
    if row["completed_status"] != "Success":
        return np.nan

    if row["build_existing_model.electric_vehicle"] == "None":
        EV_load = 0
    else: 
        EV_load = 7200 # TODO: Insert EV charger load, NEC code says use max of nameplate rating and 7200 W
    return EV_load

# --- aggregated loads ---

def standard_general_load_total(row, n_kit=2, n_ldr=1):
    """Total general load, has tiered demand factors
        General load: 15-20A breaker / branch, 120V

    Args:
        n_kit: int | "auto"
            number of branches for small appliances, minimum 2
        n_ldr: int | "auto"
            number of branches for general laundry load (exclude dryer), minimum 1
    """
    if row["completed_status"] != "Success":
        return np.nan

    general_loads = [
        _general_load_lighting(row),
        _general_load_kitchen(row, n=n_kit),
        _general_load_laundry(row, n=n_ldr),
    ]
    return apply_demand_factor_to_general_load(sum(general_loads))

def standard_fixed_load_total(row):
    """Fastened-In-Place Appliances. NEC 220-17
    Use nameplate rating. Do not include electric ranges, clothes dryers, space-heating or A/C equipment

    Sum(fixed_load) * Demand Factor (1.0 if number of fixed_load < 4 else 0.75)
    In 2020 NEC, only count appliances rated at least 1/4HP or 500W
    """
    if row["completed_status"] != "Success":
        return np.nan

    fixed_loads = np.array(
        [
            _fixed_load_water_heater(row),
            _fixed_load_dishwasher(row),
            _fixed_load_garbage_disposal(row),
            _fixed_load_garbage_compactor(row),
            _fixed_load_hot_tub_spa(row),
            _fixed_load_well_pump(row),
        ]
    )

    n_fixed_loads = len(fixed_loads[fixed_loads >= 500])
    demand_factor = 1 if n_fixed_loads < 4 else 0.75

    return sum(fixed_loads) * demand_factor

def standard_special_load_total(row):
    if row["completed_status"] != "Success":
        return np.nan

    space_cond_load, _ = _special_load_space_conditioning(row)
    special_loads = sum(
        [
            _special_load_electric_dryer(row),
            _special_load_electric_range(row),
            space_cond_load,
            _special_load_motor(row),
            _special_load_pool_heater(row),
            _special_load_pool_pump(row),
            _special_load_EVSE(row)
        ]
    )
    return special_loads

def optional_general_load_total(row, n_kit=2, new_load_calc=False):
    if row["completed_status"] != "Success":
        return np.nan

    general_loads = [
        _general_load_lighting_optm(row),
        _general_load_kitchen(row, n=n_kit),
        _fixed_load_water_heater(row),
        _fixed_load_dishwasher(row),
        _fixed_load_garbage_disposal(row),
        _fixed_load_garbage_compactor(row),
        _special_load_electric_range(row),
        _fixed_load_hot_tub_spa(row),
        _fixed_load_well_pump(row),
        _general_load_laundry(row),
        _special_load_electric_dryer(row),
        _special_load_pool_heater(row),
        _special_load_pool_pump(row),
        _special_load_EVSE(row),
    ]
    if new_load_calc:
        threshold_load=8000 #[VA]
    else:
        threshold_load=10000 #[VA]

    return apply_demand_factor_to_general_load_optm(sum(general_loads), threshold_load=threshold_load)

def optional_special_load_space_conditioning(row, new_load_calc=False):
    if row["completed_status"] != "Success":
        return np.nan

    AC_load = hvac_cooling_conversion(
        row["upgrade_costs.size_cooling_system_primary_k_btu_h"],
        row["build_existing_model.hvac_cooling_type"]
        )

    if row["build_existing_model.hvac_has_ducts"] == "Yes":
            AC_load += hvac_fan_motor + hvac_blower_motor
    
    # TODO: shared efficiency -- if not being counted, remove load from peak
    if ((row["build_existing_model.heating_fuel"] == "Electricity") | (
            "ASHP" in row["build_existing_model.hvac_heating_efficiency"]
            ) | (
            "MSHP" in row["build_existing_model.hvac_heating_efficiency"]
            ) | (
            "GSHP" in row["build_existing_model.hvac_heating_efficiency"]
            ) | (
            "Electric" in row["build_existing_model.hvac_heating_efficiency"]
            ) | (
            "Electricity" in row["build_existing_model.hvac_shared_efficiencies"]
            )): 
        heating_cols = [
            row["upgrade_costs.size_heating_system_primary_k_btu_h"],
            row["upgrade_costs.size_heating_system_secondary_k_btu_h"],
            row["upgrade_costs.size_heat_pump_backup_primary_k_btu_h"]
            ]
        system_cols = [
            row["build_existing_model.hvac_heating_type"],
            row["build_existing_model.hvac_secondary_heating_efficiency"],
            "Electric",
            ]
        fractions = [1, 0.65, 0.65]

        heating_load = sum(
            [hvac_heating_conversion(x, system_type=y)*z for x, y, z in zip(heating_cols, system_cols, fractions)]
        )
    else:
        heating_load = 0
    if row["build_existing_model.hvac_has_ducts"] == "Yes":
        heating_load += hvac_fan_motor
    
    if row["build_existing_model.hvac_has_zonal_electric_heating"] == "Yes":
        # only applies to "Electric Baseboard, 100% Efficiency"
        sep_controlled_heaters = hvac_heating_conversion(
                row["upgrade_costs.size_heating_system_primary_k_btu_h"],
                row["build_existing_model.hvac_heating_type"]
                )
        if new_load_calc:
            demand_factor_sch_less_than_four = 1
        else:
            demand_factor_sch_less_than_four  = 0.65
        demand_factor_sch_four_plus = demand_factor_sch_less_than_four * (0.4/0.65)
        if  int(row["build_existing_model.bedrooms"]) >= 3: # determine number of individually controlled heating units using number of bedrooms, assuming total = # bedrooms + 1
            sep_controlled_heaters *= demand_factor_sch_four_plus
        else: 
            sep_controlled_heaters *= demand_factor_sch_less_than_four
    else:
        sep_controlled_heaters = 0

    continous_heat = 0 # TODO: Determine if we would like to include continuous heat and how to estimate it (NEC 220.82(C)(6) 
    
    space_cond_loads = [
        AC_load , # 100% of AC load (use cooling system primary btu)
        heating_load, # 100% of heating load in absence of supplemental heat or 100% of heating load primary and 65% of secondary or backup heat
        sep_controlled_heaters, # 65% of nameplate of less than 4 seperately controlled heating units, 40% of nameplate of 4 of more seperately controlled heating units
        continous_heat # 100% of electric heat storage or other continuous heating load, assume this to be zero
    ]
    
    return(max(space_cond_loads))


def min_amperage_nec_standard(row, n_kit=2, n_ldr=1):
    """
    Min Amperes for Service - Standard Method
    Min Amperage (A) = Demand Load (total, VA) / Voltage Service (V)
    """
    if row["completed_status"] != "Success":
        return np.nan

    total_demand_load = sum(
        [
            standard_general_load_total(row, n_kit=n_kit, n_ldr=n_ldr),
            standard_fixed_load_total(row),
            standard_special_load_total(row),
        ]
    )  # [VA]

    voltage_service = 240  # [V]

    return total_demand_load / voltage_service


def min_amperage_nec_optional(df, new_load_calc=False):
    """
    Min Amperes for Service - Standard Method
    Min Amperage (A) = Demand Load (total, VA) / Voltage Service (V)
    """
    # Sum _general_load_lighting, _general_load_kitchen and _general_load_laundry, fixed_load_total, _special_load_electric_range
    #  _special_load_hot_tub_spa, _special_load_pool_heater, _special_load_pool_pump, _special_load_well_pump

    if row["completed_status"] != "Success":
        return np.nan

    total_demand_load = sum(
        [
            optional_general_load_total(row, n_kit="auto", new_load_calc=new_load_calc),
            optional_special_load_space_conditioning(row, new_load_calc=new_load_calc),
            ]
    )

    voltage_service = 240  # [V]

    return total_demand_load / voltage_service

def standard_amperage(x):
    """Convert min_amp_col into standard panel size
    http://www.naffainc.com/x/CB2/Elect/EHtmFiles/StdPanelSizes.htm
    """
    if pd.isnull(x):
        return np.nan

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


def get_standard_amperage(df, min_amp_col, standard_amp_col):
    # Convert min_amp_col into standard panel size
    df[standard_amp_col] = df[min_amp_col].apply(lambda x: standard_amperage(x))

    # Clip standard amp for SFD: it is not permitted to size service disconnect below 100 A for SFD (NEC 230.79(C))
    cond = df["build_existing_model.geometry_building_type_recs"]=="Single-Family Detached"
    df.loc[cond, standard_amp_col] = df.loc[cond, standard_amp_col].clip(100)

    return df

def read_file(filename, low_memory=True):
    """ If file is large, use low_memory=False"""
    filename = Path(filename)
    if filename.suffix == ".csv":
        df = pd.read_csv(filename, low_memory=low_memory, keep_default_na=False)
    elif filename.suffix == ".parquet":
        df = pd.read_parquet(filename)
    else:
        raise TypeError(f"Unsupported file type, cannot read file: {filename}")

    return df

def bin_panel_sizes(df_column):
    df_out = df_column.copy()
    df_out.loc[df_column<100] = "<100"
    df_out.loc[(df_column>100) & (df_column<200)] = "101-199"
    df_out.loc[df_column>200] = "200+"
    df_out = df_out.astype(str)

    return df_out

def main(filename: str = None, plot_only=False, sfd_only=False, explode_result=False):
    """ 
    Main execution
    Args :
        filename : input ResStock results file
        plot_only : if true, directly make plots from expected output file
    """
    ext = ""
    if filename is None:
        ext = "_test"
        filename = (
            Path(__file__).resolve().parent
            / "test_data"
            / "euss1_2018_results_up00_400plus.csv" # "euss1_2018_results_up00_100.csv"
        )
    else:
        filename = Path(filename)

    output_filename = filename.parent / (filename.stem + "__nec_panels" + ".csv")

    plot_dir_name = f"plots_sfd{ext}" if sfd_only else f"plots{ext}"
    output_dir = filename.parent / plot_dir_name / "nec_calculations"
    output_dir.mkdir(parents=True, exist_ok=True) 

    if plot_only:
        if not output_filename.exists():
            raise FileNotFoundError(f"Cannot create plots, output_filename not found: {output_filename}")
        df = read_file(output_filename, low_memory=False)
        generate_plots(df, output_dir, sfd_only=sfd_only)
        sys.exit()
        
    df = read_file(filename, low_memory=False)

    # reduce df
    peak_cols = [
                    "report_simulation_output.peak_electricity_summer_total_w",
                    "report_simulation_output.peak_electricity_winter_total_w",
                    "qoi_report.qoi_peak_magnitude_use_kw",
                ]
    cols_to_keep = [
        "building_id", "completed_status", "build_existing_model.sample_weight", 
        "report_simulation_output.unmet_hours_cooling_hr", "report_simulation_output.unmet_hours_heating_hr"
        ]
    cols_to_keep += get_housing_char_cols(search=False, get_ami=False)+peak_cols+[col for col in df.columns if col.startswith("upgrade_costs.")]
    df = df[cols_to_keep]

    # --- [1] NEC - STANDARD METHOD ----
    if explode_result:
        df = apply_standard_method_exploded(df)
    else:
        df = apply_standard_method(df)

    # --- [2] NEC - OPTIONAL METHOD ----
    df = apply_optional_method(df, new_load_calc=False)
        
    # --- compare with simulated peak ---
    df["peak_amp"] = df["qoi_report.qoi_peak_magnitude_use_kw"] * 1000 / 240

    df["std_m_amp_pct_delta"] = np.nan
    cond = df["peak_amp"] > df["std_m_nec_electrical_panel_amp"]
    df.loc[cond, "std_m_amp_pct_delta"] = (
        df["peak_amp"] - df["std_m_nec_electrical_panel_amp"]
    ) / df["std_m_nec_electrical_panel_amp"]

    df["opt_m_amp_pct_delta"] = np.nan
    cond = df["peak_amp"] > df["opt_m_nec_electrical_panel_amp"]
    df.loc[cond, "opt_m_amp_pct_delta"] = (
        df["peak_amp"] - df["opt_m_nec_electrical_panel_amp"]
    ) / df["opt_m_nec_electrical_panel_amp"]

    new_columns = [x for x in df.columns if x not in cols_to_keep]
    print(df.loc[cond, ["building_id"] + new_columns])

    # --- save to file ---
    df.to_csv(output_filename, index=False)
    print(f"File output to: {output_filename}")

    # --- plot ---
    generate_plots(df, output_dir, sfd_only=sfd_only)


def main_existing_load(filename: str = None):
    ext = ""
    if filename is None:
        ext = "_test"
        filename = (
            Path(__file__).resolve().parent
            / "test_data"
            / "euss1_2018_results_up00_400plus.csv" # "euss1_2018_results_up00_100.csv"
        )
    else:
        filename = Path(filename)

    output_filename = filename.parent / (filename.stem + "__existing_load" + ".csv")
        
    df = read_file(filename, low_memory=False)

    # reduce df
    peak_cols = [
                    "report_simulation_output.peak_electricity_summer_total_w",
                    "report_simulation_output.peak_electricity_winter_total_w",
                    "qoi_report.qoi_peak_magnitude_use_kw",
                ]
    cols_to_keep = [
        "building_id", "completed_status", "build_existing_model.sample_weight", 
        "report_simulation_output.unmet_hours_cooling_hr", "report_simulation_output.unmet_hours_heating_hr"
        ]
    cols_to_keep += get_housing_char_cols(search=False, get_ami=False)+peak_cols+[col for col in df.columns if col.startswith("upgrade_costs.")]
    df = df[cols_to_keep]

    # --- NEW LOAD calc: existing loads ---
    # NEC 220.83 - optional method
    new_hvac_loads = pd.Series(False, index=df.index)
    df = apply_existing_load_total_220_83(df, new_hvac_loads, n_kit=2, n_ldr=1)

    # NEC 220.87 - load study
    df = apply_existing_load_total_220_87(df)

    # --- save to file ---
    df.to_csv(output_filename, index=False)
    print(f"File output to: {output_filename}")


def generate_plots(df, output_dir, sfd_only=False):
    plot_output(df, output_dir)
    # plot_output_saturation(df, "std_m_nec_electrical_panel_amp", output_dir, sfd_only=sfd_only)
    # plot_output_saturation(df, "std_m_nec_binned_panel_amp", output_dir, sfd_only=sfd_only)
    # plot_output_saturation(df, "opt_m_nec_electrical_panel_amp", output_dir, sfd_only=sfd_only)
    plot_output_saturation(df, "opt_m_nec_binned_panel_amp", output_dir, sfd_only=sfd_only)


def apply_standard_method(dfi):

        df = dfi.copy()
        df_cols = df.columns

        df["std_m_demand_load_general_VA"] = df.apply(
            lambda x: standard_general_load_total(x, n_kit="auto", n_ldr="auto"), axis=1
        )
        df["std_m_demand_load_fixed_VA"] = df.apply(lambda x: standard_fixed_load_total(x), axis=1)
        df["std_m_demand_load_special_VA"] = df.apply(lambda x: standard_special_load_total(x), axis=1)
        df["std_m_demand_load_total_VA"] = df[["std_m_demand_load_general_VA", "std_m_demand_load_fixed_VA", "std_m_demand_load_special_VA"]].sum(axis=1)

        # df["nec_min_amp"] = df.apply(lambda x: min_amperage_nec_standard(x, n_kit="auto", n_ldr="auto"), axis=1) # this is daisy-ed
        df["std_m_nec_min_amp"] = df["std_m_demand_load_total_VA"] / 240
        df = get_standard_amperage(df, "std_m_nec_min_amp", "std_m_nec_electrical_panel_amp")
        df["std_m_nec_binned_panel_amp"] = bin_panel_sizes(df["std_m_nec_electrical_panel_amp"])

        return df

def apply_standard_method_exploded(dfi):
        
        df = dfi.copy()
        # General Load:
        df["std_m_general_lighting_VA"] = df.apply(lambda row: _general_load_lighting(row), axis=1)
        df["std_m_general_kitchen_VA"] = df.apply(lambda row: _general_load_kitchen(row, n="auto"), axis=1)
        df["std_m_general_laundry_VA"] = df.apply(lambda row: _general_load_laundry(row, n="auto"), axis=1)

        df["std_m_demand_load_general_VA"] = df.apply(
            lambda x: standard_general_load_total(x, n_kit="auto", n_ldr="auto"), axis=1
        )
        # Fixed Load:
        df["std_m_fixed_water_heater_VA"] = df.apply(lambda row: _fixed_load_water_heater(row), axis=1)
        df["std_m_fixed_dishwasher_VA"] = df.apply(lambda row: _fixed_load_dishwasher(row), axis=1)
        df["std_m_fixed_disposal_VA"] = df.apply(lambda row: _fixed_load_garbage_disposal(row), axis=1)
        df["std_m_fixed_compactor_VA"] = df.apply(lambda row: _fixed_load_garbage_compactor(row), axis=1)
        df["std_m_fixed_hot_tub_VA"] = df.apply(lambda row: _fixed_load_hot_tub_spa(row), axis=1)
        df["std_m_fixed_well_pump_VA"] = df.apply(lambda row:  _fixed_load_well_pump(row), axis=1)

        df["std_m_demand_load_fixed_VA"] = df.apply(lambda x: standard_fixed_load_total(x), axis=1)

        # Special Load:
        df["std_m_special_dryer_VA"] = df.apply(lambda row: _special_load_electric_dryer(row), axis=1)
        df["std_m_special_range_VA"] = df.apply(lambda row: _special_load_electric_range(row), axis=1)
        df["std_m_special_space_cond_VA"] = df.apply(lambda row: _special_load_space_conditioning(row)[0], axis=1)
        df["std_m_special_motor_VA"] = df.apply(lambda row: _special_load_motor(row), axis=1)
        df["std_m_special_pool_heater_VA"] = df.apply(lambda row: _special_load_pool_heater(row), axis=1)
        df["std_m_special_pool_pump_VA"] = df.apply(lambda row: _special_load_pool_pump(row), axis=1)
        df["std_m_special_evse_VA"] = df.apply(lambda row: _special_load_EVSE(row), axis=1)

        df["std_m_demand_load_special_VA"] = df.apply(lambda x: standard_special_load_total(x), axis=1)

        # Total
        df["std_m_demand_load_total_VA"] = df[["std_m_demand_load_general_VA", "std_m_demand_load_fixed_VA", "std_m_demand_load_special_VA"]].sum(axis=1)
        df["std_m_nec_min_amp"] = df["std_m_demand_load_total_VA"] / 240
        df = get_standard_amperage(df, "std_m_nec_min_amp", "std_m_nec_electrical_panel_amp")
        df["std_m_nec_binned_panel_amp"] = bin_panel_sizes(df["std_m_nec_electrical_panel_amp"])

        return df

def apply_optional_method(dfi, new_load_calc=False):
        # Sum _general_load_lighting, _general_load_kitchen and _general_load_laundry, fixed_load_total, _special_load_electric_range
        #  _special_load_hot_tub_spa, _special_load_pool_heater, _special_load_pool_pump, _special_load_well_pump

        df = dfi.copy()
        new_load_calc = False
        df_cols = df.columns
        df["opt_m_demand_load_general_VA"] = df.apply(lambda x: optional_general_load_total(x, n_kit="auto", new_load_calc=new_load_calc), axis=1) # 100% of first 10 kVA + 40% additional
        df["opt_m_demand_load_space_cond_VA"] = df.apply(lambda x: optional_special_load_space_conditioning(x, new_load_calc=new_load_calc), axis=1) # compute space conditioning load
        df["opt_m_demand_load_total_VA"] = df[["opt_m_demand_load_general_VA", "opt_m_demand_load_space_cond_VA"]].sum(axis=1)

        df["opt_m_nec_min_amp"] = df["opt_m_demand_load_total_VA"] / 240
        df = get_standard_amperage(df, "opt_m_nec_min_amp", "opt_m_nec_electrical_panel_amp")
        df["opt_m_nec_binned_panel_amp"] = bin_panel_sizes(df["opt_m_nec_electrical_panel_amp"])

        return df


### -------- new load calcs --------
def apply_existing_load_total_220_83(dfi, new_hvac_loads: pd.Series, n_kit=2, n_ldr=1):
    """
    Use NEC 220.83 (A) (has_new_hvac_load=False) for existing + additional new loads calc 
    where additional AC or space-heating IS NOT being installed
    
    Use NEC 220.83 (B) (has_new_hvac_load=True) where additional AC or space-heating IS being installed

    new_hvac_loads: pd.Series indicating where dfi rows has new electric HVAC loads
    """

    df = dfi.copy()
    

    df.loc[new_hvac_loads, "existing_load_total_VA"] = df.loc[new_hvac_loads].apply(lambda x: existing_load_total_220_83(x, n_kit=n_kit, n_ldr=n_ldr, has_new_hvac_load=True), axis=1)
    df.loc[~new_hvac_loads, "existing_load_total_VA"] = df.loc[~new_hvac_loads].apply(lambda x: existing_load_total_220_83(x, n_kit=n_kit, n_ldr=n_ldr, has_new_hvac_load=False), axis=1)
    df["existing_amp_220_83"] = df["existing_load_total_VA"] / 240

    return df


def existing_load_total_220_83(row, n_kit=2, n_ldr=1, has_new_hvac_load=False):
    if row["completed_status"] != "Success":
        return np.nan

    hvac_load, _ = _special_load_space_conditioning(row)

    other_loads = sum(
        [
            _general_load_lighting(row),
            _general_load_kitchen(row, n=n_kit),
            _general_load_laundry(row, n=n_ldr),
            _fixed_load_water_heater(row),
            _fixed_load_dishwasher(row),
            _fixed_load_garbage_disposal(row),
            _fixed_load_garbage_compactor(row),
            _fixed_load_hot_tub_spa(row),
            _fixed_load_well_pump(row),
            _special_load_electric_dryer(row),
            _special_load_electric_range_nameplate(row),
            _special_load_pool_heater(row),
            _special_load_pool_pump(row),
            _special_load_EVSE(row)
        ]
    ) # no largest motor load

    threshold_load = 8000 # kVA
    if has_new_hvac_load:
        # 100% HVAC load + 100% of 1st 8kVA other_loads + 40% of remainder other_loads
        total_loads = hvac_load + apply_demand_factor_to_general_load_optm(other_loads, threshold_load=threshold_load)

    else:
        # 100% of 1st 8kVA all loads + 40% of remainder loads
        total_loads = apply_demand_factor_to_general_load_optm(hvac_load + other_loads, threshold_load=threshold_load)

    return total_loads


def apply_existing_load_total_220_87(df):
    df["existing_amp_220_87"] = df["qoi_report.qoi_peak_magnitude_use_kw"] * 1000 / 240 * 1.25 # amp
    df.loc[df["build_existing_model.vacancy_status"]=="Vacant", "existing_amp_220_87"] = np.nan

    return df


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
    parser.add_argument(
        "-x",
        "--explode_result",
        action="store_true",
        default=False,
        help="Whether to export intermediate calculations as part of the results",
    )
    parser.add_argument(
        "-e",
        "--existing_load",
        action="store_true",
        default=False,
        help="Run NEC 220.83 and 220.87 for existing load calculations, overrides all other flags",
    )

    args = parser.parse_args()

    if args.existing_load:
        main_existing_load(args.filename)
    else:
        main(args.filename, plot_only=args.plot_only, sfd_only=args.sfd_only, explode_result=args.explode_result)

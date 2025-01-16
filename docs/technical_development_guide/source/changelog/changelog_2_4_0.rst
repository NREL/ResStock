================
v2.4.0 Changelog
================

.. changelog::
    :version: v2.4.0
    :released: 2021-01-27

    .. change::
        :tags: workflow, envelope, bugfix
        :pullreq: 537

        **Date**: 2021-01-26

        Title:
        Fix: Effective R Value Calculation for HVAC Sizing

        Description:
        Calculate slab surface effective R values used in HVAC sizing with unit-level variables.
        Fixes how the effective R value of a slab is calculated for use in the HVAC sizing measure. The effective R values were previously calculated use the slab area of the entire building footprint and the exposed perimeter of the individual unit, causing the R value to scale incorrectly with larger buildings. This calculates the R value using variables specific to the unit, not the building.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 525

        **Date**: 2021-01-20

        Title:
        Feature/weather infrastructure

        Description:
        Allow for flexible weather regions based on weather data available and introduce TMY3 weather files for the new weather format.
        This PR generalizes the weather data available for a given AMY or TMY analysis. ResStock currently uses 941 static weather stations. The stations are used based on the Location.tsv.

        resstock-estimation: `pull request 95 <https://github.com/NREL/resstock-estimation/pull/95>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, weather, bugfix
        :pullreq: 530

        **Date**: 2021-01-20

        Title:
        Bugfix for DST start hour and end date.

        Description:
        Fix DST start hour error and end date error.
        The PR fixes 2 issues with the current calculation of DST time column.
        Currently, DST spring forward occurs at 1:00 AM standard time. The time jumps from 0:59 to 2:00. It should jump from 1:59 to 3:00 instead. This fixes the problem.
        The DST end date is currently one day behind what's specified in the options_lookup or weather file. This PR also fixes that.
        The clocks are supposed to shift back by one hour at 2:00 AM on the same date as DST end date. See https://www.timeanddate.com/time/change/usa.

        Assignees: Rajendra Adhikari


    .. change::
        :tags: workflow, ducts, feature
        :pullreq: 532

        **Date**: 2021-01-13

        Title:
        Update duct related calcs in airflow.rb

        Description:
        Update the duct leakage "total" to "to outside" conversion to be based on ASHRAE Standard 152.
        Addresses https://trello.com/c/VmcGehGM/62-duct-leakage-total.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, weather, bugfix
        :pullreq: 528

        **Date**: 2021-01-11

        Title:
        Change to UTC time calculations to avoid DST messing things up

        Description:
        Fix bug related to incorrect timestamps when using AMY weather file.
        Resolves the issue of timestamps being incorrect around the DST switchover time when using AMY weather files.

        Assignees: Rajendra Adhikari


    .. change::
        :tags: workflow, heat pumps, feature
        :pullreq: 512

        **Date**: 2021-01-07

        Title:
        Report supplemental electric heating

        Description:
        Separate heat pump electric supplemental heating from total electric heating in output reporting.
        Break "supplemental electric heating" out of "electric heating".
        This is important for heat pump analysis.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 522

        **Date**: 2021-01-07

        Title:
        Fix: All buildings have double-loaded corridors

        Description:
        In the Corridor.tsv, assign single-family attached, single-family detached, and mobile homes with a "Not Applicable" option.
        In the project_national/housing_characteristics/Corridor.tsv, all buildings are assigned a "Double-Loaded Corridor." However, the single-family detached, mobile homes, and single-family attached buildings do not have corridors. For single-family detached, mobile homes, and single-family attached buildings, measures/BuildExistingModel/measure.rb removes the calls to the ResidentialGeometryCreateMultifamily measure.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, vacancy, bugfix
        :pullreq: 527

        **Date**: 2021-01-07

        Title:
        Make sure vacant units have zero ceiling fan energy

        Description:
        Remove ceiling fan energy for vacant units.
        Vacant units currently have ceiling fan energy. This PR introduces an option where the ceiling fan energy is zero. The ratio of ceiling fans is kept the same, so 72% of units have ceiling fans for either occupied or vacant units. This ensures the counts of ceiling fans are consistent, but vacant units have no ceiling fan energy.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 523

        **Date**: 2020-12-23

        Title:
        Fix surface area reporting for collapsed buildings

        Description:
        Fix for calculating door and below-grade wall area of multifamily and single-family attached buildings with collapsed geometries.
        Fixes below grade wall and door area calculations in SimulationOutputReport when minimal_collapsed = true for MF and SFA buildings. Previously, units_represented was not used to scale foundation wall or door area, and therefore areas were underestimated when building geometries were collapsed.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, water heater, feature
        :pullreq: 513

        **Date**: 2020-12-10

        Title:
        Feature/water heater update

        Description:
        Introduce premium water heaters and heat pump water heaters into building stock, differentiate between central and in-unit water heating, and split water heater fuel and efficiency into different housing characteristics.
        This pull request updates the water heater housing characteristics.

        resstock-estimation: `pull request 87 <https://github.com/NREL/resstock-estimation/pull/87>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 518

        **Date**: 2020-12-10

        Title:
        Account for collapsed units when determining geometry variables for infiltration calculation

        Description:
        Account for collapsed units when determining geometry variables (building floor/wall area and volume) in infiltration calculations; add airflow unit tests.
        Fixes how geometry variables (building ffa, building volume, and building exterior wall area) are calculated in the Airflow.rb measure when minimal_collapsed == True. The "collapsed" units were not originally accounted for when determining these variables, influencing the calculated leakage area at each unit. This changes the infiltration and HVAC sizing in SFA buildings, and most likely MF buildings as well.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, plug loads, feature
        :pullreq: 511

        **Date**: 2020-11-22

        Title:
        Multiplier updates to plug load measure

        Description:
        Allow for plug load energy consumption to vary by Census Division and include additional "diversity" multiplier in plug load equations.
        This pull request separates out multipliers meant to adjust total energy and multipliers meant to adjust diversity of the results. The ResidentialMiscPlugLoads argument mult has been split into two multipliers (energy_mult and diversity_mult).
        The energy multiplier now allows the plug load energy use to vary with building type and RECS 2015 definition of Census Division (the Mountain division is split into North and South).
        The diversity_mult argument is simply the same as the previous definition of mult.

        resstock-estimation: `pull request 86 <https://github.com/NREL/resstock-estimation/pull/86>`_

        Assignees: Joe Robertson, Anthony Fontanini


    .. change::
        :tags: characteristics, lighting, feature
        :pullreq: 510

        **Date**: 2020-11-22

        Title:
        Add spatial and building type dependencies to lighting saturations

        Description:
        Lighting saturations based on RECS 2015 with new building type and spatial dependencies.
        This pull request updates the Lighting.tsv to include dependencies on building type and RECS 2015 definition of Census Division. The RECS 2015 definition of Census division is similar to the U.S. Census definition, except RECS breaks out the Mountain Census Division into a North and South Subdivision.

        resstock-estimation: `pull request 84 <https://github.com/NREL/resstock-estimation/pull/84>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, appliances, bugfix
        :pullreq: 504

        **Date**: 2020-11-22

        Title:
        Add monthly multiplier for cooking, clothes washer, clothes dryer, and dishwasher

        Description:
        Reintroduce monthly multipliers with stochastic load model for dishwasher, clothes washer and clothes dryer and cooking.
        The cooking schedule was previously (before the ResidentialScheduleGenerator was introduced) generated using weekend, weekday, and monthly multiplier schedule. Currently, they are generated using the Markov-chain by the ResidentialScheduleGenerator. This pull request adds monthly multipliers to the schedule so generated.

        Assignees: Rajendra Adhikari


    .. change::
        :tags: characteristics, occupants, feature
        :pullreq: 509

        **Date**: 2020-11-16

        Title:
        Number of occupants based on PUMS

        Description:
        Update Occupants per unit from RECS 2015 to PUMS 5-yr 2017.
        This pull request updates the number of occupants (that gets passed into the stochastic load generator) from RECS 2015 to PUMS 5-yr 2017. The switch to PUMS allows PUMA level spatial granularity in the distributions and leverages more than 6 million samples.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 507

        **Date**: 2020-11-13

        Title:
        ResStock/ComStock weather syncronization

        Description:
        Synchronize weather between ResStock and ComStock which increases the number of weather stations from 215 to 941.
        This pull request synchronizes the weather files for both ResStock and ComStock. Currently, ResStock uses 215 weather regions defined by county. ComStock uses 941 weather files also defined by county. For applications (especially GEB applications) where combined results from ResStock and ComStock are desired, it is important that the residential and commercial models use the same weather data. This way both residential and commercial models respond to hot days, cold days, rainy days together to predict more accurate combined loads.

        resstock-estimation: `pull request 58 <https://github.com/NREL/resstock-estimation/pull/58>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 492

        **Date**: 2020-11-10

        Title:
        Update Geometry Foundation Type to be Based on RECS

        Description:
        Update foundation type from the [Building Foundation Design Handbook](https://www.osti.gov/biblio/6980439-building-foundation-design-handbook) published in 1988 to RECS 2009.
        This pull request updates the Geometry Foundation Type.tsv from the "Building Foundation Design Handbook" published in 1988 to RECS 2009. The new TSV has dependencies on IECC Climate and Moisture regions and Vintage ACS.

        resstock-estimation: `pull request 63 <https://github.com/NREL/resstock-estimation/pull/63>`_, `pull request 73 <https://github.com/NREL/resstock-estimation/pull/73>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, climate zones, bugfix
        :pullreq: 497

        **Date**: 2020-11-10

        Title:
        Add IECC zone dependency to HVAC Cooling Type and some minor heat pump fixes

        Description:
        Reintroduce IECC climate zone dependency to HVAC Cooling Type and some heat pump fixes.
        Addresses #64 by adding IECC zone as a dependency. Lumping some of the other dependencies to bring up sample sizes. Increased from ~47% to 60% rows with fewer than 10 samples, but overall I think it is a net improvement.

        resstock-estimation: `pull request 67 <https://github.com/NREL/resstock-estimation/pull/67>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, internal gains, bugfix
        :pullreq: 501

        **Date**: 2020-10-27

        Title:
        Internal gain calcs for sizing updates/fixes

        Description:
        For the purpose of calculating cooling and dehumidification loads for HVAC sizing, use simple internal gains equation from ANSI/RESNET/ICC 301 (consistent with HPXML workflow); this fixes a bug introduced in [#348](https://github.com/NREL/resstock/pull/348) that caused cooling capacities to be ~3x larger than they should be.
        Updates to be consistent with how the hpxml workflow processes internal gains.

        Assignees: Joe Robertson


    .. change::
        :tags: mechanics, envelope, bugfix
        :pullreq: 496

        **Date**: 2020-10-07

        Title:
        Update partition wall area calculation for MF and SFA buildings

        Description:
        Exclude existing shared walls when calculating the partition wall area of MF and SFA buildings.
        Updates how partition wall surface area is calculated so that shared walls in MF and SFA buildings do not count as existing partition wall mass. This means that MF and SFA building partition walls are now calculated the same as SFD buildings - as a direct proportion of the finished floor area.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, vacancy, bugfix
        :pullreq: 486

        **Date**: 2020-09-24

        Title:
        Fix/vacant units

        Description:
        Update spatial distribution of units based on total dwelling unit counts rather than occupied unit counts.
        After talking with @TobiAdekanye, we realized that the spatial distribution of dwelling units are based on only the occupied dwelling units. When the vacant units were pulled into ResStock, the TSV creation functions in sources/spatial/tsv_maker.py in the resstock-estimation repository should have been updated to acs_count instead of acs_occupied_count. This was an oversight when I merged in the Vacant Units.

        resstock-estimation: `pull request 56 <https://github.com/NREL/resstock-estimation/pull/56>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, envelope, feature
        :pullreq: 485

        **Date**: 2020-09-23

        Title:
        Roofing material options and tsvs updates

        Description:
        Increase roofing material options; update roofing material tsv files to include these new options.
        Expand roof material options and update related tsv files.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 478

        **Date**: 2020-09-09

        Title:
        HVAC tsv restructuring

        Description:
        Restructure HVAC housing characteristics to 1) simplify the structure, 2) allow for integrating more local data sources, 3) update reference years for HVAC and refrigerator ages and efficiencies from 2009 to 2018, 4) add assumption comments to all HVAC-related housing characteristics, 5) improve Room AC efficiency distributions using ENERGY STAR saturation data, and 6) fix some incorrect assignment of Option=None heating systems.
        We have an inordinate number of tsvs presently describing the hvac systems in OpenStudio-BuildStock. This PR reorders and merges existing hvac tsvs while preserving the necessary interactions. The major changes to structure are to move from multiple heating fuel-specific efficiency TSV files to a single TSV for heating efficiencies. The "Is Heat Pump" TSV is also expanded to include ducted/non-ducted options for use as an interim dependency.

        resstock-estimation: `pull request 32 <https://github.com/NREL/resstock-estimation/pull/32>`_

        Assignees: Tobi Adekanye, Eric Wilson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 480

        **Date**: 2020-08-18

        Title:
        Addresses #479, garage zone infiltration not always added to model

        Description:
        Iterate all spaces in a thermal zone when checking for zone type; fixes missing infiltration for protruding garages in 1-story homes.
        For 1-story, SFD homes with protruding garages, we expect an effective leakage area object added to the model for the garage and garage attic spaces, as shown below. However, these only get added about half of the time.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, vacancy, feature
        :pullreq: 473

        **Date**: 2020-08-17

        Title:
        Introduce Vacant Units

        Description:
        Distinguish between vacant and occupied dwelling units using PUMS data.
        The purpose of the pull request is to introduce vacant units into the residential stock. This work was motivated by the following maps that shows the fraction of vacant units by building type and PUMA.

        resstock-estimation: `pull request 36 <https://github.com/NREL/resstock-estimation/pull/36>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, schedules, bugfix
        :pullreq: 477

        **Date**: 2020-08-13

        Title:
        Addresses #476, appliance design levels fluctuate between runs

        Description:
        Fix for pseudo-random number generator that was generating non-deterministic occupancy schedules
        Fixes an issue with sampling an integer without using the pseudo-random number generator seed.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, plug loads, feature
        :pullreq: 471

        **Date**: 2020-08-11

        Title:
        Separate plug load equations for SFD, SFA, MF

        Description:
        Based on RECS 2015, separate the plug load equations for single-family detached, single-family attached, and multifamily buildings.
        Using RECS 2015 a multilinear regression is performed to determine the annual MELS for ResStock. The dependent variables are the number of occupants (noccupants) and the finished floor area (ffa) of the dwelling unit. The MELS definition is a combination of microwave, television, humidifiers, and other devices. The RECS fields for these variables are KWHMICRO, KWHTVREL, KWHHUM, and KWHNEC, respectively.

        resstock-estimation: `pull request 45 <https://github.com/NREL/resstock-estimation/pull/45>`_

        Assignees: Joe Robertson, Anthony Fontanini


    .. change::
        :tags: characteristics, setpoints, feature
        :pullreq: 468

        **Date**: 2020-08-10

        Title:
        Update Setpoint and Setpoint Schedule Distributions

        Description:
        Update the dependencies for heating and cooling setpoint tsvs (Setpoint, Has Offset, Offset Magnitude, and Offset Period) to IECC climate zone.
        Updates the thermostat heating and cooling setpoint distributions (setpoint, has offset, offset magnitude, offset schedule) to be dependent on IECC climate zone instead of AIA zone.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, heating fuel, feature
        :pullreq: 474

        **Date**: 2020-08-10

        Title:
        Feature/heating fuel puma

        Description:
        Update heating fuel distributions to be by Public Use Microdata Area (PUMA) rather than State.
        This pull request modifies the state level description of Heating Fuel type to PUMA. See the graphics below for modifications of heating fuel types. The data is based on PUMS 5-yr 2016, and for sample sizes that are less than 10, the state average is used.

        resstock-estimation: `pull request 49 <https://github.com/NREL/resstock-estimation/pull/49>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, schedules, feature
        :pullreq: 348

        **Date**: 2020-07-16

        Title:
        Generate schedule csv on the fly and use Schedule:File objects on its columns

        Description:
        Major change to most occupant-related schedules. Occupant activities are now generated on-the-fly and saved to .csv files used by Schedule:File objects. Schedules are generated using time-inhomogenous Markov chains derived from American Time Use Survey data, supplemented with sampling duration and power level from NEEA RBSA data, as well as DHW draw duration and flow rate data from Aquacraft/AWWA data [(see pre-print for details)](https://arxiv.org/abs/2111.01881).
        The Stochastic Occupancy Modelling introduces major change to most occupant-related schedules. Occupant activities are now generated on-the-fly and saved to .csv files used by Schedule:File objects. Schedules are generated using time-inhomogenous Markov chains derived from American Time Use Survey data, supplemented with sampling duration and power level from NEEA RBSA data, as well as DHW draw duration and flow rate data from Aquacraft/AWWA data.

        Assignees: Joe Robertson, Rajendra Adhikari


    .. change::
        :tags: workflow, quantities of interest, feature
        :pullreq: 460

        **Date**: 2020-07-08

        Title:
        Report peak kw

        Description:
        Report the annual peak use and timing using the quantities of interest measure.
        Report peak use and timing using the QOIReport measure.

        Assignees: Joe Robertson



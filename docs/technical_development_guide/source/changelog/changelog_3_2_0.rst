================
v3.2.0 Changelog
================

.. changelog::
    :version: v3.2.0
    :released: 2023-12-19

    .. change::
        :tags: workflow, weather, bugfix
        :pullreq: 1182

        **Date**: 2023-12-18

        Title:
        Update weather files from NREL Data Catalog

        Description:
        Update TMY3 weather URL from the NREL Data Catalog.
        The current link in the project YAMLs for the TMY weather files in NREL Data Catalog is out of date and missing the following Counties. This PR updates the link to the latest file on the NREL Data Catalog.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, gshp, feature
        :pullreq: 1187

        **Date**: 2023-12-10

        Title:
        Geothermal loop & soil properties

        Description:
        Updates and enhancements to the ground source heat pump model; ability to describe detailed geothermal loop inputs.
        Allow inputs to describe a ground-source heat pump field (e.g., vertical vs horizontal, bore/trench length, etc.).

        OpenStudio-HPXML: `pull request 1391 <https://github.com/NREL/OpenStudio-HPXML/pull/1391>`_

        Assignees: Prateek Shrestha, Jeff Maguire, Anthony Fontanini, Joe Robertson


    .. change::
        :tags: characteristics, ground conductivity, feature
        :pullreq: 1165

        **Date**: 2023-12-04

        Title:
        Add variability in ground thermal conductivity

        Description:
        Add variability in ground thermal conductivity.
        Allow ground conductivity to vary by climate zone. The GeoVision task force report provided data by climate zone. The same data is used to fill out distributions by climate zone.

        resstock-estimation: `pull request 393 <https://github.com/NREL/resstock-estimation/pull/393>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: documentation, resstockarguments, feature
        :pullreq: 1146

        **Date**: 2023-11-27

        Title:
        RTD: summarize lookup arguments

        Description:
        Automate creation of new "Arguments" documentation sections for summarizing arguments (and their default values) in options_lookup.tsv.
        By housing characteristic parameter, automates summarizing Arguments sets used in options_lookup.tsv (including Name, Required, Units, Type, Choices, Description). See below for example.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, data sources, bugfix
        :pullreq: 1164

        **Date**: 2023-11-10

        Title:
        Update to RECS 2020 V5 data files

        Description:
        Update to RECS 2020 V5 data files.
        Use RECS 2020 V5 microdata file to create the characteristics. There is very little impact as the update to RECS 2020 V5 is mainly adding columns with end-use energy and expenditures. There are some very small changes to some TSVs, but these changes result in no changes to the options_saturation file.

        resstock-estimation: `pull request 392 <https://github.com/NREL/resstock-estimation/pull/392>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: software, openstudio, feature
        :pullreq: 1144

        **Date**: 2023-10-26

        Title:
        Latest OS-HPXML, OS v3.7.0

        Description:
        Update to OpenStudio 3.7.0/EnergyPlus 23.2.0.

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: workflow, utility bills, feature
        :pullreq: 1109

        **Date**: 2023-10-24

        Title:
        Calculate detailed utility bills

        Description:
        Add ability to calculate detailed utility bills based on a user-specified TSV file of paths to JSON utility rate tariff files.
        Add optional detailed_filepath yml argument for pointing to user-specified TSV file of electricity tariff file paths. The TSV file can contain electricity tariff file paths mapped by State, or any other parameter.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, resilience, feature
        :pullreq: 1113

        **Date**: 2023-10-23

        Title:
        Add resilience arguments to yml files

        Description:
        Add ability to request timeseries resilience output from the yml file.
        Include the new include_timeseries_resilience argument in example yml files.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, water heater, feature
        :pullreq: 1125

        **Date**: 2023-09-25

        Title:
        Add water heater location

        Description:
        Add Water Heater Location and Geometry Space Combination, update Geometry Garage and Geometry Floor Area Bin to RECS2020, update RECS2020 microdata from v2 to v4, auto-generate buildstocks for yml_precomputed tests.
        Added Water Heater Location.tsv.

        resstock-estimation: `pull request 385 <https://github.com/NREL/resstock-estimation/pull/385>`_

        Assignees: Lixi Liu


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 1138

        **Date**: 2023-09-20

        Title:
        run_analysis.rb: handle illegal upgrade names, provide run folder map

        Description:
        Update `run_analysis.rb` to handle illegal path characters in upgrade names.
        run_analysis.rb creates directories based on upgrade names, but these upgrade names may have illegal path characters in them (e.g., "/" if the upgrade name is "Higher efficiency ducted ASHP w/ elec backup "), resulting in an obscure error. It should more gracefully handle this situation and be able to run upgrades with these characters in the name.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 1138

        **Date**: 2023-09-20

        Title:
        run_analysis.rb: handle illegal upgrade names, provide run folder map

        Description:
        Update `run_analysis.rb` to map datapoints to run folder names when the `-k` argument is supplied.
        Also, adds writing run folder names (e.g., "run1", "run2", etc.) to the "job_id" column when supplying the -k argument to run_analysis.rb (i.e., a map from datapoint to run folder).

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, setpoints, bugfix
        :pullreq: 1136

        **Date**: 2023-09-11

        Title:
        Update TSVs after bugfix

        Description:
        Minor changes to heating and cooling setpoint TSV after a bug fix.
        Fix an elusive bug that causes a slight changes on the Heating Setpoint and Cooling Setpoint TSV on each run. This bug was a result of previous PR of refactoring prune_rules.

        resstock-estimation: `pull request 388 <https://github.com/NREL/resstock-estimation/pull/388>`_

        Assignees: Rajendra Adhikari


    .. change::
        :tags: characteristics, setpoints, bugfix
        :pullreq: 1132

        **Date**: 2023-09-06

        Title:
        TSV changes from prune_rules refactor and adding options_saturations.csv

        Description:
        Minor changes to heating and cooling setpoint TSV due to refactoring of prune_rules handling in resstock-estimation.
        Attempt at fixing ongoing issue with unexpected behavior of prune rules in #385 by refactoring and simplifying prune rule handling.

        resstock-estimation: `pull request 386 <https://github.com/NREL/resstock-estimation/pull/386>`_

        Assignees: Rajendra Adhikari


    .. change::
        :tags: characteristics, general, feature
        :pullreq: 1132

        **Date**: 2023-09-06

        Title:
        TSV changes from prune_rules refactor and adding options_saturations.csv

        Description:
        options_saturations.csv is added to project_*/resources/ folder.
        Also add options_saturations.csv to resources.

        resstock-estimation: `pull request 386 <https://github.com/NREL/resstock-estimation/pull/386>`_

        Assignees: Rajendra Adhikari


    .. change::
        :tags: characteristics, refrigerator, bugfix
        :pullreq: 1118

        **Date**: 2023-08-23

        Title:
        change refrigerator rated annual kwh

        Description:
        Correct refrigerator rated annual kWh based on EF and an assumed volume of 20.9cft.
        Change the rated annual consumption of refrigerator and misc extra refrigerator in options_lookup.tsv.

        Assignees: Lixi Liu


    .. change::
        :tags: workflow, heat pumps, feature
        :pullreq: 1074

        **Date**: 2023-08-18

        Title:
        Heating system -> heat pump backup

        Description:
        For heat pump upgrades, adds the ability to set the existing primary (non-shared) heating system as the backup system using only a single option from the lookup.
        Uses ResStockArguments to add a new boolean argument heat_pump_backup_use_existing_system.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, ducts, bugfix
        :pullreq: 1104, 1112

        **Date**: 2023-08-09

        Title:
        add Duct Location and Duct Leakage to Outside

        Description:
        Fix/clarify duct location assignment by defining Duct Location.tsv, making Duct Leakage and Insulation (formerly Duct) depend on Duct Location, and making HVAC Has Ducts depend on HVAC Has Shared Systems. Includes fixes on standalone and shared heating system assignment for Other Fuel.
        Added Duct Location.tsv.
        Replaced Duct.tsv with Duct Leakage and Insulation.tsv.
        Added "HVAC Has Shared System" as dependency to HVAC Has Ducts.tsv.
        Fixed HVAC Shared Efficiencies.tsv.
        Fixed HVAC Heating Efficiency.tsv.

        resstock-estimation: `pull request 377 <https://github.com/NREL/resstock-estimation/pull/377>`_

        Assignees: Lixi Liu, Joe Robertson


    .. change::
        :tags: characteristics, floor area, bugfix
        :pullreq: 1115

        **Date**: 2023-08-07

        Title:
        Typo for square feet area of multi-family

        Description:
        Fix square footage for a MF dwelling unit in the "3000-3999" CFA bin (from 33171 to 3171).
        This shows square footage for an MF housing bin of 3000-3999 to be 33171. I assume this is incorrect and a typo, but should be a quick fix.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, secondary heating, feature
        :pullreq: 1093

        **Date**: 2023-07-17

        Title:
        HVAC Secondary Heating, try 2

        Description:
        Include HVAC secondary heating capabilities for project_testing.
        Support options sampled from HVAC Secondary Heating xxx.

        resstock-estimation: `pull request 375 <https://github.com/NREL/resstock-estimation/pull/375>`_

        OpenStudio-HPXML: `pull request 1414 <https://github.com/NREL/OpenStudio-HPXML/pull/1414>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, secondary heating, bugfix
        :pullreq: 1093

        **Date**: 2023-07-17

        Title:
        HVAC Secondary Heating, try 2

        Description:
        Update ResStockArguments to support nonzero fraction of heat load served by the secondary heating system.
        Update the ResStockArguments measure to adjust the primary system's fraction of heat load served such that the sum of fractions does not exceed 1.0.

        resstock-estimation: `pull request 375 <https://github.com/NREL/resstock-estimation/pull/375>`_

        OpenStudio-HPXML: `pull request 1414 <https://github.com/NREL/OpenStudio-HPXML/pull/1414>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, other fuel, bugfix
        :pullreq: 947

        **Date**: 2023-07-11

        Title:
        Model wood fuel when sampling "Other Fuel" for WH and "Other" for HVAC

        Description:
        Model a wood storage water heater when "Other Fuel" is sampled from Water Heater Efficiency.tsv (allowing downstream modeling of clothes washer/dryer). Similarly, model a wood wall/floor furnace when "Other" is sampled from HVAC Heating Efficiency.tsv.
        Water Heater Efficiency|Other Fuel to model a wood storage water heater instead of no water heater.
        HVAC Heating Efficiency|Other to model a wood wall/floor furnace instead of no heating system.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, formatting, bugfix
        :pullreq: 962

        **Date**: 2023-06-26

        Title:
        Clean up options_lookup.tsv in github actions

        Description:
        Set standard format for options_lookup.
        In an effort to clean up resources/options_lookup.tsv, this sets a standard for what the file should look like.

        Assignees: Rajendra Adhikari, Anthony Fontanini


    .. change::
        :tags: workflow, utility bills, feature
        :pullreq: 1012

        **Date**: 2023-06-12

        Title:
        Simple bill calcs (enhancement)

        Description:
        Add ability to calculate simple utility bills based on a user-specified TSV file of utility rates.
        Add optional simple_filepath yml argument for pointing to user-specified TSV file of utility rates. The TSV file can contain utility rates mapped by State, or any other parameter.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, data sources, feature
        :pullreq: 1031

        **Date**: 2023-06-08

        Title:
        Update to RECS 2020 data

        Description:
        Update characteristics to use EIA 2020 RECS.
        Transitioning characteristics to use the EIA's 2020 RECS survey final characteristics.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, emissions, feature
        :pullreq: 1038

        **Date**: 2023-06-07

        Title:
        Update to 2022 Cambium release

        Description:
        Add 2022 Cambium emissions data.
        Cambium 2022 data is out. This issue is to update to the 2022 data.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, climate zones, feature
        :pullreq: 1080

        **Date**: 2023-06-06

        Title:
        Ll/energystar climate zones

        Description:
        Add Energystar Climate Zone for window upgrade specification.

        resstock-estimation: `pull request 369 <https://github.com/NREL/resstock-estimation/pull/369>`_

        Assignees: Lixi Liu



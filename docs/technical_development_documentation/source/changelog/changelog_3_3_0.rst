================
v3.3.0 Changelog
================

.. changelog::
    :version: v3.3.0
    :released: 2024-07-24

    .. change::
        :tags: workflow, refactor, bugfix
        :pullreq: 1277

        **Date**: 2024-07-22

        Title:
        ServerDirectoryCleanup: catch \*schedules.csv, refactor

        Description:
        Remove duplicate measure code.
        Catch \*schedules.csv since OS-HPXML generates in.schedules.csv.
        Remove "retain_in_idf: false" from national project yml files; appears that even if you delete in.idf from ServerDirectoryCleanup, the file is still subsequently exported (by the openstudio workflow?).

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 1275

        **Date**: 2024-07-20

        Title:
        Specify upgrade_names for run_analysis.rb

        Description:
        Introduce a new optional upgrade_name argument (can be called multiple times) to run_analysis.rb.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, feature, utility bills
        :pullreq: 1246

        **Date**: 2024-07-19

        Title:
        Latest OS-HPXML, v1.8.1

        Description:
        Add new project yml file arguments for reporting/controlling annual/monthly utility bill outputs.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, changed, utility bills
        :pullreq: 1246

        **Date**: 2024-07-19

        Title:
        Latest OS-HPXML, v1.8.1

        Description:
        Updates default fuel prices to use 2022 EIA State Energy Data System (SEDS) instead of state-averages.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, bugfix, temperature capacitance multiplier
        :pullreq: 1246

        **Date**: 2024-07-19

        Title:
        Latest OS-HPXML, v1.8.1

        Description:
        Update to use the new temperature capacitance multiplier of 7.0 after some resilience application investigation.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, refactor, bugfix
        :pullreq: 1253

        **Date**: 2024-07-19

        Title:
        Convert UpgradeCosts measure to ModelMeasure

        Description:
        UpgradeCosts does not need to be a reporting measure; it doesn't actually report any simulation output.
        ReportHPXMLOutput does not need to be its own measure; it can be pulled into UpgradeCosts.

        If UpgradeCosts becomes a model measure, it gets applied before simulation time and therefore its registered values would show up in the results.csv when using the measures_only flag.

        This also fixes a bug related to using the measure_only flag.
        When using measure_only, the results.json file is not produced.
        Therefore, no registered values would show up in the results csv.
        Now we use data_point_out.json, which is produced when using measures_only.

        Update buildstock.rb and sample yml files with workflow generator version tag.
        This enables us to point to buildstockbatch's develop branch for CI tests.

        buildstockbatch: `pull request 458 <https://github.com/NREL/buildstockbatch/pull/458>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, refactor
        :pullreq: 1269

        **Date**: 2024-07-15

        Title:
        ResStockArguments: convert args to double, integer

        Description:
        Avoids a bug that would be introduced by making air_leakage_value optional in https://github.com/NREL/OpenStudio-HPXML/pull/1760.
        Per suggestion by @shorowit, create a method for automatically converting ResStockArguments argument data types based on original argument type.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, bugfix, geometry
        :pullreq: 1258

        **Date**: 2024-06-21

        Title:
        Reduce garage protrusion slightly for 0-499 Geometry Floor Area

        Description:
        For the "0-499" Geometry Floor Area option, change the garage protrusion from 0.75 to 0.72.
        This avoids the "Garage is as wide as the single-family detached unit." error.

        Assignees: Joe Robertson


    .. change::
        :tags: documentation, changelog, feature
        :pullreq: 1244

        **Date**: 2024-06-12

        Title:
        RTD: detailed changelog

        Description:
        Adopt changelog approach from buildstockbatch.

        Assignees: Joe Robertson
    

    .. change::
        :tags: documentation, options_lookup, feature
        :pullreq: 1249

        **Date**: 2024-06-04

        Title:
        Adding options and option arguments to Read the Docs

        Description:
        Adding to the read the docs documentation by articulating the options in project national and the arguments specified. One can now look at the descriptions of the arguments and documentation linked to OS-HPXML and see what arguments are currently being used in the baseline stock.
        The updates combines two files automatically: "options_lookup.tsv" and the "project_national/resuources/options_saturations.csv".

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, plug loads, feature
        :pullreq: 1213
        :tickets: 1206

        **Date**: 2024-05-21

        Title:
        Split out Other and TV plug loads

        Description:
        Split out TV plug loads (calculated using an equation based on ANSI/RESNET/ICC 301) from other plug loads (calculated using updated regression equations based on RECS2020).
        For TV, we are now using OS-HPXML defaults (i.e., TV = 413.0 + 69.0 * NumberofBedrooms based on ANSI/RESNET/ICC 301-2019, where NumberofBedrooms is adjusted based on NumberofResidents).
        Create a new sources/recs/recs2020/plug_loads/mel_ann.py script.

        resstock-estimation: `pull request 401 <https://github.com/NREL/resstock-estimation/pull/401>`_

        Assignees: Joe Robertson, Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 1230
        :tickets: 1130

        **Date**: 2024-05-16

        Title:
        Run run_analysis in parallel

        Description:
        Introduce a new optional `buildstock_csv_path` argument that supports parallel resstock runs using `run_analysis.rb`.
        I know this is an odd workflow, but I'd like to call resstock in parallel, to run multiple models (baseline only) built each with a precomputed buildstock.csv.

        Assignees: Julien Marrec


    .. change::
        :tags: workflow, reporting, feature
        :pullreq: 1240

        **Date**: 2024-05-16

        Title:
        Latest OS-HPXML

        Description:
        Improves heating/cooling component loads; for timesteps where there is no heating/cooling load, assigns heat transfer to heating or cooling by comparing indoor temperature to the average of heating/cooling setpoints.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, reporting, feature
        :pullreq: 1240

        **Date**: 2024-05-16

        Title:
        Latest OS-HPXML

        Description:
        Additional geothermal loop default simulation outputs (number/length of boreholes).
        Adds geothermal loop outputs (number/length of boreholes) to annual results output file.

        OpenStudio-HPXML: `#1657 <https://github.com/NREL/OpenStudio-HPXML/issues/1657>`_

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, infiltration, feature
        :pullreq: 1240

        **Date**: 2024-05-16

        Title:
        Latest OS-HPXML

        Description:
        Updates default `ShieldingofHome` to be "well-shielded" (from "normal") for single-family attached and multifamily dwelling units.
        Updates default ShieldingofHome to be "well-shielded" for single-family attached and multifamily dwelling units.

        Assignees: Scott Horowitz


    .. change::
        :tags: software, openstudio, feature
        :pullreq: 1225

        **Date**: 2024-05-09

        Title:
        OpenStudio 3.8/EnergyPlus 24.1

        Description:
        Update to OpenStudio v3.8.0.

        OpenStudio-HPXML: `pull request 1630 <https://github.com/NREL/OpenStudio-HPXML/pull/1630>`_

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: characteristics, ducts, feature
        :pullreq: 1233

        **Date**: 2024-05-07

        Title:
        Updates duct effective R-values; allows duct shape inputs

        Description:
        Update to new OS-HPXML defaults for duct insulation; 25% rectangular supply ducts and 100% rectangular return ducts (previously 100% round supply/return ducts).
        Adds optional inputs (Ducts/DuctShape and Ducts/DuctFractionRectangular); defaults to 25% rectangular supply ducts and 100% rectangular return ducts (previously 100% round supply/return ducts).

        OpenStudio-HPXML: `#1470 <https://github.com/NREL/OpenStudio-HPXML/issues/1470>`_, `pull request 1691 <https://github.com/NREL/OpenStudio-HPXML/pull/1691>`_

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, hvac, feature
        :pullreq: 1233

        **Date**: 2024-05-07

        Title:
        HVAC Autosizing Limits

        Description:
        Sizing control option to specify max allowed airflow.
        The PR aims to allow specifying upper limits for autosized capacities.

        OpenStudio-HPXML: `#1530 <https://github.com/NREL/OpenStudio-HPXML/issues/1530>`_, `#1556 <https://github.com/NREL/OpenStudio-HPXML/issues/1556>`_, `pull request 1584 <https://github.com/NREL/OpenStudio-HPXML/pull/1584>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, hvac, feature
        :pullreq: 1218

        **Date**: 2024-04-09

        Title:
        HVAC Autosizing Factors

        Description:
        Enable HVAC airflow and capacity scaling factors to oversize or undersize the equipment.
        Manually create new tsv files for assigning autosizing factor arguments introduced by NREL/OpenStudio-HPXML#1611.

        resstock-estimation: `pull request 406 <https://github.com/NREL/resstock-estimation/pull/406>`_

        OpenStudio-HPXML: `#1561 <https://github.com/NREL/OpenStudio-HPXML/issues/1561>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, plug loads, ceiling fan, feature
        :pullreq: 1220

        **Date**: 2024-04-02

        Title:
        Update Other, TV, and Ceiling Fan stochastic schedules

        Description:
        Update the stochastic schedule generator to produce updated other/TV plug load and ceiling fan schedules.
        generate TV schedules that follow the ATUS TV schedule fractions (distinct weekday/weekend) and multipliers (and not Other schedule fractions and multipliers).
        generate Other schedules that follow the new Other schedule fractions (still uses non-constant 2010 BAHSP monthly multipliers).
        generate Ceiling Fan schedules that follow the new Ceiling Fan schedule fractions (also update multipliers to not follow Other multipliers, but rather Ceiling Fan multipliers that are a function of weather).

        OpenStudio-HPXML: `pull request 1634 <https://github.com/NREL/OpenStudio-HPXML/pull/1634>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, alaska, bugfix
        :pullreq: 1214

        **Date**: 2024-03-18

        Title:
        Integrate ARIS data

        Description:
        Update the Alaska residential stock characterization using the Alaska Retrofit Information System data.
        Update housing characteristics for Alaska using ARIS dataset. Explicitly model wood heating for the national.

        resstock-estimation: `pull request 381 <https://github.com/NREL/resstock-estimation/pull/381>`_

        Assignees: Rajendra Adhikari, Anthony Fontanini


    .. change::
        :tags: workflow, hvac, bugfix
        :pullreq: 1215

        **Date**: 2024-03-11

        Title:
        HVAC Autosizing Factors

        Description:
        Add ability to specify HVAC system autosizing factors for baseline buildings; autosizing factors are retained for upgrade buildings following the same approach for HVAC system capacities.
        Allows optional HeatingAutosizingFactor, CoolingAutosizingFactor, BackupHeatingAutosizingFactor inputs to scale HVAC equipment autosizing results.

        OpenStudio-HPXML: `#1561 <https://github.com/NREL/OpenStudio-HPXML/issues/1561>`_, `pull request 1611 <https://github.com/NREL/OpenStudio-HPXML/pull/1611>`_

        Assignees: Joe Robertson, Yueyue Zhou


    .. change::
        :tags: workflow, weather, feature
        :pullreq: 1215

        **Date**: 2024-03-11

        Title:
        Allow building site inputs

        Description:
        Allow building site inputs; this is particularly useful when the building is located far from, or at a very different elevation than, the EPW weather station. When not provided, defaults to using EPW header values (as before).

        OpenStudio-HPXML: `pull request 1636 <https://github.com/NREL/OpenStudio-HPXML/pull/1636>`_

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, socio-demographics, feature
        :pullreq: 1212

        **Date**: 2024-02-29

        Title:
        Add SMI, MSA, Metro Status

        Description:
        Add Metropolitan and Micropolitan Statistical Area tsv, County Metro Status tsv, and State Metro Median Income tsv.
        Added 3 new tsvs to support @SinounPhoung's socio-demographically differentiated Stochastic Occupant Schedule integration into ResStock.

        resstock-estimation: `pull request 400 <https://github.com/NREL/resstock-estimation/pull/400>`_

        Assignees: Lixi Liu


    .. change::
        :tags: characteristics, water heater, bugfix
        :pullreq: 1201

        **Date**: 2024-02-28

        Title:
        Update water heater location

        Description:
        Move location of out-of-unit (shared) water heaters to conditioned mechanical room.
        Move out-of-unit water heaters (i.e., Water Heater In Unit=No from Location=None to Location=Conditioned Mechanical Room (corresponds to OS-HPXML location: "other heated space").

        Assignees: Lixi Liu, Jeff Maguire, Anthony Fontanini


    .. change::
        :tags: workflow, unavailable periods, feature
        :pullreq: 1209

        **Date**: 2024-02-23

        Title:
        BuildResidentialHPXML: multiple vacancy/outage periods

        Description:
        Allow definition of multiple unavailable periods (i.e., vacancy, power outage).
        Update schedules_vacancy_period and schedules_power_outage_period arguments to support multiple periods (comma-separated?).

        OpenStudio-HPXML: `#1618 <https://github.com/NREL/OpenStudio-HPXML/issues/1618>`_, `pull request 1622 <https://github.com/NREL/OpenStudio-HPXML/pull/1622>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, heat pump backup, feature
        :pullreq: 1209

        **Date**: 2024-02-23

        Title:
        HP backup sizing methodology

        Description:
        Add ability to set either an "emergency" or "supplemental" heat pump backup sizing methodology.
        Adds a HeatPumpBackupSizingMethodology element with choices of 'emergency' and 'supplemental'. Defaults to 'emergency', so results do not change by default.

        OpenStudio-HPXML: `#1322 <https://github.com/NREL/OpenStudio-HPXML/issues/1322>`_, `pull request 1597 <https://github.com/NREL/OpenStudio-HPXML/pull/1597>`_

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, refrigerator, feature
        :pullreq: 1209

        **Date**: 2024-02-23

        Title:
        ANSI 301-2022: load profile schedules

        Description:
        Refrigerator energy use is now affected by its ambient temperature using hourly constant and temperature coefficients from ANSI/RESNET/ICC 301-2022 Addendum C.
        Default fridge schedule is now an actuated EMS program. Daily schedule is a function of hour and space temperature.

        OpenStudio-HPXML: `pull request 1572 <https://github.com/NREL/OpenStudio-HPXML/pull/1572>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, general water use, feature
        :pullreq: 1209

        **Date**: 2024-02-23

        Title:
        ANSI 301-2022: load profile schedules

        Description:
        Various schedule fractions/multipliers updates (e.g., appliances, lighting, fixtures, occupancy, ceiling fan).

        OpenStudio-HPXML: `pull request 1572 <https://github.com/NREL/OpenStudio-HPXML/pull/1572>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, ceiling fan, feature
        :pullreq: 1209

        **Date**: 2024-02-23

        Title:
        ANSI 301-2022: load profile schedules

        Description:
        For ceiling fans, add a LabelEnergyUse (W) input as an alternative to Efficiency (cfm/W).

        OpenStudio-HPXML: `pull request 1609 <https://github.com/NREL/OpenStudio-HPXML/pull/1609>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, hot water fixtures, feature
        :pullreq: 1210

        **Date**: 2024-02-21

        Title:
        Updating hot water fixtures multipliers based on field data.

        Description:
        Update hot water usage multipliers based on field data rather than engineering judgement.
        Update hot water usage multipliers. Using field data from 1700 water heaters in New England to come up with the distribution. Based on data collected as part of PERFORM with Michael Blonsky, who shared the distribution with us.

        resstock-estimation: `#289 <https://github.com/NREL/resstock-estimation/issues/289>`_, `pull request 361 <https://github.com/NREL/resstock-estimation/pull/361>`_

        Assignees: Jeff Maguire, Anthony Fontanini


    .. change::
        :tags: workflow, whole building, feature
        :pullreq: 1200

        **Date**: 2024-01-30

        Title:
        Whole MF building models: Replace building_id=ALL argument with an HPXML element

        Description:
        Add optional switch to BuildExistingModel (defaulted to false) for modeling whole SFA/MF buildings.
        Replaces building_id=ALL argument with an element in the HPXML file, which allows us to perform validation specific to whole MF building simulations.

        OpenStudio-HPXML: `pull request 1594 <https://github.com/NREL/OpenStudio-HPXML/pull/1594>`_

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: characteristics, data sources, bugfix
        :pullreq: 1199

        **Date**: 2024-01-26

        Title:
        Update characteristics using 2020 RECS v7 data

        Description:
        Update to RECS 2020 V7 data files.
        Updates RECS 2020 data from v5 to v7. There are some new EV variables to be leveraged by the ResStock/TEMPO project.

        resstock-estimation: `pull request 394 <https://github.com/NREL/resstock-estimation/pull/394>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 1195

        **Date**: 2024-01-22

        Title:
        Reorganize emissions and utility bills data folders

        Description:
        Reorganize the emissions and utility rates data folders such that their sources and functions are more clear.
        Previously, it wasn't clear that the provided utility rate data was for demonstration purposes only.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, emissions, feature
        :pullreq: 1194

        **Date**: 2024-01-19

        Title:
        2022 Cambium: add 25 year levelization scenarios

        Description:
        Include additional 2022 Cambium 25-year LRMER emissions data.
        Add 10 new "LRMER_xxx_25" data folders to resources/data/cambium/2022.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, radiant barrier, feature
        :pullreq: 1188

        **Date**: 2024-01-17

        Title:
        Adding flexibility to specify location of the radiant barrier

        Description:
        Add flexibility to specify location of the radiant barrier.
        Allowing Radiant Barrier for Attic Floor.

        OpenStudio-HPXML: `#1435 <https://github.com/NREL/OpenStudio-HPXML/issues/1435>`_, `pull request 1473 <https://github.com/NREL/OpenStudio-HPXML/pull/1473>`_

        Assignees: Prateek Shrestha


    .. change::
        :tags: workflow, hvac, feature
        :pullreq: 1188, 1200

        **Date**: 2024-01-17

        Title:
        Allow autosizing with detailed performance data inputs for var speed systems
        BuildResidentialHPXML: detailed performance data arguments

        Description:
        Add ability to describe detailed performance data for variable-speed air-source HVAC systems.
        Updated assumptions for variable-speed air conditioners, heat pumps, and mini-splits.
        Also allows detailed heating and cooling performance data (min/max COPs and capacities at different outdoor temperatures) as an optional set of inputs. 
        Data can be sourced from e.g. NEEP's Cold Climate Air Source Heat Pump List.
        Add detailed performance data arguments for air-source, variable-speed HVAC systems.

        OpenStudio-HPXML: `pull request 1583 <https://github.com/NREL/OpenStudio-HPXML/pull/1583>`_, `pull request 1317 <https://github.com/NREL/OpenStudio-HPXML/pull/1317>`_, `pull request 1558 <https://github.com/NREL/OpenStudio-HPXML/pull/1558>`_

        Assignees: Yueyue Zhou, Scott Horowitz, Joe Robertson


    .. change::
        :tags: workflow, water heater, bugfix
        :pullreq: 1190
        :tickets: 1184

        **Date**: 2024-01-12

        Title:
        Remove old HPWH options from options_lookup

        Description:
        Remove old HPWH options from options_lookup.
        Removing the old HPWH options from options_lookup.tsv.

        Assignees: Jeff Maguire
    
    .. change::
        :tags: characteristics
        :pullreq: 1260

        **Date**: 2024-06-17

        Title:
        Update threshold for weekday occupancy

        Description:
        RECS tsv_maker previously assumed that if people are home even for 1 day during the week, they are home every day of the week.
        This resulted in people being less away (and hence fewer day time setbacks). This PR updates the threshold for weekday occupancy to be 3 days.
        This makes the weekday occupancy more in line with RECS.

        Assignees: Rajendra Adhikari



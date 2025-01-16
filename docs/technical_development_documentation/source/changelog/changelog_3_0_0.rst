================
v3.0.0 Changelog
================

.. changelog::
    :version: v3.0.0
    :released: 2023-02-03

    .. change::
        :tags: software, openstudio, feature
        :pullreq: 1015

        **Date**: 2023-02-01

        Title:
        Latest OS-HPXML

        Description:
        Update to OpenStudio v3.5.1.

        OpenStudio-HPXML: `pull request 1251 <https://github.com/NREL/OpenStudio-HPXML/pull/1251>`_

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: characteristics, income, feature
        :pullreq: 1004

        **Date**: 2022-11-09

        Title:
        Add AMI + modified tsvs from resstock-estimation refactoring/opt

        Description:
        Add area median income.
        Using the traditional method of copying files over from resstock-estimation, add AMI and other modified tsvs from a recent set of resstock-estimation PRs refactoring and optimizing tsv_making processes.

        resstock-estimation: `pull request 243 <https://github.com/NREL/resstock-estimation/pull/243>`_, `pull request 302 <https://github.com/NREL/resstock-estimation/pull/302>`_, `pull request 304 <https://github.com/NREL/resstock-estimation/pull/304>`_

        Assignees: Lixi Liu, Anthony Fontanini


    .. change::
        :tags: characteristics, floor area, feature
        :pullreq: 978

        **Date**: 2022-10-27

        Title:
        AHS 2019 and 2021 data for simulated conditioned floor area

        Description:
        Modeled floor area based on AHS 2021 and AHS 2019.
        Use the AHS 2019, 2021 data for the simulated conditioned floor area ResStock arguments. Link to the AHS table used is HERE. For multi-family the ACS multi-family building types were combined using a weighted average where there were enough samples.

        Assignees: Anthony Fontanini, Lixi Liu


    .. change::
        :tags: workflow, utility bills, feature
        :pullreq: 984

        **Date**: 2022-09-09

        Title:
        Optionally calculate simple utility bills

        Description:
        Add ability to calculate simple utility bills for various scenarios.
        Call new ReportUtilityBills measure from OS-HPXML.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 982

        **Date**: 2022-08-26

        Title:
        Update join_tsv to use raw source_count

        Description:
        Update low-sample downscaling logic to use raw source_weight, which leads to minor changes to Geometry Floor Area and HVAC Partial Space Conditioning.
        TSV changes from updating join_distributions_in_order to use raw source_weight (previously, it uses what is now called fallback_weight which artificially increases the weight of undersampled options, thus making it deviate more from the sample truth marginal distributions)

        resstock-estimation: `pull request 248 <https://github.com/NREL/resstock-estimation/pull/248>`_

        Assignees: Lixi Liu, Anthony Fontanini


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 981

        **Date**: 2022-08-22

        Title:
        TSV changes from improved low samples handling

        Description:
        Remove Void from dependency columns in TSVs and update tests.
        Some TSVs have "Option=Void" as one of the available options. The idea behind Void is that certain dependency conditions are structurally impossible. For example, for "HVAC Heating Type and Fuel.tsv", it's impossible that "Heating Fuel" = Electricity and "HVAC Heating Efficiency" = "Fuel Boiler". So, this particular dependency condition get's Void option.

        resstock-estimation: `pull request 245 <https://github.com/NREL/resstock-estimation/pull/245>`_

        Assignees: Rajendra Adhikari


    .. change::
        :tags: workflow, setpoints, bugfix
        :pullreq: 975

        **Date**: 2022-08-17

        Title:
        Support auto_seasons arguments

        Description:
        Fix heating and cooling auto-season inputs.
        Looks like OS-HPXML auto_seasons related arguments may have been updated, but ResStockArguments subsequently was not. I believe this was not caught because our testing project does not currently sample any setpoint options which enable the auto_seasons arguments.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, hvac, feature
        :pullreq: 964

        **Date**: 2022-07-15

        Title:
        Introduce cooling partial space conditioning

        Description:
        Add distributions for partial space cooling.
        Introduce partial space conditioning for cooling.

        resstock-estimation: `pull request 235 <https://github.com/NREL/resstock-estimation/pull/235>`_, `pull request 233 <https://github.com/NREL/resstock-estimation/pull/233>`_, `pull request 241 <https://github.com/NREL/resstock-estimation/pull/241>`_

        Assignees: Anthony Fontanini, Rajendra Adhikari


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 959

        **Date**: 2022-07-09

        Title:
        Ll/rename sources

        Description:
        Rename sources subfolders so all tsv_makers can be imported as packages.
        Rename sources folders so all tsv_makers can be imported as packages. Packages cannot contain names that start with a number.

        resstock-estimation: `pull request 238 <https://github.com/NREL/resstock-estimation/pull/238>`_

        Assignees: Lixi Liu


    .. change::
        :tags: characteristics, income, feature
        :pullreq: 949

        **Date**: 2022-07-08

        Title:
        add income + tenure to floor_area

        Description:
        Add Income and Tenure into Geometry Floor Area.
        Add Income and Tenure to Geometry Floor Area.

        resstock-estimation: `pull request 233 <https://github.com/NREL/resstock-estimation/pull/233>`_

        Assignees: Lixi Liu


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 934

        **Date**: 2022-06-02

        Title:
        Fix/tsv tags sampling prob etc

        Description:
        Fix minor bug in sampling probability calculation.

        resstock-estimation: `pull request 221 <https://github.com/NREL/resstock-estimation/pull/221>`_

        Assignees: Lixi Liu, Anthony Fontanini


    .. change::
        :tags: characteristics, income, feature
        :pullreq: 900

        **Date**: 2022-05-06

        Title:
        Add income, tenure, fix occupants

        Description:
        Add Income and Tenure tsv, update PUMS tsvs from 2017 5-yrs to 2019 5-yrs, update dependencies and fix encoding error in Occupants.tsv.
        Update PUMS tsvs from 2017 5-yrs to 2019 5-yrs.
        Add new tvs: Income, Income RECS2015, Federal Poverty Level, Tenure, and PUMA Metro Status (a few of them are explained in detail below.)

        Assignees: Lixi Liu, Anthony Fontanini, Nate Moore


    .. change::
        :tags: characteristics, heat pumps, feature
        :pullreq: 913

        **Date**: 2022-05-02

        Title:
        Improve heat pump distributions for Texas and Florida

        Description:
        Improve distributions of heat pumps in the southeast U.S. by spliting IECC zone 2A into two zones: 2A (FL, GA, AL, MS) and 2A (TX, LA).
        Currently using IECC climate zone for HVAC Heating Type.
        Zone 2A is 16%-20% HP, whereas Reportable Domain of TX (3%), FL (20%).
        Solution: Split 2A into two chunks, 2A (FL, GA, AL, MS), and 2A (TX, LA).

        resstock-estimation: `pull request 209 <https://github.com/NREL/resstock-estimation/pull/209>`_

        Assignees: Phil White, Eric Wilson, Anthony Fontanini


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 905

        **Date**: 2022-04-27

        Title:
        update tsvs with new sampling_prob

        Description:
        Update tsvs with new sampling_probability calculation.

        resstock-estimation: `pull request 210 <https://github.com/NREL/resstock-estimation/pull/210>`_, `pull request 203 <https://github.com/NREL/resstock-estimation/pull/203>`_

        Assignees: Lixi Liu


    .. change::
        :tags: characteristics, geography, feature
        :pullreq: 874

        **Date**: 2022-04-20

        Title:
        City Boundaries

        Description:
        Cities with more than 15,000 dwelling units are added as a geographic characteristic.
        Adding City boundaries as a housing characteristic in ResStock. This way users can aggregate directly by a given City.

        resstock-estimation: `pull request 196 <https://github.com/NREL/resstock-estimation/pull/196>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, cost multipliers, feature
        :pullreq: 870

        **Date**: 2022-04-11

        Title:
        Unvented crawlspace upgrade

        Description:
        Add a new "Floor Area, Foundation (ft^2)" cost multiplier.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, cost multipliers, feature
        :pullreq: 848

        **Date**: 2022-04-06

        Title:
        Handle incremental costs of (1) adding attic insulation and (2) reducing (%) infiltration

        Description:
        Add a new "Floor Area, Attic * Insulation Increase (ft^2 * Delta R-value)" cost multiplier for handling incremental costs of adding attic insulation.
        Handle incremental costs of adding attic insulation.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, cost multipliers, feature
        :pullreq: 848

        **Date**: 2022-04-06

        Title:
        Handle incremental costs of (1) adding attic insulation and (2) reducing (%) infiltration

        Description:
        Allow air leakage % reduction upgrades (e.g., 25%), and add a new "Floor Area, Conditioned * Infiltration Reduction (ft^2 * Delta ACH50)" cost multiplier for handling incremental costs of such upgrades.
        Add generic multiplier argument to infiltration options to facilitate % reductions in ACH50.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 877

        **Date**: 2022-04-04

        Title:
        Reduce TSV Sizes

        Description:
        Reduce housing characteristic file size by relaxing the six digit float format in the housing characteristics.
        As housing characteristics get bigger, we are moving to a compact writing style. The 6-digit float format requirement was put in place when most of the characteristics were not scripted. Now that there is a standard workflow for creating the characteristics, the formatting requirements are being relaxed. This change should allow for more accurate characteristic distributions because the exponential format can be used. The change should also stop round-off errors.

        resstock-estimation: `pull request 200 <https://github.com/NREL/resstock-estimation/pull/200>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, testing, feature
        :pullreq: 828

        **Date**: 2022-03-09

        Title:
        Changes after switching to ResStock-HPXML

        Description:
        For the testing project, sample equal distributions of (1) smooth and stochastic schedules (each 50%) and (2) faulted and non-faulted HVAC systems (each 50%).
        project_testing/Schedules.tsv to equal distribution of Default and Stochastic.
        project_testing/HVAC System Is Faulted.tsv to equal distribution of No and Yes.

        resstock-estimation: `pull request 193 <https://github.com/NREL/resstock-estimation/pull/193>`_

        Assignees: Joe Robertson, Andrew Speake


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 828

        **Date**: 2022-03-09

        Title:
        Changes after switching to ResStock-HPXML

        Description:
        Clean up option names for natural ventilation and hot water distribution.

        resstock-estimation: `pull request 193 <https://github.com/NREL/resstock-estimation/pull/193>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 839

        **Date**: 2022-02-28

        Title:
        Extend ApplyUpgrade for upgrade measures

        Description:
        Allow upgrade options to be defined in the lookup using measures other than ResStockArguments.
        Support "upgrade" measures that are not part of the OS-HPXML workflow, and are tacked on after model is created.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, rim joists, feature
        :pullreq: 831

        **Date**: 2022-02-16

        Title:
        Enable rim joists

        Description:
        Enable rim joists for homes with basements/crawlspaces; assumes a height of 9.25 inches and calculates rim joist assembly R-value from new insulation arguments.
        Enable rim joists (set this by default, and r-value to foundation wall r-value); we could potentially enable rim joists between floors by adjusting average ceiling height, but we won't for now.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, heat pumps, bugfix
        :pullreq: 833

        **Date**: 2022-02-16

        Title:
        Remove backup switchover temp for non dual fuel heat pumps

        Description:
        Remove the zero degree switchover temperature for heat pump backup heating.
        Remove heat_pump_backup_heating_switchover_temp=0.0 for non dual fuel heat pumps. Leave heat_pump_backup_heating_switchover_temp=30.0 for dual fuel heat pumps.

        Assignees: Joe Robertson, Andrew Speake


    .. change::
        :tags: workflow, hescore, feature
        :pullreq: 782

        **Date**: 2022-02-14

        Title:
        HEScore Workflow

        Description:
        Enable the HEScore workflow to be run with BuildExistingModel.
        Enables to the HEScore workflow to be run from BuildExistingModel. A new argument os_hescore_directory is added in BuildExistingModel which points to a local checkout of https://github.com/NREL/OpenStudio-HEScore.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 830

        **Date**: 2022-02-14

        Title:
        Model finished attics

        Description:
        For homes with a finished attic or cathedral ceilings, models a conditioned attic instead of a vented attic.
        Change geometry_attic_type=VentedAttic when Geometry Attic Type samples Finished Attic or Cathedral Ceilings.

        Assignees: Joe Robertson, Andrew Speake


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 443

        **Date**: 2022-02-10

        Title:
        ResStock-HPXML

        Description:
        Transition to using the HPXML-based workflow.
        Subtree resources/hpxml-measures to github.com/NREL/OpenStudio-HPXML.

        OpenStudio-HPXML: `pull request 372 <https://github.com/NREL/OpenStudio-HPXML/pull/372>`_

        Assignees: Joe Robertson, Andrew Speake



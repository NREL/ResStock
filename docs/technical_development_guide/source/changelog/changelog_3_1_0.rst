================
v3.1.0 Changelog
================

.. changelog::
    :version: v3.1.0
    :released: 2023-05-25

    .. change::
        :tags: software, openstudio, feature
        :pullreq: 1076

        **Date**: 2023-05-25

        Title:
        Latest OS-HPXML, OS v3.6.1

        Description:
        Update to OpenStudio v3.6.1.

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 1076

        **Date**: 2023-05-25

        Title:
        Pulls in upstream OS-HPXML fix related to [falling back to a WWR calculation when window placement fails](https://github.com/NREL/OpenStudio-HPXML/pull/1385) causing errors fitting windows

        Description:
        Pulls in upstream OS-HPXML fix related to [falling back to a WWR calculation when window placement fails](https://github.com/NREL/OpenStudio-HPXML/pull/1385) causing errors fitting windows.

        Assignees: Joe Robertson


    .. change::
        :tags: documentation, data dictionary, feature
        :pullreq: 1058

        **Date**: 2023-05-10

        Title:
        Data dictionary + automated RTD generation

        Description:
        Add data dictionary files for describing various outputs. Use these files to (1) check against integration test results, and (2) generate documentation tables.
        One of the pain points we experience when importing ResStock runs into SightGlass (resstock.nrel.gov) is that the outputs and format of the outputs from ResStock frequently change. This causes our data processing for that to break and require many hours of manual updating every time we go to bring new data in.
        It would be really helpful to have a data dictionary of the outputs ResStock produces meaning every column name (including the input and output columns) in the results.csv and timeseries parquet files. It should also include some flags about which are end uses to include in the sum vs aggregates (net or totals), units, other random outputs like load, emissions, etc. To keep this in sync, it should be verified against the CI runs of ResStock and if there is a discrepancy you get a big ❌ on your checks.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, heat pumps, feature
        :pullreq: 1071

        **Date**: 2023-05-09

        Title:
        Add capacity retention arguments for ASHP

        Description:
        Connect ASHP to optional capacity retention temperature and fraction arguments (that already exist for MSHP).

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: workflow, heat pumps, feature
        :pullreq: 1072

        **Date**: 2023-05-09

        Title:
        HP heating capacity retention

        Description:
        OS-HPXML now supports use of optional heat pump capacity retention temperature and fraction arguments (applicable to both ASHP and MSHP).
        Adds optional inputs for defining heat pump capacity retention:
        
        - extension/HeatingCapacityRetention/Fraction
        - extension/HeatingCapacityRetention/Temperature

        OpenStudio-HPXML: `pull request 1383 <https://github.com/NREL/OpenStudio-HPXML/pull/1383>`_

        Assignees: Joe Robertson, Scott Horowitz


    .. change::
        :tags: characteristics, documentation, feature
        :pullreq: 1069

        **Date**: 2023-05-01

        Title:
        Add descriptions to housing characteristics

        Description:
        Add descriptions to the housing characteristics.
        Add a description tag to each of the housing characteristics. Add the source reports from resstock-estimation to resstock.

        resstock-estimation: `pull request 366 <https://github.com/NREL/resstock-estimation/pull/366>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 1056

        **Date**: 2023-03-21

        Title:
        Support sample_weight in buildstock.csv

        Description:
        Ability to specify a "sample_weight" column in the precomputed buildstock.csv.
        Adds support for a sample_weight column in the precomputed buildstock.csv. By default, BuildExistingModel writes build_existing_model.sample_weight based on calculating n_buildings_represented / n_datapoints (this calculation is done in the workflow generator and then passed into the BuildExistingModel measure). Now, if sample_weight already exists in the buildstock.csv, it will write this value instead of the calculated one.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, unavailable periods, feature
        :pullreq: 1054

        **Date**: 2023-03-15

        Title:
        Support for power outages

        Description:
        Demonstrate new power outage modeling feature using upgrades specified in example project yml files.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 1054

        **Date**: 2023-03-15

        Title:
        Pulls in upstream OS-HPXML fix related to [avoiding possible OpenStudio temporary directory collision](https://github.com/NREL/OpenStudio-HPXML/pull/1316) causing random errors

        Description:
        Pulls in upstream OS-HPXML fix related to [avoiding possible OpenStudio temporary directory collision](https://github.com/NREL/OpenStudio-HPXML/pull/1316) causing random errors.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, battery, feature
        :pullreq: 1009

        **Date**: 2023-03-07

        Title:
        Stub battery tsv for testing project

        Description:
        Include battery modeling capabilities for project_testing.
        Stub new Battery.tsv.
        Separate battery related arguments from PV in options_lookup.
        Test battery options using testing project.

        resstock-estimation: `pull request 321 <https://github.com/NREL/resstock-estimation/pull/321>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 1042

        **Date**: 2023-03-07

        Title:
        Check a buildstock csv against an options_lookup tsv

        Description:
        Ability to check buildstock csv against an options lookup as a command line utility.
        Enable "integrity checks" on buildstock.csv.

        Assignees: Joe Robertson



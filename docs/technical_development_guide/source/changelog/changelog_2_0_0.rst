================
v2.0.0 Changelog
================

.. changelog::
    :version: v2.0.0
    :released: 2019-04-17

    .. change::
        :tags: software, openstudio, feature
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Update to OpenStudio v2.8.0.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Add a multifamily project which includes housing characteristic distributions for single-family detached, single-family attached, and multifamily buildings.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Add measures for calculating construction properties, modeling power outages and calculating resilience metrics, and calculating utility bills.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Add measure for modeling shared multiifamily facades using adiabatic constructions.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Relocate all measure unit tests, test osw files, and test osm files from archived OpenStudio-BEopt and into this repository.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Create example workflow osw files for single-family detached, single-family attached, and multifamily buildings using TMY weather.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Reporting measures read from ReportMeterData table to get disaggregated fan and pump energy.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 151

        **Date**: 2019-04-11

        Title:
        Multifamily

        Description:
        Break out central system heating, cooling, and pump energy in reporting measures.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 216

        **Date**: 2019-03-21

        Title:
        Use UnitConversions.convert(...) method

        Description:
        Use custom unit conversions script instead of that provided by OpenStudio SDK.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, documentation, feature
        :pullreq: 211

        **Date**: 2019-02-28

        Title:
        Dependency graphs and wheels

        Description:
        Automatically generate dependency graphs and a dependency wheel for each project.
        I put together scripts in the docs folder to automatically generate dependency graphs and a dependency wheel for each <project_folder> in the OpenStudio-BuildStock repository. These scripts create a util folder if it doesn't exist and puts data for these visualizations. A project README.md file has been added to each <project_folder> where there is a link to the interactive dependency wheel. These visualizations are easily updated as they depend strictly on the TSV files. They are updated through a single regenerate_visualization.ipynb script.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 206

        **Date**: 2019-02-12

        Title:
        Large buildings collapsed into minimal units

        Description:
        Ability to simulate large multifamily buildings using "collapsed" buildings with multipliers on building units.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 151

        **Date**: NaT

        Title:
        Multifamily

        Description:
        Ability to add central systems (boiler with baseboards, fan coil, PTAC) to multifamily buildings using the openstudio-standards gem.

        Assignees: Joe Robertson, Maharshi Pathak, Scott Horowitz



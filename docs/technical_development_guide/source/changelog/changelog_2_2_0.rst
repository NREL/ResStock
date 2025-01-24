================
v2.2.0 Changelog
================

.. changelog::
    :version: v2.2.0
    :released: 2020-01-30

    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 346

        **Date**: 2020-01-30

        Title:
        Addresses #344, adjust timeseries csv index for DST

        Description:
        Include additional "daylight saving time" and "utc time" columns to timeseries csv file to account for one hour forward and backward time shifts.
        The TimeseriesCSVExport measure outputs time at a constant interval across a year, regardless of time changes for daylight savings time. This can cause confusion, as E+ shifts schedules to account for DST, but our time output does not line up with this shift.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, reporting, bugfix
        :pullreq: 346

        **Date**: 2020-01-30

        Title:
        Addresses #344, adjust timeseries csv index for DST

        Description:
        Update each PAT project's AMI selection to "2.9.0".
        The TimeseriesCSVExport measure outputs time at a constant interval across a year, regardless of time changes for daylight savings time. This can cause confusion, as E+ shifts schedules to account for DST, but our time output does not line up with this shift.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, misc loads, feature
        :pullreq: 362

        **Date**: 2020-01-29

        Title:
        More none no natl avg

        Description:
        Split out national average options so not all homes have all miscellaneous equipment, and add none options to appliances.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 371

        **Date**: 2020-01-24

        Title:
        Addresses #352, optionally include annual totals for end use subcategories

        Description:
        The results csv now optionally reports annual totals for all end use subcategories, including appliances, plug loads, etc.
        Can now optionally report (using the SimulationOutputReport measure) annual totals for end use subcategories (same as for the TimeseriesCSVExport measure) in the results csv. Measure also checks that the sum of the end use subcategories equals the reported interior equipment value.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 371

        **Date**: 2020-01-24

        Title:
        Addresses #352, optionally include annual totals for end use subcategories

        Description:
        Custom meters for ceiling fan, hot water recirc pump, and vehicle end use subcategories were not properly implemented.
        Can now optionally report (using the SimulationOutputReport measure) annual totals for end use subcategories (same as for the TimeseriesCSVExport measure) in the results csv. Measure also checks that the sum of the end use subcategories equals the reported interior equipment value.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, hvac, bugfix
        :pullreq: 372

        **Date**: 2020-01-23

        Title:
        Fixes wood stove upgrade

        Description:
        Allow Wood Stove option as an upgrade, and account for wood heating energy in simulation output.
        I added a bugfix for the upgrade so that the EnergyPlus simulation is successful.

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 357

        **Date**: 2020-01-18

        Title:
        Tsv wall w hcs reformat

        Description:
        Update the single-family detached project with a Geometry Wall Type tsv file for sampling between wood stud and masonry walls.
        Added the TSV for wall type, masonry and wood. added dependency to the Insulation Wall TSV; additional options for CMU walls(post-1950) and 3" wythe brick wall.

        Assignees: Maharshi Pathak


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 356

        **Date**: 2020-01-18

        Title:
        Mf renaming w hcs formating

        Description:
        Some re-labeling of tsv files, such as "Geometry Building Type" to "Geometry Building Type RECS" and "Geometry Building Type FPL" to "Geometry Building Type ACS".
        Changes in the naming convention of hcs with the new hcs format included.

        Assignees: Maharshi Pathak


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 353

        **Date**: 2020-01-17

        Title:
        Make housing characteristics format consistent.

        Description:
        Made housing characteristics a consistent format. Added integrity check to ensure housing characteristics follow the guildelines specified in read-the-docs.
        In the effort to make the format more consistent, the following format has been applied to the housing characteristics. Standardizing the format of the housing characteristics should make it easier to see differences in commits
        
        - All line terminators are '\r\n' which is consistent with Windows machines.
        - All Option columns have format '%.6f'.
        - All [For Reference Only] Source Sample Size columns are type 'int'.
        - All [For Reference Only] Source Weight columns are type 'int'.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 360

        **Date**: 2020-01-17

        Title:
        Remove "auto" option for number of occupants

        Description:
        Removes option "Auto" from parameter "Occupants" in the options lookup file.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 350

        **Date**: 2019-12-12

        Title:
        Neighbors update

        Description:
        Update the multifamily project's neighbors and orientation tsv files to have geometry building type dependency; remove the now obsolete "Geometry Is Multifamily Low Rise.tsv" file.
        Remove Geometry Is Multifamily Low Rise.tsv from all projects, and replace with Geometry Building Type.tsv as a dependency in the multifamily project.
        Use Geometry Building Type.tsv as dependency for Neighbors.tsv in multifamily project.
        Use Geometry Building Type.tsv as dependency for Orientation.tsv in multifamily project.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, lighting, bugfix
        :pullreq: 349

        **Date**: 2019-12-11

        Title:
        Lighting fixes

        Description:
        Fixes for custom output meters: total site electricity double-counting exterior holiday lighting, and garage lighting all zeroes.
        Addresses bugs in custom output meters found by @rajeee and @afontani.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, recs, feature
        :pullreq: 340

        **Date**: 2019-11-26

        Title:
        RECS 2015 tsv maker

        Description:
        Update bedrooms and occupants tsv files with options and probability distributions based on RECS 2015 data.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, facades, bugfix
        :pullreq: 301

        **Date**: 2019-11-15

        Title:
        Remove shared facades

        Description:
        Remove shared facades tsv files from the multifamily_beta and testing projects.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, power outage, bugfix
        :pullreq: 238

        **Date**: 2019-11-13

        Title:
        Updates to outage measure

        Description:
        Fix for the power outages measure where the last hour of the day was not getting the new schedule applied.
        It looked like the last hour of the day wasn't getting the new schedule applied. This fixes that. I've also cleaned up some code and added some new unit tests.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 338

        **Date**: 2019-11-07

        Title:
        Update sfd, mf, and testing tsv structure

        Description:
        Separate tsv files for bedrooms, cooking range schedule, corridor, holiday lighting, interior/other lighting use, pool schedule, plug loads schedule, and refrigeration schedule.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, reporting, feature
        :pullreq: 334

        **Date**: 2019-11-05

        Title:
        Report quantities of interest

        Description:
        Add new QOIReport measure for reporting seasonal quantities of interest for uncertainty quantification.
        Reporting quantities of interest for EULP uncertainty quantification.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, reporting, bugfix
        :pullreq: 334

        **Date**: 2019-11-05

        Title:
        Report quantities of interest

        Description:
        Move redundant output meter code from individual reporting measures out into shared resource file.

        Assignees: Joe Robertson



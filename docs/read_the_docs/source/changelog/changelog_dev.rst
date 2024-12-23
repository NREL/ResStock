=====================
Development Changelog
=====================
.. changelog::
    :version: v3.5.0
    :released: pending

    .. change::
        :tags: characteristics, pool heater
        :pullreq: 1324

        **Date**: 2024-12-3

        Title:
        Add heat pump pool heaters

        Description:
        Add heat pump pool heaters to baseline.

        resstock-estimation: `pull request 436 <https://github.com/NREL/resstock-estimation/pull/436>`_

        :tags: workflow, infiltration, bugfix
        :pullreq: 1257

        **Date**: 2024-08-20

        Title:
        Air leakage type "unit total"

        Description:
        Update options_lookup and ResStockArguments to use "unit total" air leakage type instead of the current "unit exterior only" type w/ infiltration adjustment approach.
        Modeled infiltration for dwelling units now have an upper bound equal to the sampled ACH50 option.
        Update BuildExistingModel to register adjusted total infiltration ACH50 value.

        Assignees: Joe Robertson

    .. change::
        :tags: characteristics, floor area, bugfix
        :pullreq: 1301

        **Date**: 2024-09-18

        Title:
        Fix RECS floor area bins

        Description:
        RECS have been using incorrect floor area bins when assigning some characteristics due to a bug on how floor area bin is calculated. This PR fixes the issue.

        Assignees: Rajendra Adhikari, Anthony Fontanini

    .. change::
        :tags: workflow, hot water, feature
        :pullreq: 1282

        **Date**: 2024-09-04

        Title:
        Latest OS-HPXML

        Description:
        For hot water end uses OS-HPXML now directly uses equations from https://www.fsec.ucf.edu/en/publications/pdf/fsec-pf-464-15.pdf, that are a function of number of occupants, for operational calculations.

        OpenStudio-HPXML: `pull request 1761 <https://github.com/NREL/OpenStudio-HPXML/pull/1761>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, plug loads, feature
        :pullreq: 1298

        **Date**: 2024-09-24

        Title:
        Latest OS-HPXML

        Description:
        For TV plug loads, we are now using OS-HPXML defaults that directly use equations from RECS 2020 that are a function of number of occupants and conditioned floor area.
        For operational calculations in general, we are also updating the relationships between number of bedrooms/occupants based on RECS 2020 and disaggregated by building types.

        OpenStudio-HPXML: `pull request 1690 <https://github.com/NREL/OpenStudio-HPXML/pull/1690>`_, `pull request 1775 <https://github.com/NREL/OpenStudio-HPXML/pull/1775>`_

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, hvac, feature
        :pullreq: 1254

        **Date**: 2024-09-218

        Title:
        Heating and Cooling Unavailable Days

        Description:
        The purpose of this PR is to account for dwelling units whose HVAC system (heating/cooling) is unavailable for some number of days during the year (per RECS 2020).
        Specifically, this PR modifies HVAC heating/cooling seasons using number of unavailable days and BAHSP definition for heating/cooling months.

        Assignees: Joe Robertson

    .. change::
        :tags: workflow, feature
        :pullreq: 929

        **Date**: 2024-10-14

        Title:
        New ResStockArgumentsPostHPXML measure

        Description:
        This measure is added to the workflow to post-process the output of the BuildResidentialHPXML and BuildResidentialScheduleFile measures.

        Assignees: Joe Robertson, Rajendra Adhikari

        GitHub: `pull request 929 <https://github.com/NREL/resstock/pull/929>`_   
        Assignees: Janet Reyna

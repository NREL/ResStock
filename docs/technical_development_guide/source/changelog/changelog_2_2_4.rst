================
v2.2.4 Changelog
================

.. changelog::
    :version: v2.2.4
    :released: 2020-05-01

    .. change::
        :tags: workflow, airflow, bugfix
        :pullreq: 442

        **Date**: 2020-05-01

        Title:
        Release 2_2_4 patch

        Description:
        Fix bug in options lookup where buildings without heating systems were not being assigned the required "has_hvac_flue" airflow measure argument.
        Argument has_hvac_flue for ResidentialAirflow wasn't being assigned when no heating system was sampled.
        The proposed solution here is to move the has_hvac_flue argument from the ResidentialAirflow measure out into the HVAC equipment measures (furnace, boiler, unit heater, shared systems). The value assigned to has_hvac_flue will be set as an additional property on the Building model object, and then the airflow measure will parse it from the Building model object. If it doesn't exist, then the value will be set to false.

        Assignees: Joe Robertson



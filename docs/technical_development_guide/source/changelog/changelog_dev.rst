=====================
Development Changelog
=====================
.. changelog::
    :version: v3.5.0
    :released: pending

    .. change::
        :tags: ci, docs, technical reference guide, technical development guide
        :pullreq: 1338
        :tickets: resstock-estimation 437

        **Date**: 2025-1-11

        Title:
        Add ResStock Technical Reference Guide

        Description:
        Add the ResStock Technical Reference Guide to the repository and compile it on github actions to keep the pdf up to date.

        Assignees: Anthony Fontanini

    .. change::
        :tags: feature, characteristics
        :pullreq: 1325
        :tickets: resstock-estimation 437

        **Date**: 2024-12-30

        Title:
        Well pump distribution using AHS

        Description:
        Use 2017-2019 AHS data to create Misc Well Pump distribution (~11% nationally) with respect to geography/urbanity, building type, and foundation type. Previously well pump was randomly assigned via a manually created distribution.

        resstock-estimation: `pull request 437 <https://github.com/NREL/resstock-estimation/pull/437>`_

        Assignees: Lixi Liu

    .. change::
        :tags: characteristics, pool heater
        :pullreq: 1324

        **Date**: 2024-12-3

        Title:
        Add heat pump pool heaters

        Description:
        Add heat pump pool heaters to baseline.

        resstock-estimation: `pull request 436 <https://github.com/NREL/resstock-estimation/pull/436>`_

        Assignees: Janet Reyna

    .. change::
        :tags: workflow, standard data release
        :pullreq: 1329
        :tickets: 1261

        **Date**: 2024-1-23

        Title:
        Add Standard Data Release YAML to GitHub Actions

        Description:
        Add an initial Standard Data Release (SDR) YAML file. Add the SDR upgrade file into CI tests to continue progress towards end-to-end testing.

        Assignees: Anthony Fontanini

================
v2.2.1 Changelog
================

.. changelog::
    :version: v2.2.1
    :released: 2020-02-07

    .. change::
        :tags: characteristics, envelope, bugfix
        :pullreq: 387

        **Date**: 2020-02-07

        Title:
        Addresses #386, fix misc pool tsv files and updates project_singlefamilydetached masonry walls

        Description:
        Add generation of the Geometry Wall Type tsv file for the single-family detached project to the 2009 RECS tsv maker; this corrects the tsv file.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, misc loads, bugfix
        :pullreq: 387

        **Date**: 2020-02-07

        Title:
        Addresses #386, fix misc pool tsv files and updates project_singlefamilydetached masonry walls

        Description:
        Add generation of the Misc Pool tsv file (with Geometry Building Type and Location Region dependencies) to the 2009 RECS tsv maker; this also corrects having pool pumps for all homes.
        Fix pool pump probabilities.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 382

        **Date**: 2020-02-04

        Title:
        Multifamily masonry walls

        Description:
        Update the multifamily project with a Geometry Wall Type tsv file for sampling between wood stud and masonry walls.
        Adding in masonry walls via "Geometry Wall Type" tsv and adding a new dependency in "Insulation Wall". Mimics work done by Maharshi for project_singlefamily. Also created a new tsv_maker for RECS 2009.

        Assignees: Janet Reyna


    .. change::
        :tags: characteristics, recs, bugfix
        :pullreq: 382

        **Date**: 2020-02-04

        Title:
        Multifamily masonry walls

        Description:
        Refactor the RECS tsv makers for years 2009 and 2015.

        Assignees: Janet Reyna



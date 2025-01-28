================
v2.2.2 Changelog
================

.. changelog::
    :version: v2.2.2
    :released: 2020-02-21

    .. change::
        :tags: workflow, weather, bugfix
        :pullreq: 406

        **Date**: 2020-02-21

        Title:
        Release 2_2_2 patch

        Description:
        Update the datapoint initialization script to download weather files to a common zip filename.
        Current curl command in datapoint init script guaranteed aws s3 downloads to work, but not downloads from other hosts (e.g., dropbox). Changing the curl command to be more generic.

        Assignees: Joe Robertson



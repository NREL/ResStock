================
v3.1.1 Changelog
================

.. changelog::
    :version: v3.1.1
    :released: 2023-11-28

    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 1170

        **Date**: 2023-11-28

        Title:
        Use gem version on bsb version strings

        Description:
        Use `Gem::Version` on buildstockbatch version string comparisons so that, e.g., '2023.10.0' < '2023.5.0' does not evaluate to true.
        Patched release with version comparison fix.

        Assignees: Joe Robertson



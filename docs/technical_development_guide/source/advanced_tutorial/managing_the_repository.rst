Managing the Repository
=======================

At this point in the tutorial, it is assumed that you have checked out a new branch that is up-to-date with the either the ``develop`` or ``latest-os-hpxml`` branch of the `ResStock <https://github.com/NREL/resstock>`_ repository.
Note that if your changes are intended to be merged into the ``develop`` branch of the `ResStock <https://github.com/NREL/resstock>`_ repository, a pull request review is required.

ResStock contains a `git subtree <https://www.atlassian.com/git/tutorials/git-subtree>`_ to the `OpenStudio-HPXML <https://github.com/NREL/OpenStudio-HPXML>`_ repository.
The subtree is located at ``resources/hpxml-measures``, and is basically a direct copy of all the folders and files contained in OpenStudio-HPXML for a particular commit.

When using or testing a specific OpenStudio-HPXML branch, the subtree at ``resources/hpxml-measures`` can be updated using a set of simple commands.
Files located at ``resources/hpxml-measures`` should typically never be directly edited or modified manually.
Once ``resources/hpxml-measures`` has been updated, there are a few :ref:`remaining steps<post-git-subtree-steps>` for ensuring ResStock is properly connected to OpenStudio-HPXML.

ResStock's ``develop`` branch generally points to the latest ``master`` branch of OpenStudio-HPXML.
A standing ``latest-os-hpxml`` branch in ResStock helps to ensure that ResStock stays up-to-date with OpenStudio-HPXML's development.
The ``latest-os-hpxml`` is periodically merged into ``develop`` using a "Latest OS-HPXML" pull request.

There is a ResStock maintenance task for keeping ``latest-os-hpxml`` up-to-date, and periodically merging its corresponding pull request.
Other ResStock tasks are developmental in nature and include, e.g.:

- TSV file updates from `resstock-estimation <https://github.com/NREL/resstock-estimation>`_
- technical documentation updates
- tests and/or CI config updates
- core OpenStudio measure updates

Any of these types of updates may or may not relate to or use files contained in the OpenStudio-HPXML ``resources-hpxml-measures`` subtree.
Depending on how anticipated ResStock changes and updates relate to OpenStudio-HPXML, branching from either ResStock's ``develop`` or ``latest-os-hpxml`` branch may be more appropriate.
The following describes general guidelines for:

- when to branch from ``develop`` vs. ``latest-os-hpxml``
- how to keep your branch up-to-date with either ResStock or OpenStudio-HPXML
- how to eventually merge your branch into ResStock

Using these guidelines should help to ensure a simple and straightforward merging of new ResStock changes and updates.


.. _develop_vs_latest_os_hpxml:

``develop`` vs. ``latest-os-hpxml``
-----------------------------------

Use ``develop`` for the maintenance task of keeping an up-to-date ``latest-os-hpxml`` branch.
For updating ResStock's ``develop`` branch to point to OpenStudio-HPXML's ``master`` branch, branch from ``develop`` (with branch name ``latest-os-hpxml``), and then enter the following command:

.. code:: bash

  $ openstudio tasks.rb update_resources

See :doc:`running_task_commands` for more information and context about running tasks.
Executing the ``update_resources`` task will issue the appropriate ``git subtree ...`` command for syncing ResStock with OpenStudio-HPXML's ``master`` branch.

For pulling in and testing a specific OpenStudio-HPXML branch (i.e., that is not the ``master`` branch), create a test branch in ResStock from ``latest-os-hpxml``.
Then enter the following command:

.. code:: bash

  $ git subtree pull --prefix resources/hpxml-measures https://github.com/NREL/OpenStudio-HPXML.git <branch_or_tag> --squash

where ``<branch_or_tag>`` represents the OpenStudio-HPXML branch (or tag) name to be pulled in and tested.

Note that the previous command essentially mirrors what ``update_resources`` calls, but with a user-specified branch (or tag) name.

TODO

.. _update_branch:

Update branch
-------------

TODO

.. _merge_branch:

Merge branch
------------

TODO

.. _post-git-subtree-steps:

Post ``git subtree`` steps
--------------------------

After pulling a branch of OpenStudio-HPXML into ResStock, a few additional steps are involved:

1. Run ``openstudio tasks.rb update_measures``.
   
   This applies rubocop auto-correct to measures, updates measure.xml files, and ensures arguments of the ResStockArguments measure reflect BuildResidentialHPXML.
   
   Although ``update_measures`` has the same name as OpenStudio-HPXML's ``update_measures`` task, it is applied only to ResStock's core measures.
   
2. Run ``openstudio measures/ResStockArguments/tests/resstock_arguments_test.rb``.

3. Update ``resources/options_lookup.tsv`` with any new ResStockArguments arguments introduced by BuildResidentialHPXML.

4. Update CSV files in the ``resources/data/dictionary`` folder.
   
   This addresses any input/output data dictionary changes introduced by OpenStudio-HPXML workflow updates.

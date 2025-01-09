OpenStudio-HPXML
================

ResStock contains a `git subtree <https://www.atlassian.com/git/tutorials/git-subtree>`_ to the `OpenStudio-HPXML <https://github.com/NREL/OpenStudio-HPXML>`_ repository.
The subtree is located at ``resources/hpxml-measures``, and is basically a direct copy of all the folders and files contained in OpenStudio-HPXML.
As OpenStudio-HPXML is updated, ResStock's ``develop`` branch is periodically updated to point to the latest ``master`` branch of OpenStudio-HPXML, helping to ensure that ResStock stays up-to-date with OpenStudio-HPXML's development.
It may also be helpful to test an OpenStudio-HPXML branch (or tag) using a branch of ResStock.
In both cases, the subtree at ``resources/hpxml-measures`` can be updated using a set of simple commands.
Files located at ``resources/hpxml-measures`` should typically never be directly edited or modified manually.

Once ``resources/hpxml-measures`` has been updated, there are a few other steps for ensuring ResStock is properly connected to OpenStudio-HPXML.

.. _latest-os-hpxml:

Syncing w/latest
----------------

For updating ResStock's ``develop`` branch to point to OpenStudio-HPXML's ``master`` branch, branch off of ``develop`` (e.g., with branch name ``latest-os-hpxml``), and then enter the following command:

.. code:: bash

  $ openstudio tasks.rb update_resources

See :doc:`running_tasks` for more information and context about running tasks.
Executing the ``update_resources`` task will issue the appropriate ``git subtree ...`` command for syncing ResStock with OpenStudio-HPXML's ``master`` branch.

.. _branch-os-hpxml:

Testing a branch
----------------

For pulling in and testing a specific OpenStudio-HPXML branch (i.e., that is not the ``master`` branch), first create a test branch in ResStock.
Then enter the following command:

.. code:: bash

  $ git subtree pull --prefix resources/hpxml-measures https://github.com/NREL/OpenStudio-HPXML.git <branch_or_tag> --squash

where ``<branch_or_tag>`` represents the OpenStudio-HPXML branch (or tag) name to be pulled in and tested.

Note that the previous command essentially mirrors what ``update_resources`` calls, but with a user-specified branch (or tag) name.

.. _other-steps:

Other steps
-----------

After pulling a branch of OpenStudio-HPXML into ResStock, a few additional steps are involved:

1. Run ``openstudio tasks.rb update_measures``; this applies rubocop auto-correct to measures, updates measure.xml files, and ensures arguments of the ResStockArguments measure reflect BuildResidentialHPXML
2. Run ``openstudio measures/ResStockArguments/tests/resstock_arguments_test.rb``; update ``resources/options_lookup.tsv`` with any new ResStockArguments arguments introduced by BuildResidentialHPXML
3. Update CSV files in the ``resources/data/dictionary`` folder; this addresses any input/output data dictionary changes introduced by OpenStudio-HPXML workflow updates

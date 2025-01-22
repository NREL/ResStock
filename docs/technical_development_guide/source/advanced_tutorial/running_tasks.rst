Running Tasks
=============

Run ``openstudio tasks.rb`` to see available task commands:

.. code:: bash

  $ openstudio tasks.rb 
  ERROR: Missing command.
  Usage: openstudio tasks.rb [COMMAND]
  Commands:
    update_measures
    update_resources
    integrity_check_national
    integrity_check_testing
    download_weather

.. _update-measures:

Update Measures
---------------

Use ``openstudio tasks.rb update_measures`` to apply rubocop auto-correct to measures, and to update measure.xml files:

.. code:: bash

  $ openstudio tasks.rb update_measures
  Applying rubocop auto-correct to measures...
  Running RuboCop...

  91 files inspected, no offenses detected
  Updating measure.xmls...
  Done.

Update Resources
----------------

Use ``openstudio tasks.rb update_resources`` to update files in ``resources/hpxml-measures`` with the latest version of OpenStudio-HPXML.

.. code:: bash

  $ openstudio tasks.rb update_resources
  remote: Enumerating objects: 188817, done.
  remote: Counting objects: 100% (15305/15305), done.
  ...
  From https://github.com/NREL/OpenStudio-HPXML
   * branch                    master     -> FETCH_HEAD
  Merge made by the 'ort' strategy.
  ...

.. _integrity-checks:

Integrity Checks
----------------

Run ``openstudio tasks.rb integrity_check_<project_name>``, where ``<project_name>`` matches the project you are working with. If no task exists for the project you are working with, extend the list of integrity check tasks to accommodate your project by modifying the ``tasks.rb`` file. An example for running a project's integrity checks is given below:

.. code:: bash

  $ openstudio tasks.rb integrity_check_national
  Checking for issues with project_national/Location Region...
  Checking for issues with project_national/Location EPW...
  Checking for issues with project_national/Vintage...
  Checking for issues with project_national/Heating Fuel...
  Checking for issues with project_national/Usage Level...
  ...

If the integrity check for a given project fails, you will need to update either your tsv files and/or the ``resources/options_lookup.tsv`` file. See :doc:`options_lookup` for information about the ``options_lookup.tsv`` file.

.. download-weather:

Download Weather
----------------

Run ``openstudio tasks.rb download_weather`` to download available EPW weather files:

.. code:: bash

  $ openstudio tasks.rb download_weather
  Downloading /files/156/BuildStock_TMY3_FIPS.zip (  1%) 
  Downloading /files/156/BuildStock_TMY3_FIPS.zip (  2%) 
  Downloading /files/156/BuildStock_TMY3_FIPS.zip (  3%)
  ...

.. rakefile:

Rakefile
--------

Once you have completed instructions found in :doc:`installer_setup`, you can then use the `Rakefile <https://github.com/NREL/resstock/blob/develop/Rakefile>`_ contained at the top level of this repository. You can run rake task(s) for :ref:`performing integrity checks on project inputs <integrity-checks>` as well as executing various tests.

Run ``rake -T`` to see the list of possible rake tasks. The ``-T`` is replaced with the chosen task.

.. code:: bash

  $ rake -T
  rake unit_tests:integrity_check_tests     # Run tests for integrity_check_t...
  rake unit_tests:measure_tests             # Run tests for measure_tests
  rake unit_tests:project_integrity_checks  # Run tests for project_integrity...
  rake workflow:analysis_tests              # Run tests for analysis_tests

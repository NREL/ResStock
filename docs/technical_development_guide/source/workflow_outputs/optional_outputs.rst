.. _optional_outputs:

Optional Outputs
================

Optional outputs include component loads, emissions, utility bills, and quantities of interest.
Other timeseries outputs related to zone temperatures/setpoints, airflow rates, weather file data, and user-requested EnergyPlus output variables can also be requested.

To be generated, some optional outputs need only a single switch enabled (e.g., component loads).
Others need additional input arguments specified (e.g., emissions, utility bills).
Again, see the `Residential HPXML Workflow Generator <https://buildstockbatch.readthedocs.io/en/latest/workflow_generators/residential_hpxml.html>`_ documentation page for more information on how to enable optional output requests.

Component Loads
***************

Component loads represent the estimated contribution of different building components to the annual heating/cooling building loads.

.. csv-table::
   :file: csv_tables/component_loads.csv
   :header-rows: 1

These outputs require that only a single switch is enabled.
See the `Residential HPXML Workflow Generator <https://buildstockbatch.readthedocs.io/en/latest/workflow_generators/residential_hpxml.html>`_ documentation page (i.e., ``build_existing_model`` section) for more information.

See the OpenStudio-HPXML Workflow Outputs sections on `Annual Component Building Loads <https://openstudio-hpxml.readthedocs.io/en/latest/workflow_outputs.html#annual-component-building-loads>`_ and `Timeseries Outputs <https://openstudio-hpxml.readthedocs.io/en/latest/workflow_outputs.html#timeseries-outputs>`_ for more information about component loads.

Emissions
*********

Optional emissions outputs include annual total, by fuel, and by end use, for each emissions scenario requested.
See the `Residential HPXML Workflow Generator <https://buildstockbatch.readthedocs.io/en/latest/workflow_generators/residential_hpxml.html>`_ documentation page (i.e., ``emissions`` section) for more information on how to request emissions outputs by scenario.

See the OpenStudio-HPXML Workflow Outputs sections on `Annual Emissions <https://openstudio-hpxml.readthedocs.io/en/latest/workflow_outputs.html#annual-emissions>`_ and `Timeseries Outputs <https://openstudio-hpxml.readthedocs.io/en/latest/workflow_outputs.html#timeseries-outputs>`_ for more information about emissions.

In the table below, "<type>" refers to the ``type`` of emission (e.g., "CO2e", "NOx", etc.) specified and "<scenario_name>" refers to the ``scenario_name`` (e.g., "LRMER_MidCase_15", "AER_HighRECost_1", etc.) specified.
See the list of all available emissions scenario name choices at https://github.com/NREL/resstock/tree/develop/resources/data/cambium.

.. note::
  Output names may show "<type>" and "<scenario_name>" in some form of "underscore" case. For example, "CO2e" may become "co2e" (or "co_2_e") and "LRMER_MidCase_15" may become "lrmer_mid_case_15" (or "lrmer_midcase_15").

.. csv-table::
   :file: csv_tables/emissions.csv
   :header-rows: 1

Utility Bills
*************

For each utility bill scenario requested, optional utility bill outputs include:

- Annual: fixed costs and energy costs by fuel type (including PV credits for electricity), and total costs (including by fuel type)
- Monthly: total costs (including by fuel type)

See the `Residential HPXML Workflow Generator <https://buildstockbatch.readthedocs.io/en/latest/workflow_generators/residential_hpxml.html>`_ documentation page (i.e., ``utility_bills`` and ``simulation_output_report`` sections) for more information on how to request utility bill outputs by scenario.

See the OpenStudio-HPXML Workflow Outputs section on `Utility Bill Outputs <https://openstudio-hpxml.readthedocs.io/en/latest/workflow_outputs.html#utility-bill-outputs>`_ for more information about utility bill outputs.

In the table below, "<scenario_name>" refers to the ``scenario_name`` (e.g., "Bills") specified.
Like emissions, output names may show "<scenario_name>" in some form of "underscore" case. For example, "Bills" may become "bills".

.. csv-table::
   :file: csv_tables/utility_bills.csv
   :header-rows: 1

Quantities of Interest
**********************

These outputs require that only a single switch is enabled.
See the `Residential HPXML Workflow Generator <https://buildstockbatch.readthedocs.io/en/latest/workflow_generators/residential_hpxml.html>`_ documentation page (i.e., ``reporting_measures`` section) for more information on how to request quantities of interest outputs.

.. csv-table::
   :file: csv_tables/qoi_report.csv
   :header-rows: 1

Other Timeseries
****************

Other timeseries outputs include zone temperatures/setpoints, airflow rates, weather file data, and user-requested EnergyPlus output variables.
See the `Residential HPXML Workflow Generator <https://buildstockbatch.readthedocs.io/en/latest/workflow_generators/residential_hpxml.html>`_ documentation page (i.e., ``simulation_output_report`` section) for more information on how to request other timeseries outputs.

See the OpenStudio-HPXML Workflow Outputs section on `Timeseries Outputs <https://openstudio-hpxml.readthedocs.io/en/latest/workflow_outputs.html#timeseries-outputs>`_ for more information about other timeseries outputs.

.. csv-table::
   :file: csv_tables/other_timeseries.csv
   :header-rows: 1

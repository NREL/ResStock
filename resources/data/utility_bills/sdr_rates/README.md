In the YML file's "simple_filepath" field for utility bill scenario definitions, enter a relative file path to a TSV lookup file (e.g., "data/simple_rates/State.tsv") containing user-defined values corresponding to arguments for fixed costs, marginal rates, and PV.
The first column of the TSV lookup file contains the name of a chosen parameter for which sets of argument values are assigned according to its options.
Any blank fields, or missing options for a parameter not specified in the TSV lookup file, will be defaulted.

See the Simple section of OpenStudio-HPXML's documentation for [Electricity Rates](https://openstudio-hpxml.readthedocs.io/en/latest/workflow_inputs.html#electricity-rates), and [Fuel Rates](https://openstudio-hpxml.readthedocs.io/en/latest/workflow_inputs.html#fuel-rates), for more information about arguments for fixed charges, marginal rates, and PV.
Refer to BuildStockBatch's documentation for [Residential HPXML Workflow Generator](https://buildstockbatch.readthedocs.io/en/stable/workflow_generators/residential_hpxml.html) for more information about YML file arguments.

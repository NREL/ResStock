Testing Framework
=================

A large number of tests are automatically run for every code change in the GitHub repository.

The current set of tests include:

- Successful simulations for all sample files
- ASHRAE 140
- RESNET® HERS® HVAC tests
- RESNET HERS DSE tests
- RESNET HERS Hot Water tests
- ACCA Manual J tests

Running Tests Locally
---------------------

All ASHRAE 140 tests can be run using:

| ``openstudio test_ashrae_140.rb``
| 

All RESNET HERS tests can be run using:

| ``openstudio test_hers.rb``
| 

Or individual tests can be run by specifying the name of the test. For example:

| ``openstudio test_hers.rb --name=test_hers_hvac``
| 

Test results in CSV format are created at ``workflow/tests/test_results`` and can be used to populate RESNET Excel spreadsheet forms. 
RESNET acceptance criteria are also implemented as part of the tests to check for test failures.

At the completion of the test, there will be output that denotes the number of failures/errors like so:

``Finished in 36.067116s, 0.0277 runs/s, 0.9704 assertions/s.``
``1 runs, 35 assertions, 0 failures, 0 errors, 0 skips``

Software developers may find it convenient to export HPXML files with the same name as the test files included in the repository.
This allows issuing the commands above to generate test results.

Official Test Results
---------------------

The official OpenStudio-HPXML test results can be found in any release or any checkout of the code at ``workflow/tests/base_results``.
The results are based on using the HPXML files found under ``workflow/tests``.

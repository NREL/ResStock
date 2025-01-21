================
v2.1.0 Changelog
================

.. changelog::
    :version: v2.1.0
    :released: 2019-11-05

    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 333

        **Date**: 2019-10-23

        Title:
        Update the cw options a bit

        Description:
        Additional options for EnergyStar clothes washer, clothes dryer, dishwasher.
        Reduce IMEF on the "more" efficient option. Change drum volume on "most" efficient option. Add links in unit tests to actual clothes washer examples pulled from energystar.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 333

        **Date**: 2019-10-23

        Title:
        Update the cw options a bit

        Description:
        Bugfix for some clothes washer, dishwasher options causing increased energy consumption.
        Reduce IMEF on the "more" efficient option. Change drum volume on "most" efficient option. Add links in unit tests to actual clothes washer examples pulled from energystar.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, testing, bugfix
        :pullreq: 331

        **Date**: 2019-10-18

        Title:
        Enforce rubocop as separate ci test

        Description:
        Enforce rubocop as CI test so code with offenses cannot be merged.
        Code can no longer be committed to the repo with rubocop offenses.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 329

        **Date**: 2019-10-17

        Title:
        Add more efficient options for dw, cw, cd

        Description:
        Additional options for EnergyStar clothes washer, clothes dryer, dishwasher.
        We need "more efficient" options for idsm-scout and mf aedg. Currently, the dw, cw options are causing increased energy consumption. Janet had started to look into this. Turns out things related to the energy guide label, like rated_annual_energy, annual_cost, and test_date, had not been updated.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 330

        **Date**: 2019-10-17

        Title:
        Fix assignment of bedrooms to units

        Description:
        Bugfix when specifying numbers of bedrooms to building units.
        This fixes a bug when you try to assign, e.g., 3, 2, 1, 2, 2, 3 numbers of bedrooms to 6 building units.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 329

        **Date**: 2019-10-17

        Title:
        Add more efficient options for dw, cw, cd

        Description:
        Bugfix for some clothes washer, dishwasher options causing increased energy consumption.
        We need "more efficient" options for idsm-scout and mf aedg. Currently, the dw, cw options are causing increased energy consumption. Janet had started to look into this. Turns out things related to the energy guide label, like rated_annual_energy, annual_cost, and test_date, had not been updated.

        Assignees: Joe Robertson


    .. change::
        :tags: software, openstudio, feature
        :pullreq: 322

        **Date**: 2019-10-15

        Title:
        OS 2.9.0

        Description:
        Update to OpenStudio v2.9.0
        Try out OpenStudio 2.9.0: rc1, rc2, rc3, and final.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, setpoints, feature
        :pullreq: 272

        **Date**: 2019-09-25

        Title:
        new distributions for heating/cooling tsps with offsets

        Description:
        Update all projects with new heating/cooling setpoint, offset, and magnitude distributions
        New/updated tsvs for distributions of heating/cooling setpoints and setpoint offsets. Queried from RECS at the AIA climate zone level. Options_lookup is updated with new options.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, documentation, feature
        :pullreq: 321

        **Date**: 2019-09-23

        Title:
        Talk to downselect point that datapoints are before downselect logic.

        Description:
        Update documentation to clarify downselect logic parameters.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, testing, bugfix
        :pullreq: 320

        **Date**: 2019-09-23

        Title:
        Fixes #319

        Description:
        Add tests to ensure that the Run Measure argument is correctly defined in all Apply Upgrade measures for all projects.
        Fixes #319. Added tests to ensure that the Run Measure argument is correctly defined in all Apply Upgrade measures for all projects.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 314

        **Date**: 2019-09-20

        Title:
        Example YAML file upload

        Description:
        Create example project yaml files for use with buildstockbatch.
        Some comments on correct defaults included, could use more.

        Assignees: Elaina Present


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 317

        **Date**: 2019-09-19

        Title:
        Create pull_request_template.md

        Description:
        Create a pull request template to facilitate development.
        Start creating a pull request template.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 315

        **Date**: 2019-09-19

        Title:
        Log the error string along with backtrace

        Description:
        Log the error message along with the backtrace when an applied measure fails.
        Currently, the apply_measure function only logs the error backtrace when the measure being applied fails, but not the actual error message. This fixes the issue, and logs the error message alongside the backtrace.

        Assignees: Rajendra Adhikari


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 310

        **Date**: 2019-09-03

        Title:
        Ehale ignore measures

        Description:
        Add argument to BuildExistingModel measure that allows the user to ignore measures.
        This branch adds the feature of being able to having the ResStock BuildExistingModel ignore measures. There will be a companion pull request to buildstockbatch that passes that argument through the project yml.

        Assignees: Elaine Hale


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 312

        **Date**: 2019-08-23

        Title:
        Get past runner values of any type

        Description:
        Able to get past runner values of any type, and not just as string.
        Can only get runner past values as string.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, reporting, feature
        :pullreq: 304

        **Date**: 2019-08-21

        Title:
        Fixes/updates for SimulationOutputReport measure

        Description:
        Report all cost multipliers in the SimulationOutputReport measure.
        Fix bug in cost multipliers for "minimally collapsed" building.
        SimulationOutputReport unit tests for "minimally collapsed" building.
        Report all cost multipliers in results csv.
        Regression tests include all cost multipliers.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, ducts, bugfix
        :pullreq: 309

        **Date**: 2019-08-21

        Title:
        Ducts sometimes placed in garage attic

        Description:
        Bugfix for ducts occasionally getting placed in the garage attic instead of only unfinished attic.
        This changes the space type for the 1-story building garage attic from unfinished attic to garage attic. This should fix issues brought up by @jonwinkler.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, solar hot water, bugfix
        :pullreq: 307

        **Date**: 2019-08-20

        Title:
        Addresses #306

        Description:
        Ensure that autosizing does not draw the whole tank volume in one minute for solar hot water storage tank.
        setUseSideDesignFlowRate for solar hw measure.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 308

        **Date**: 2019-08-20

        Title:
        Remove invalid characters from option names

        Description:
        Remove invalid characters from option names for consistency with buildstockbatch.
        Fixes options that would fail the validation proposed in NREL/buildstockbatch#99.

        Assignees: Nate Moore


    .. change::
        :tags: workflow, fixtures, feature
        :pullreq: 305

        **Date**: 2019-08-16

        Title:
        Low flow fixture options

        Description:
        Add options for low flow fixtures.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, hvac, feature
        :pullreq: 292

        **Date**: 2019-08-14

        Title:
        Add 96% AFUE Propane Boiler

        Description:
        Additional options for HVAC, dehumidifier, clothes washer, misc loads, infiltration, etc.
        Propane boilers go up to 97% AFUE in the Energy STAR database. Oil boilers only go up to 91%.

        Assignees: Elaina Present


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 302

        **Date**: 2019-08-08

        Title:
        Add TM to ResStock and ComStock

        Description:
        Add references to ResStock trademark in both the license and readme files.
        Added to first references in:
        
        - README.md
        - LICENSE.md

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, upgrades, feature
        :pullreq: 296

        **Date**: 2019-07-31

        Title:
        Additional max-tech levels for options_lookup

        Description:
        Additional "max-tech" options for slab, wall, refrigerator, dishwasher, clothes washer, and lighting.
        Added 112 lm/W LED option, EF 22.2 refrigerator option, R20 Whole Slab insulation option, Wood Stud R-13 with R-20 external XPS option, EnergyStar Most Efficient clothes washers, and EnergyStar Most Efficient Dishwashers at 199 rated Kwh.

        Assignees: Elaina Present


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 295

        **Date**: 2019-07-18

        Title:
        Fix bug when you specify all br but not ba

        Description:
        Bugfix for when bedrooms are specified for each unit but bathrooms are not.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, upgrades, feature
        :pullreq: 293

        **Date**: 2019-07-16

        Title:
        Increase upgrade options from 20 to 25

        Description:
        Increase number of possible upgrade options from 10 to 25.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, demand response, feature
        :pullreq: 276

        **Date**: 2019-07-15

        Title:
        Demand response

        Description:
        Add new ResidentialDemandResponse measure that allows for 8760 DR schedules to be applied to heating/cooling schedules.
        New measure ResidentialDemandResponse that allows for 8760 DR schedules to be applied to heating and/or cooling schedules.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 282

        **Date**: 2019-07-12

        Title:
        Add options and write EV code

        Description:
        Add EV options and update ResidentialMiscLargeUncommonLoads measure with new electric vehicle argument.
        Also includes writing new options/arguments in measure.rb, which should be closely examined for errors due to my inexperience with that task.

        Assignees: Nate Moore


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 291

        **Date**: 2019-07-12

        Title:
        Add buildstockbatch ymls to each resstock project

        Description:
        Create example project yaml files for use with buildstockbatch for convenience.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 287

        **Date**: 2019-07-09

        Title:
        Add year argument to simulation controls measure

        Description:
        Update ResidentialSimulationControls measure to include a calendar year argument for controlling the simulation start day of week.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 286

        **Date**: 2019-07-09

        Title:
        Don't request output for "invalid" datapoints

        Description:
        Skip any reporting measure output requests for datapoints that have been registered as invalid.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, testing, bugfix
        :pullreq: 280

        **Date**: 2019-07-02

        Title:
        Update testing project to sweep thru more options

        Description:
        Update testing project to sweep through more options.

        Assignees: Nate Moore


    .. change::
        :tags: workflow, documentation, bugfix
        :pullreq: 285

        **Date**: 2019-07-02

        Title:
        Minor readthedocs updates

        Description:
        Updates, edits, and clarification to the documentation.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 278

        **Date**: 2019-06-25

        Title:
        Moar options

        Description:
        Additional options for HVAC, dehumidifier, clothes washer, misc loads, infiltration, etc.
        Add items to options_lookup available in master branch.

        Assignees: Nate Moore


    .. change::
        :tags: workflow, documentation, bugfix
        :pullreq: 274

        **Date**: 2019-06-19

        Title:
        Some RTD updates

        Description:
        Updates, edits, and clarification to the documentation.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, upgrades, feature
        :pullreq: 273

        **Date**: 2019-06-18

        Title:
        Increase upgrade options from 10 to 20

        Description:
        Increase number of possible upgrade options from 10 to 25.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, documentation, bugfix
        :pullreq: 270

        **Date**: 2019-06-17

        Title:
        Advanced tutorial updates

        Description:
        Updates, edits, and clarification to the documentation.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 264

        **Date**: 2019-06-13

        Title:
        New parameters & options

        Description:
        Additional options for HVAC, dehumidifier, clothes washer, misc loads, infiltration, etc.
        New options and parameters for existing OS measures.
        Purpose is to expand OS modeling capability, driven in this case by an outside client interested in using E+ as their simulation engine.

        Assignees: Nate Moore


    .. change::
        :tags: workflow, hvac, bugfix
        :pullreq: 263

        **Date**: 2019-06-06

        Title:
        HVAC autosizing and add/replace fixes

        Description:
        Various HVAC-related fixes for buildings with central systems.
        When a model has both a central system and non central system, don't autosize the non central system (e.g., central boiler with room ac).
        Cannot have heating-only fan coil anymore; the ZoneHVACUnitHeater object was not being autosized correctly and was resulting in zero heating energy.
        Don't remove the cooling-only fan coil when applying a heating-only non central system (e.g., cooling-only fan coil with furnace).

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 255

        **Date**: 2019-05-28

        Title:
        Addresses #243 and #254

        Description:
        Bugfix for assuming that all simulations are exactly 365 days.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, testing, feature
        :pullreq: 261

        **Date**: 2019-05-24

        Title:
        Additional example workflow osws

        Description:
        Additional example workflow osw files using TMY/AMY2012/AMY2014 weather for use in regression testing:
        
        - TMY
        - AMY2012
        - AMY2014

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, testing, feature
        :pullreq: 259

        **Date**: 2019-05-22

        Title:
        Store example osw annual simulation results on ci

        Description:
        Additional example workflow osw files using TMY/AMY2012/AMY2014 weather for use in regression testing.
        Similar to how @shorowit does "regression testing" on https://github.com/NREL/OpenStudio-HPXML.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, hvac, bugfix
        :pullreq: 258

        **Date**: 2019-05-21

        Title:
        Typo in heating coil defrost strategy

        Description:
        Bugfix for heating coil defrost strategy.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, lighting, feature
        :pullreq: 252

        **Date**: 2019-05-15

        Title:
        Optional exterior "holiday" lights

        Description:
        Split ResidentialLighting into separate ResidentialLightingInterior and ResidentialLightingOther (with optional exterior holiday lighting) measures.
        This involves modifications to:
        
        - ResidentialLightingOther measure
        
          - 4 new arguments (daily energy use, holiday period start, holiday period end, holiday schedule)
          - unit test for verifying that exterior lighting increases by, e.g., 41 days * 1.1 kWh/day = 45 kWh
          
        - lighting.rb
        
          - new apply_exterior_holiday method
          - assigning end use subcategories to all light objects
          
        - options_lookup.tsv and testing project
        
          - existing lighting options now get default holiday argument values
          - new lighting option to test exterior holiday lighting
          
        - SimulationOutputReport / TimeseriesCSVExport measures
        
          - custom meters for "garage lighting" and "exterior holiday lighting"
          - reporting "garage lighting" and "exterior holiday lighting"

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, lighting, feature
        :pullreq: 244

        **Date**: 2019-05-06

        Title:
        Lighting measure changes

        Description:
        Split ResidentialLighting into separate ResidentialLightingInterior and ResidentialLightingOther (with optional exterior holiday lighting) measures.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, reporting, feature
        :pullreq: 245

        **Date**: 2019-05-02

        Title:
        Register climate zones

        Description:
        Register climate zones (BA and IECC) based on the simulation EPW file.
        This is a pretty simple and straightforward PR: it adds two columns "climate_zone_ba" and "climate_zone_iecc" (based on the epw) to the results csv.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, testing, feature
        :pullreq: 237

        **Date**: 2019-04-22

        Title:
        Integrity check unit tests

        Description:
        Unit tests and performance improvements for integrity checks.
        Adds unit tests to make sure that the integrity checks are covering various potential scenarios that would cause errors. Each unit test consists of a housing_characteristics dir with custom TSVs and corresponding options in the test_options_lookup.tsv that should cause the error. The unit tests check that the appropriate error message is hit.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, testing, feature
        :pullreq: 239

        **Date**: 2019-04-22

        Title:
        Integrity check performance improvement

        Description:
        Unit tests and performance improvements for integrity checks.
        Dramatically improves the speed of performing measure argument checks. Rather than checking every combination of option for every parameter that contributes to a single measure's arguments, we now pick options from each parameter in step.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 228

        **Date**: 2019-04-12

        Title:
        TSV Speed Improvements

        Description:
        Unit tests and performance improvements for integrity checks.
        This PR substantially speeds up integrity checks for TSVs with large numbers of rows (and has the side benefit of speeding up sampling) by using caching.

        Assignees: Scott Horowitz



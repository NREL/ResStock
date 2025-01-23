================
v2.5.0 Changelog
================

.. changelog::
    :version: v2.5.0
    :released: 2022-02-09

    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 821

        **Date**: 2022-02-03

        Title:
        Update national project YAMLs with unit counts from ACS 2019 5-year

        Description:
        Update the number of units represented in the national project YAML files to the American Community Survey 2019 5-year estimate.
        In the YAML files, the n_buildings_represented was 110,000,000. This estimate is a bit low compared to the ACS 2019 5-year estimate of 136,569,411.
        This PR updates the YAML files to include the ACS 2019 5-year estimate of the number of housing units.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 817

        **Date**: 2022-02-03

        Title:
        Finished Roof Bugfix

        Description:
        Properly apply roof insulation when the attic type is Finished Attic or Cathedral Ceilings.
        Insulation Roof options are not applying insulation correctly because attic spaces are modeled as unfinished, and no applicable surfaces are found in the ResidentialConstructionsFinishedRoof measure. This PR applies roof insulation via the ResidentialConstructionsUnfinishedAttic instead.
        This keeps attic spaces modeled as unfinished, correctly applies insulation, and better aligns with the resstock-hpxml attic construction.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 818

        **Date**: 2022-02-02

        Title:
        ServerDirectoryCleanup debug argument

        Description:
        Add arguments to the ServerDirectoryCleanup measure for controlling deletion of files in the run folder.
        Setting to true would set all "retain" arguments to true.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, emissions, feature
        :pullreq: 791

        **Date**: 2022-02-01

        Title:
        ResStock-HPXML: Emissions calculations (e.g., CO2)

        Description:
        Add ability to calculate emissions for various scenarios.
        ResStock-HPXML: CO2 Emissions calculations.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, solar hot water, bugfix
        :pullreq: 809

        **Date**: 2022-01-27

        Title:
        Backport unit conversion bugfixes for solar hot model from OS-HPXML

        Description:
        Fixes unit conversion bugs in solar hot water model.

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, envelope, bugfix
        :pullreq: 789

        **Date**: 2022-01-18

        Title:
        Backport material properties from ResStock-HPXML

        Description:
        Fixes for wall constructions: remove wood sheathing on CMU and brick walls; better data for exterior finish absorptances and wall densities.
        Update exterior finish absorptance and wall density values to align with ResStock-HPXML values. Also removes sheathing layer from CMU and brick wall types.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 759

        **Date**: 2021-11-17

        Title:
        add geometry_story_bin, add story_bin as dependency to geometry_wall_type

        Description:
        Add Geometry Story Bin tsv and Geometry Story Bin dependency to Geometry Wall Type.
        Revert wall type constraint that assumes all brick facades built >1960 are wood-framed with 4" face brick. Also add constraint to force all buildings > 8 stories to have steel-framed wall type.
        Resolves:
        
        - Missing building height dependency in Geometry Wall Type (resstock-estimation#175)
        - Higher than expected brick %s in wall type in recent vintages (resstock-estimation#145) - reverting fix for high brick %s in newer vintages

        resstock-estimation: `pull request 177 <https://github.com/NREL/resstock-estimation/pull/177>`_

        Assignees: Lixi Liu


    .. change::
        :tags: workflow, climate zones, feature
        :pullreq: 764

        **Date**: 2021-11-08

        Title:
        IECC Zone argument for ResidentialLocation

        Description:
        Add optional argument to ResidentialLocation measure for setting the IECC climate zone.
        Backport water heater location logic (based on IECC zone).

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, unmet hours, bugfix
        :pullreq: 700

        **Date**: 2021-09-03

        Title:
        Fix unmet hours

        Description:
        Fixes hours setpoint not met output to exclude A) no heating and/or cooling equipment and B) finished basements.
        Excludes reported unmet hours for A) no heating and/or cooling equipment and B) finished basements.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, hvac, bugfix
        :pullreq: 694

        **Date**: 2021-08-31

        Title:
        Disaggregate fan coil fan energy use

        Description:
        Disaggregate the shared fan coil's fan energy use into heating and cooling.
        Was previously all lumped into ElectricityFansCooling with a FIXME.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, pv, feature
        :pullreq: 673

        **Date**: 2021-08-25

        Title:
        add PV distributions

        Description:
        Add PV ownership and PV system size distributions using 2019 Tracking the Sun and GTM report on solar installation.
        This PR introduces PV systems into ResStock.

        Assignees: Lixi Liu


    .. change::
        :tags: characteristics, mechanical ventilation, feature
        :pullreq: 675

        **Date**: 2021-08-19

        Title:
        Update mechanical ventilation

        Description:
        Updates mechanical ventilation options/model to ASHRAE 62.2-2019 and adds a "Flow Rate, Mechanical Ventilation (cfm)" output.
        Updates mechanical ventilation to ASHRAE 62.2-2019. This affects both the Qfan requirement for a mechanical ventilation system as well as how mechanical ventilation interacts with infiltration on a timestep basis. Also adds a 'Flow Rate, Mechanical Ventilation (cfm)' cost multiplier.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 661

        **Date**: 2021-08-16

        Title:
        Clean up ServerDirectoryCleanup measure

        Description:
        Add arguments to the ServerDirectoryCleanup measure for controlling deletion of files in the run folder.
        Update this measure to have arguments for including/excluding files in the run directory. Would need to update the buildstockbatch workflow generator to accommodate this.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, cost multipliers, bugfix
        :pullreq: 674

        **Date**: 2021-08-05

        Title:
        Exclude corridor doors in door area cost multiplier

        Description:
        Exclude adiabatic doors when outputting the door area cost multiplier.
        Backports approach used by OS-HPXML, in which adiabatic doors are not included in the door area cost multiplier output.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, infiltration, feature
        :pullreq: 670

        **Date**: 2021-08-04

        Title:
        Update infiltration

        Description:
        Updates infiltration model pressure coefficient.
        Changes the pressure coefficient from 0.67 to 0.65 for consistency with OS-HPXML. Also updates a water heater option's flue input to be consistent with the OS-HPXML default logic.

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, windows, feature
        :pullreq: 649

        **Date**: 2021-07-27

        Title:
        Adjust interior shading assumptions

        Description:
        Reduces window interior shading during Winter to match ANSI/RESNET/ICC 301 assumption.
        Changes to winter interior shading factor = 85% instead of 70%, per ANSI/RESNET/ICC 301 Standard.

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, ceiling fan, feature
        :pullreq: 652

        **Date**: 2021-07-27

        Title:
        Update ceiling fan model

        Description:
        Updates ceiling fan model based on ANSI/RESNET ICC 301 assumptions.
        Backports the ceiling fan model from OS-HPXML, which is based on ANSI/RESNET/ICC 301.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 653

        **Date**: 2021-07-27

        Title:
        Hot water recirc pump bugfix, take 2

        Description:
        Fixes hot water distribution internal gains not being zeroed out during vacancies.
        Follow-up to #646. It turns out that the recirculation pump was correctly reflecting the vacancy status for a unit, so that code is reverting. While making the change, I noticed that the internal gains associated with the hot water distribution system were not being zeroed out for vacant units, so that is fixed here too

        Assignees: Scott Horowitz


    .. change::
        :tags: software, openstudio, feature
        :pullreq: 604

        **Date**: 2021-07-26

        Title:
        OS v3.2.1 (E+ v9.5)

        Description:
        Update to OpenStudio v3.3.0
        Updates to OpenStudio v3.2.1 (EnergyPlus v9.5).

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, windows, feature
        :pullreq: 615

        **Date**: 2021-07-21

        Title:
        Add more descriptive window options

        Description:
        Update window type distributions using RECS 2015. Includes additional of frame material types (RECS 2015) and presence of storm windows (D&R International).
        The previous limited description of windows caused a lack of variation in U-value and solar gains for windows

        resstock-estimation: `pull request 140 <https://github.com/NREL/resstock-estimation/pull/140>`_

        Assignees: Elaina Present, Anthony Fontanini, Prateek Munankarmi


    .. change::
        :tags: workflow, water heater, feature
        :pullreq: 483

        **Date**: 2021-07-19

        Title:
        Water Heater GEB

        Description:
        Introduce GEB capabilities for water heaters, including the ability to schedule setpoint and HPWH operating mode.
        Adding in new GEB related features, including:
        
        - Allowing tanks to use either a mixed or stratified tank model (additional user argument)
        - Allowing setpoint to follow an hourly (8760) schedule rather than only fixed values.
        - Allowing HPWH operating mode to be scheduled (either "HP Only" or "standard"). This allows the elements to be disabled during peak periods.
        - Adding unmet shower (an unmet load metric for WHs) calculations into ResStock runs to quantify any unmet WH loads.
        
        In addition to these GEB features, a few new HPWH options, corresponding the AO Smith's current product line, are added to options lookup as potential upgrade options.

        resstock-estimation: `pull request 150 <https://github.com/NREL/resstock-estimation/pull/150>`_

        Assignees: Jeff Maguire, Joe Robertson, Andrew Speake


    .. change::
        :tags: characteristics, windows, bugfix
        :pullreq: 597

        **Date**: 2021-07-14

        Title:
        WWR calculation for facades w/ doors

        Description:
        Fixes window-to-wall ratio calculation for facades with doors. Previously if a facade had a door, the WWR would be applied to the net wall area instead of gross wall area. Added a unit test that demonstrates the fix -- previously the front window area was 95.6 ft2, now it's 100 ft2 and matches the results from ResStock-HPXML.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, heat pumps, feature
        :pullreq: 605

        **Date**: 2021-07-13

        Title:
        HP defrost control

        Description:
        Changes heat pump defrost control from OnDemand to Timed.
        Backports NREL/OpenStudio-HPXML#403.

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 561

        **Date**: 2021-07-09

        Title:
        geometry wall type.tsv to create from Lightbox

        Description:
        Switch data source for `Geometry Wall Type.tsv` from RECS 2009 to Homeland Infrastructure Foundation-Level Data (HIFLD) Parcel data.
        replace existing geometry wall type.tsv with new tsv from Lightbox.
        add geometry wall exterior finish.tsv from Lightbox.
        update insulation wall.tsv per new wall type.
        update options lookup per new wall type and exterior finish.

        resstock-estimation: `pull request 109 <https://github.com/NREL/resstock-estimation/pull/109>`_

        Assignees: Lixi Liu


    .. change::
        :tags: workflow, cost multipliers, feature
        :pullreq: 634

        **Date**: 2021-07-08

        Title:
        Duct cost multiplier - unconditioned area

        Description:
        Changes "Duct Surface Area (ft^2)" cost multiplier to "Duct Unconditioned Surface Area (ft^2)".
        Converts "Duct Surface Area (ft^2)" cost multiplier to "Duct Unconditioned Surface Area (ft^2)". Provides consistency w/ ResStock-HPXML. Follow-up to #532.
        Only buildings where the primary duct location is living space or finished basement are affected; they now return zero (instead of non-zero) values for the cost multiplier.

        Assignees: Scott Horowitz


    .. change::
        :tags: workflow, hvac, feature
        :pullreq: 586

        **Date**: 2021-07-01

        Title:
        Replace room-ac performance curves by Cutler curves

        Description:
        Switches room air conditioner model to use Cutler performance curves.
        Backports:
        
        - Replace room-ac performance curves by Cutler curves OpenStudio-HPXML#698
        - Room air conditioner performance curve bugfix OpenStudio-HPXML#701
        - Allow CEER efficiency unit for room ac OpenStudio-HPXML#764

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 559

        **Date**: 2021-06-29

        Title:
        ResStock-HPXML: Apply tsv files to develop branch

        Description:
        Update tsv files for both the national and testing projects. Supports transition to ResStock-HPXML.

        resstock-estimation: `pull request 136 <https://github.com/NREL/resstock-estimation/pull/136>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, lighting, feature
        :pullreq: 619

        **Date**: 2021-06-21

        Title:
        Backport ERI lighting calcs from restructure-v3

        Description:
        Use ANSI/RESNET/ICC 301 equations to calculate annual interior, exterior, and garage lighting energy.
        Backports the Energy Rating Index equations used to calculate interior, exterior, and garage lighting on https://github.com/NREL/resstock/tree/restructure-v3.

        Assignees: Andrew Speake


    .. change::
        :tags: characteristics, balancing areas, bugfix
        :pullreq: 613

        **Date**: 2021-06-18

        Title:
        Rename ReEDS to REEDS

        Description:
        Fix name of ReEDS balancing areas.
        In the results.csv the ReEDS column gets interpreted as re_eds which makes the column hard to search for. Even though "ReEDS" is correct, it was decided that the TSV name will be "REEDS".

        resstock-estimation: `pull request 143 <https://github.com/NREL/resstock-estimation/pull/143>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, bathrooms, feature, bugfix
        :pullreq: 601

        **Date**: 2021-06-10

        Title:
        Number of bathrooms

        Description:
        Update number of bathrooms assumption to match the Building America House Simulation Protocols.
        This PR makes two changes:
        
        - Updates number of bathrooms to use the BAHSP equation (Nbedrooms/2 + 0.5) and fixes the values used for SFA/MF.
        - Rounds down the number of bathrooms to the nearest integer for the assumption of number of bath fans. (E.g., a 1.5 bathroom home will now have 1 bath fan instead of 1.5 bath fans.)

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 609

        **Date**: 2021-06-10

        Title:
        Update sampling_probabilty column based on bug in tsv_dist

        Description:
        Sync the sample probabilities after a bug fix in tsv_dist.
        The tsv_dist function was updated in the EULP-uncertainty-quantification PR #27. This update was due to a bug in identifying dependency intersections. As a result, the sample_probability column has updated for many housing characteristics.

        resstock-estimation: `pull request 142 <https://github.com/NREL/resstock-estimation/pull/142>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, sampling, feature
        :pullreq: 606

        **Date**: 2021-06-04

        Title:
        Sampling speed improvement

        Description:
        Speed up sampling algorithm by multiple orders of magnitude for large numbers of samples.
        Addresses a bottleneck in run_sampling.rb that occurs for large TSVs.

        Assignees: Scott Horowitz


    .. change::
        :tags: characteristics, sampling, bugfix
        :pullreq: 592

        **Date**: 2021-05-27

        Title:
        Housing Characteristic Fixes

        Description:
        Housing characteristics fixes based on more samples in testing.
        Add Geometry Attic Type.tsv.
        Ensure assumptions are consistent for 5 to 9 unit buildings and their number of units. The assumption was added that 5 to 9 unit buildings cannot be >10 stories was not transparent in Geometry Building Number Units MF.tsv, but is enforced in Geometry Stories. The sampling_probability is 0, so the option values are set to "Option=None".
        Add Geometry Attic Type as a dependency in Insulation Unfinished Attic.tsv.
        Script Roof Material Finished Roof.tsv and Roof Material Unfinished Attic.tsv.
        Add Geometry Attic Type.tsv.
        Add Geometry Attic Type as a dependency in Insulation Unfinished Attic.tsv.
        Script Roof Material Finished Roof.tsv and Roof Material Unfinished Attic.tsv.
        Add Geometry Attic Type as a dependency to Roof Material Finished Roof.tsv and Roof Material Unfinished Attic.tsv.
        Add Geometry Stories as a dependency for Geometry Building Number Units MF.tsv.
        Pier and Beam Foundations cannot have garages.
        Add HVAC Cooling Type as a dependency to HVAC Cooling Efficiency.tsv.

        resstock-estimation: `pull request 134 <https://github.com/NREL/resstock-estimation/pull/134>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, balancing areas, feature
        :pullreq: 591

        **Date**: 2021-05-21

        Title:
        ReEDS Balancing Areas

        Description:
        Add ReEDS balancing areas as a spatial field
        This PR adds a TSV for the ReEDS balancing areas. There are 134 balancing areas. The balancing areas are a county mapping provided by the ReEDS team.

        resstock-estimation: `pull request 132 <https://github.com/NREL/resstock-estimation/pull/132>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, sampling, feature
        :pullreq: 584

        **Date**: 2021-05-17

        Title:
        Enforce running sampling probability script, try 2

        Description:
        Add a sampling probability column in the housing characteristics to define the probability a given column will be sampled.
        Add in a column called the sampling_probability to each housing characteristic. The sampling_probability is the probability that a given row in the housing characteristic TSV file is sampled. This value is calculated from the product of the marginal probability of each of the dependency values being sampled for that specific row. For each housing characteristic, the sampling_probability column should sum to 1.0 and have non-negative values.

        resstock-estimation: `pull request 127 <https://github.com/NREL/resstock-estimation/pull/127>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 558

        **Date**: 2021-05-11

        Title:
        New stories options for MF buildings

        Description:
        Remove 3 story limit for multi-family buildings, and instead use RECS data to allow for buildings up to 21 stories.
        Removes the artificial cap of 3 stories for MF buildings, and instead uses RECS data to allow for up to 21 stories. Horizontal location and level tsvs were updated to account for the new dependencies. ResidentialGeometryCreateMultifamily was also updated for error checking and to set the Middle-level units at the halfway point. Dependency options in the Window Areas and Geometry Garage tsvs are updated as well.

        resstock-estimation: `pull request 100 <https://github.com/NREL/resstock-estimation/pull/100>`_, `pull request 129 <https://github.com/NREL/resstock-estimation/pull/129>`_

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 585

        **Date**: 2021-05-03

        Title:
        dst=NA somehow shifted from AZ to AR

        Description:
        Update default daylight saving start and end dates to March 12 and November 5, respectively.
        AZ counties did not have daylight saving dates set to NA (instead, some AR counties did). This corrects that.
        This PR also updates daylight saving dates from April 7 to October 26 to March 12 through November 5 (current OS-HPXML default values).

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 585

        **Date**: 2021-05-02

        Title:
        dst=NA somehow shifted from AZ to AR

        Description:
        Set AZ counties to NA daylight saving times instead of some AR counties.
        AZ counties did not have daylight saving dates set to NA (instead, some AR counties did). This corrects that.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 583

        **Date**: 2021-04-29

        Title:
        Project yml updates

        Description:
        Update example project yaml files to use buildstockbatch input schema version 0.3.
        From schema 0.2 to 0.3.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, schedules, bugfix
        :pullreq: 577

        **Date**: 2021-04-16

        Title:
        Faster stochastic schedules, second pass

        Description:
        Reduce stochastic schedule generation runtime by over 50%.
        Related to NREL/OpenStudio-HPXML#706.
        ScheduleGenerator.create:
        
        - develop: ~10 s
        - faster-schedules2: ~7 s

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, sampling, bugfix
        :pullreq: 568

        **Date**: 2021-04-14

        Title:
        Fix Heating Type = Void showing up in buildstock.csv

        Description:
        Fixes the problem that `Heating Type=Void` is showing up in buildstock samples.
        Fixes the problem that Heating Type=Void is showing up in buildstock samples.

        resstock-estimation: `pull request 123 <https://github.com/NREL/resstock-estimation/pull/123>`_

        Assignees: Lixi Liu


    .. change::
        :tags: workflow, schedules, bugfix
        :pullreq: 571

        **Date**: 2021-04-08

        Title:
        Faster stochastic schedules

        Description:
        Reduce stochastic schedule generation runtime by over 50%.
        Related to NREL/OpenStudio-HPXML#697.
        ScheduleGenerator.create:
        
        - develop: ~34 s
        - faster-schedules: ~10 s

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, schedules, feature
        :pullreq: 566

        **Date**: 2021-04-02

        Title:
        Addresses #562, use Schedule:File with plug/fuel loads

        Description:
        Use Schedule:File with well pump / vehicle plug loads, as well as gas grill / fireplace / lighting fuel loads. This enables the optional vacancy period to apply to these end uses.
        Populate well pump and vehicle plug loads, as well as grill / lighting / fireplace fuel loads, in the schedule csv. Remove weekday / weekend / monthly schedule arguments from ResidentialMiscLargeUncommonLoads measure and the options lookup. Apply vacancy to these plug/fuel loads.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, heat pumps, bugfix
        :pullreq: 564

        **Date**: 2021-03-26

        Title:
        Fix the supplimental capacity to autosize and reorder for efficiency

        Description:
        Set all mini-split heat pump supplemental capacity to autosize.
        Make sure all the HVAC Heating Efficiency; MSHP options have the ResidentialHVACMiniSplitHeatPump argument supplemental_capacity=autosize.
        Reorder MSHP options based on efficiency.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 560

        **Date**: 2021-03-25

        Title:
        Bugfix/invalid geometry garage size

        Description:
        Fixes invalid garage and living space dimension errors.
        The geometry measure is throwing an error due to garage sizes compared to the conditioned space size. We believe the error is due to the tucked garage is larger than either the depth or width of the first floor of the single-family detached unit.

        resstock-estimation: `pull request 106 <https://github.com/NREL/resstock-estimation/pull/106>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 556

        **Date**: 2021-03-16

        Title:
        Addresses #555, unfinished attic floor material layers are reversed

        Description:
        Reverses the material layers of the unfinished attic floor construction so that they are correctly ordered outside-to-inside.
        Unfinished attic floor material layers are reversed.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, envelope, bugfix
        :pullreq: 553

        **Date**: 2021-03-08

        Title:
        Bug Fix: Too many bedrooms for small units

        Description:
        Dwelling units that are 0-499 ft2 are limited to a maximum of 2 bedrooms.
        This pull request updates the number of bedrooms for small units.

        resstock-estimation: `pull request 104 <https://github.com/NREL/resstock-estimation/pull/104>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, schedules, feature
        :pullreq: 550

        **Date**: 2021-03-04

        Title:
        Apply schedule geo-temporal shifting

        Description:
        Geo-temporal shifting of the stochastic load model schedules using the American Time Use Survey.
        The appliance schedules are shifted based on geography (state), day type(weekday/weekend), and month.
        The amount of shift is defined in resources/measures/HPXMLtoOpenStudio/resources/schedules/weekday/state_and_monthly_schedule_shift.csv and resources/measures/HPXMLtoOpenStudio/resources/schedules/weekend/state_and_monthly_schedule_shift.csv files.

        resstock-estimation: `pull request 101 <https://github.com/NREL/resstock-estimation/pull/101>`_

        Assignees: Rajendra Adhikari


    .. change::
        :tags: characteristics, hvac, feature
        :pullreq: 551

        **Date**: 2021-03-02

        Title:
        Room AC Setpoint Dependency

        Description:
        Introduce different cooling setpoint distributions for window ACs.
        Adds HVAC Cooling Type dependency to Cooling Setpoint.tsv. Cooling type is not queried in RECS, and setpoints are determined the same as before, however the underlying temperature data for Room ACs is reduced by 6F to better align with the 2009 Residential Appliance Saturation Study (RASS).

        resstock-estimation: `pull request 96 <https://github.com/NREL/resstock-estimation/pull/96>`_

        Assignees: Andrew Speake, Anthony Fontanini


    .. change::
        :tags: characteristics, hvac, feature
        :pullreq: 549

        **Date**: 2021-03-02

        Title:
        Zonal Electric Heating Setpoints

        Description:
        Include electric zonal heating equipment as a dependency in heating setpoint-related tsvs.
        Adds zonal electric heating equipment as a dependency for heating setpoint-related tsvs (Heating Setpoint, Heating Setpoint Offset Period, Heating Setpoint Offset Magnitude and Heating Setpoint Has Offset). Zonal electric heating includes "Built-In Electric Units" and "Portable Electric Heaters" in RECS 2009. Additionally, all weekend daytime heating and cooling setpoint offsets are removed

        resstock-estimation: `pull request 96 <https://github.com/NREL/resstock-estimation/pull/96>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, climate zones, feature
        :pullreq: 548

        **Date**: 2021-02-18

        Title:
        Introduce CEC Climate Zones

        Description:
        Introduce a CEC Building Climate Zone tag for samples in California.
        This pull requests add the California Energy Commission (CEC) Building Climate Zones into ResStock. A given building sample is tagged with a CEC climate zone (1-16) if the building is in California. If the sample is outside of California the sample is tagged with "None".

        resstock-estimation: `pull request 99 <https://github.com/NREL/resstock-estimation/pull/99>`_

        Assignees: Anthony Fontanini, Eric Wilson


    .. change::
        :tags: characteristics, lighting, feature
        :pullreq: 545

        **Date**: 2021-02-18

        Title:
        Increase LED saturation to 2019 projected values

        Description:
        Increase LED saturation to approximately 2019 levels.
        LED saturation is one of the fastest-changing technologies. Previously, we estimated that the LED saturation was ~10% based on the 2015 U.S. Lighting Market Characterization.

        Assignees: Anthony Fontanini, Eric Wilson


    .. change::
        :tags: characteristics, setpoints, feature
        :pullreq: 541

        **Date**: 2021-02-15

        Title:
        Vacant Unit Heating Setpoints

        Description:
        Reduce vacant unit heating setpoints to 55ºF
        Assign Vacant Unit Heating Setpoints to 55F. The assumption is close to a "don't freeze the pipes" instead of using occupied setpoints.

        resstock-estimation: `pull request 96 <https://github.com/NREL/resstock-estimation/pull/96>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 439

        **Date**: 2021-02-09

        Title:
        Single-Unit Geometry

        Description:
        Model multifamily and single-family attached buildings as individual dwelling units instead of multiple units representing a building.
        Updates geometry measures and various measure resources to model MF and SFA homes as single units. The geometry measures now apply adiabatic boundary conditions to surfaces that would otherwise be shared in the current MF and SFA modeling approaches

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 543

        **Date**: 2021-02-09

        Title:
        Speed up TSV fetching

        Description:
        Fixes significant runtime bottleneck in TSV fetching in BuildExistingModel & ApplyUpgrade measures.
        A bug in the buildstock.rb get_measure_args_from_option_names() method was causing the entirety of every TSV to be processed even when the option(s) of interest had already been found. As the number and length of TSVs has grown, so has this bottleneck.

        Assignees: Scott Horowitz



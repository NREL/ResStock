================
v2.3.0 Changelog
================

.. changelog::
    :version: v2.3.0
    :released: 2020-06-24

    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 459

        **Date**: 2020-06-23

        Title:
        Rename multifamily_beta to national

        Description:
        Rename "project_multifamily_beta" to "project_national".

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, heat pumps, bugfix
        :pullreq: 454

        **Date**: 2020-06-10

        Title:
        MSHP pan heater custom meter

        Description:
        Add mini-split heat pump pan heater to custom meter for heating electricity.
        Exclude mshp pan heater from being added to the electric interior equipment meter. Instead, add it to the electric heating meter.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 452

        **Date**: 2020-06-10

        Title:
        fix bug for small window areas

        Description:
        Fix bug in assigning small window areas to surfaces.
        @whiphi92 uncovered a bug that would throw an error when the calculated window area of a facade was less than the minimum allowable window area. This fix checks for that case and applies the invalid window area to the largest available surface.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 453

        **Date**: 2020-05-21

        Title:
        Assign daylight saving dates based on County

        Description:
        Assign daylight saving start/end dates based on county and not epw region.
        Assign dst_start_date and dst_end_date based on county instead of epw location. This eliminates the possibility of simulating a building without daylight saving dates when it is near, but not within, Arizona.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, ceiling fan, bugfix
        :pullreq: 445

        **Date**: 2020-05-12

        Title:
        Update ceiling fan options

        Description:
        Update ceiling fan tsv to remove the "National Average" option, and instead sample 28% "None" and 72% "Standard Efficiency".
        Update ceiling fan options and tsvs according to: https://trello.com/c/yBmLc3OU/23-ceiling-fans.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 438

        **Date**: 2020-04-30

        Title:
        Specify key value in timeseries reporting

        Description:
        Allow a key value to be specified when outputting timeseries variables.
        Allows users to specify a key value when requesting timeseries csvs, for example:
        
        - output_variables: Surface Outside Face Incident Solar Radiation Rate per Area|Surface 2 outputs the variable for just Surface 2, instead of every surface.

        Assignees: Andrew Speake


    .. change::
        :tags: workflow, weather, bugfix
        :pullreq: 432

        **Date**: 2020-04-06

        Title:
        Weather file update

        Description:
        Remove Location Weather Filename and Location Weather Year tsvs, and update options lookup to reflect updated weather file changes; weather filenames are now required to match what is in the options lookup.
        Presently, to update the weather year files, we would need to make changes to the Location Weather Filename and Location Weather Year tsvs. While this approach is fine with two weather years i.e. TMY3 and AMY weather files presently, it creates a 'ballooning' effect when one begins to add more weather years as the location weather filename tsv will need the addition of 216 EPWs to its rows and columns for each AMY year. To resolve this issue, we:
        
        - rename all epw weather filenames such that names are consistent between all years. New location weather filename data can be found here
        - delete location weather filename and location weather year as the names are now consistent between years
        - update options lookup tsv by adding weather filename arguments to the location tsv
        - update options lookup tsv by removing 'location weather filename' and 'location weather year' arguments

        Assignees: Tobi Adekanye


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 433

        **Date**: 2020-04-02

        Title:
        ix qoi report measure to handle locations without a season

        Description:
        Fix bug in QOI reporting measure where absence of any heating/cooling/overlap seasons would cause errors.
        The QOI report measure timing section has two errors:
        
        - If there are no days with mean daily temperature above 70F (summer), the measure will fail, as the summer season does not exist. Common in climate zones 7+
        - The daily_vals object is comprised of two arrays, and the intent is to get the array length. This fixes the timing reporting in the measure.

        Assignees: Matt Dahlhausen, Joe Robertson


    .. change::
        :tags: workflow, envelope, bugfix
        :pullreq: 426

        **Date**: 2020-04-01

        Title:
        Roofing material restructure

        Description:
        Restructure unfinished attic and finished roof -related tsv files (i.e., insulation, roof material, and radiant barrier) and options.
        Previously, we had:
        
        - No "None" option for Insulation Unfinished Attic.tsv
        - Roofing Material.tsv assigned roofing_material arguments for both ResidentialConstructionsUnfinishedAttic and ResidentialConstructionsFinishedRoof
        
        The issue with the previous is that if we try to upgrade just roofing_material, measure ResidentialConstructionsFinishedRoof is applied without all measure arguments specified. By adding the building type dependency to Insulation Unfinished Attic.tsv, Insulation Finished Roof.tsv, and both Roofing Material.tsv files, we can avoid this issue.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, water heater, bugfix
        :pullreq: 375

        **Date**: 2020-03-25

        Title:
        Update Water Heater=Other Fuel to map to no water heater

        Description:
        Allow a building to be simulated with no water heater; map the "Other Fuel" option from the Water Heater tsv to no water heater.
        update cw, cd, dw, fixtures, distribution measures to skip when not finding a water heater.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, infiltration, feature
        :pullreq: 427

        **Date**: 2020-03-24

        Title:
        Update Infiltration.tsv based on the Residential Diagnostics Database.

        Description:
        Increase the diversity of the infiltration simulated. Now using the Residential Diagnostics Database for the Infiltration housing characteristic.
        The purpose of this pull request is to diversify and update the infiltration housing characteristic. Currently, infiltration is based on the regression from Chan et al. (also based on LBL ResDB). As the regression produces a single infiltration value for a given set of input parameters, the probability distributions specified in the Infiltration.tsv are binary (only 0 and 1). In reality, the distributions are more continuous.
        In this pull request, the Infiltration.tsv has been updated with data from the Residential Diagnostics Database (ResDB). The cumulative distribution functions (CDFs) for air change at 50 Pa (ACH50) have been downloaded from their website. Each CDF from the website was fit with a lognormal distribution. The fitted lognormal distribution is then used to assign probabilities into the infiltration bins in ResStock.

        resstock-estimation: `pull request 20 <https://github.com/NREL/resstock-estimation/pull/20>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, windows, bugfix
        :pullreq: 412

        **Date**: 2020-03-24

        Title:
        Add wwr variation per RBSA II data

        Description:
        Diversify window to wall ratio variation using the Residential Building Stock Assessment (RBSA) II data.
        Per comments on that PR and discussion with @mdahlhausen, there are still changes that might happen before merging.
        binned WWRs for multifamily and single family buildings from RBSA II data.
        for calculations, see WWR estimates in EULP calibration directory on sharepoint.
        Assuming '50 or more Unit' building type is midrise/highrise with default 30% WWR for all buildings.

        resstock-estimation: `pull request 21 <https://github.com/NREL/resstock-estimation/pull/21>`_

        Assignees: Andrew Parker, Anthony Fontanini


    .. change::
        :tags: characteristics, floor area, feature
        :pullreq: 425

        **Date**: 2020-03-17

        Title:
        Increase floor area diversity

        Description:
        Increase the diversity of the floor areas that are simulated. Geometry House Size has been replaced by Geometry Floor Area Bin and Geometry Floor Area. Now using AHS for specifying the floor area. Floor areas differ by non-Core Based Statistical Areas (CBSAs) Census Divisions and the top 15 largest CBSAs.
        The purpose of this pull request is to diversify the floor area values that are simulated in ResStock. There are now two floor area bins housing characteristics, Geometry Floor Area Coarse and Geometry Floor Area Fine. These two housing characteristics are replacing the Geometry House Size housing characteristic. The Geometry Floor Area Coarse characteristics is meant to be used as a dependency for other RECS queries. The small number of bins (as before in Geometry House Size) does not slice RECS into many bins and retains reasonable sample sizes for housing characteristics dependent on Geometry Floor Area Coarse (Geometry Garage, Geometry Stories, Bedrooms, and Infiltration). The Geometry Floor Area Fine are bins based on the American Housing Survey (AHS). To maintain consistency between the two characteristics the bin sizes have been updated in Geometry Floor Area Coarse. The total_ffa and unit_ffa arguments in options_lookup.tsv are obtained from Geometry Floor Area Fine bin averages from RECS 2015.

        resstock-estimation: `pull request 19 <https://github.com/NREL/resstock-estimation/pull/19>`_

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, appliances, feature
        :pullreq: 420

        **Date**: 2020-03-12

        Title:
        Major appliance sat

        Description:
        Reduce the number of appliances in multifamily units. Adding RECS building type as a dependencies to clothes washers, clothes dryers, dishwashers, refrigerators, extra refrigerators, and stand-alone freezers. Update refrigeration levels based on RECS 2009 age and shipment-weighted efficiency by year. Now using the American Housing Survey (AHS) for clothes washer and clothes dryer saturations. New geographic field, AHS Region, which uses the top 15 largest Core Based Statistical Areas (CBSAs) and Non-CBSA Census Divisions.
        The purpose of this pull request is to reduce the number of appliances in multifamily units. The current assumption is that all units have Dishwashers and Clothes Washers. However multifamily units should have a lower probability of having laundry facilities (in unit) and extra refrigerators and stand-alone freezers. As a result, building type dependency was added to these characteristics and the fraction of units without the appliances is adjusted.

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, lighting, feature
        :pullreq: 419

        **Date**: 2020-03-12

        Title:
        Update the ResidentialLightingOther schedule in the options_lookup.tsv

        Description:
        Exterior lighting schedule changed from using interior lighting sunrise/sunset algorithm to T24 2016 Residential ACM Appendix C Table 8 Exterior Lighting Hourly Multiplier for weekdays and weekends.
        The old schedules were from the T24 2016 Residential ACM, except they were using the residential MELS schedule instead of the exterior lighting schedule. This commit updates to use the properly intended exterior lighting schedule instead.
        See the T24 2016 Residential ACM and the Plug Loads and Lighting Modeling CASE report from Energy Solutions for more information.

        Assignees: Anthony Fontanini, Eric Wilson


    .. change::
        :tags: characteristics, occupants, plug loads, feature
        :pullreq: 324

        **Date**: 2020-03-05

        Title:
        Update to RECS 2015

        Description:
        Update occupant and plug loads equations based on RECS 2015 data; replace floor area with occupants as independent variable in plug loads equation; allow modeling of zero-bedroom units (e.g., studios).
        To summarize, this solves for Nbr (in terms of Nocc) for:
        
        - sinks, showers, baths
        - range, dishwasher, clothes washer, clothes dryer
        - plug loads, large uncommon loads
        - replaces plug loads equation with RECS 2015-derived

        resstock-estimation: `pull request 12 <https://github.com/NREL/resstock-estimation/pull/12>`_

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, setpoints, feature
        :pullreq: 414

        **Date**: 2020-03-05

        Title:
        Fuzzy schedules

        Description:
        Diversify the timing heating and cooling setpoint setbacks.
        Smears the Heating and Cooling offset schedules period +- 2hours around existing times.

        Assignees: Rajendra Adhikari


    .. change::
        :tags: characteristics, geospatial, feature
        :pullreq: 416

        **Date**: 2020-03-02

        Title:
        Geospatial

        Description:
        New geospatial characteristics have been added or updated. New geospatial characteristics are as follows: ASHRAE IECC Climate Zone 2004, State, County, PUMA, Census Division, Census Region, Building America Climate Zone, and ISO/RTO Region. The top level housing characteristic is now ASHRAE IECC Climate Zone 2004. Now using data from the American Community Survey Public Use Microdata Sample (ACS PUMS) for Building Type, Vintage, and Heating Fuel.
        This pull request is aimed at adding some spatial specification of ResStock samples. Currently, there are only two spatial descriptions in the housing characteristics: 1) Location (the epw weather file regions), and 2) Location Region (RECS defined Custom Regions) This pull request creates 10 housing characteristic files that help spatially define the location of a sampled housing unit.

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, hvac, feature
        :pullreq: 418

        **Date**: 2020-03-02

        Title:
        Chicago AC saturation

        Description:
        Update HVAC System Cooling tsv with air-conditioning saturations ("None", "Room AC", or "Central AC") from American Housing Survey for Custom Region 04. Efficiency probabilities remain based on RECS 2009.
        During data source comparison, it was discovered that we probably have cooling saturation too low for Chicago. AHS is probably a better source for cooling saturation that we should use going forward. In the meantime, I pulled AC type saturation from AHS (None, Room AC , Central), and adjusted the distributions for each of these within the HVAC System Cooling tsv, but still using the efficiency breakdowns from RECS. Only CR04 was adjusted for the moment (which includes Chicago), using East North Central as an approximation for CR04 (the difference is the state of Wisconsin). In the future, we should probably separate saturation from efficiency in separate TSVs so we can use AHS for saturation and RECS for efficiency.

        Assignees: Janet Reyna


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 416

        **Date**: 2020-03-02

        Title:
        Geospatial

        Description:
        Removed the "Geometry Unit Stories SF" and "Geometry Unit Stories MF" housing characteristics. Unit stories are instead represented by the "Geometry Stories" housing characteristic.
        This pull request is aimed at adding some spatial specification of ResStock samples. Currently, there are only two spatial descriptions in the housing characteristics: 1) Location (the epw weather file regions), and 2) Location Region (RECS defined Custom Regions) This pull request creates 10 housing characteristic files that help spatially define the location of a sampled housing unit.

        Assignees: Anthony Fontanini


    .. change::
        :tags: workflow, mechanics, bugfix
        :pullreq: 405

        **Date**: 2020-02-25

        Title:
        Addresses #403, remove redundant enduses

        Description:
        Exclude net site energy consumption from annual and timeseries simulation output ("total" now reflects net of pv); change `include_enduse_subcategories` argument default to "true"; report either total interior equipment OR each of its components.
        Remove all the net site columns.
        Leave total columns for both true and false.
        Total columns become net of pv.
        Change the default of include_enduse_subcategories from false to true.

        Assignees: Joe Robertson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 408

        **Date**: 2020-02-21

        Title:
        Ignore comment lines

        Description:
        Add ability to ignore comment lines with the "#" symbol.
        This pull request is an effort to make the housing characteristics more machine-readable. The created by line is causing issues when reading the files programmatically. The resolution is that we have ResStock ignore comment lines. The comment lines begin with the "#" symbol.

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, envelope, feature
        :pullreq: 395

        **Date**: 2020-02-18

        Title:
        adding in diversity to MF roof insulation.

        Description:
        Update Insulation Finished Attic tsv with more options for insulation levels.
        Improve diversity for MF roof insulation by manually copying SF roof insulation (from Insulation Unfinished Attic). In the future, script NAHB / RBSA to pull MF distribution and also improve attic / non-attic split.

        Assignees: Janet Reyna


    .. change::
        :tags: workflow, plug loads, bugfix
        :pullreq: 355

        **Date**: 2020-02-18

        Title:
        revert national average plug load schedule to RBSAM-derived schedule,…

        Description:
        Revert plug load schedule to RBSA for the National Average option, which had accidentally been changed to CA Title 24 – CASE Plug Loads and Lighting Schedule.

        Assignees: Eric Wilson


    .. change::
        :tags: workflow, mechanics, feature
        :pullreq: 402

        **Date**: 2020-02-17

        Title:
        Remove single-family detached, PAT projects

        Description:
        Remove the single-family detached project, and remove PAT from the testing and multifamily projects.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, mechanics, feature
        :pullreq: 401

        **Date**: 2020-02-17

        Title:
        Move data folder into resstock-estimation

        Description:
        Relocate the data folder, along with tsv makers, to a separate private repository.
        Folder data moved here: https://github.com/NREL/resstock-estimation.

        Assignees: Joe Robertson


    .. change::
        :tags: characteristics, lighting, feature
        :pullreq: 392

        **Date**: 2020-02-13

        Title:
        Update lighting distribution.

        Description:
        Update the single-family detached and multifamily projects with more up-to-date lighting stock distributions.
        The old lighting distribution is weighted too heavily towards incandescent bulbs. New distribution data is from 2015 in the 2015 U.S. Lighting Market Characterization study. Option= 100% Incandescent include Incandescent, HID, Halogen, and Other. Option=100% CFL include CFL and LFL. Option=100% LED include LED.

        Assignees: Anthony Fontanini


    .. change::
        :tags: characteristics, mechanics, bugfix
        :pullreq: 392

        **Date**: 2020-02-13

        Title:
        Update lighting distribution.

        Description:
        Refactor the tsv maker classes to accommodate more data sources.
        The old lighting distribution is weighted too heavily towards incandescent bulbs. New distribution data is from 2015 in the 2015 U.S. Lighting Market Characterization study. Option= 100% Incandescent include Incandescent, HID, Halogen, and Other. Option=100% CFL include CFL and LFL. Option=100% LED include LED.

        Assignees: Anthony Fontanini



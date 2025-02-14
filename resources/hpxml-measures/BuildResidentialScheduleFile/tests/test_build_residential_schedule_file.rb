# frozen_string_literal: true

require_relative '../../HPXMLtoOpenStudio/resources/minitest_helper'
require 'openstudio'
require 'openstudio/measure/ShowRunnerOutput'
require 'fileutils'
# require 'csv'
require_relative '../measure.rb'

class BuildResidentialScheduleFileTest < Minitest::Test
  def setup
    @root_path = File.absolute_path(File.join(File.dirname(__FILE__), '..', '..'))
    @sample_files_path = File.join(@root_path, 'workflow', 'sample_files')
    @tmp_hpxml_path = File.join(@sample_files_path, 'tmp.xml')
    @tmp_output_path = File.join(@sample_files_path, 'tmp_output')
    @tmp_schedule_file_path = File.join(@sample_files_path, 'tmp.csv')
    FileUtils.mkdir_p(@tmp_output_path)

    @args_hash = {}
    @args_hash['hpxml_path'] = File.absolute_path(@tmp_hpxml_path)
    @args_hash['hpxml_output_path'] = @args_hash['hpxml_path']

    @year = 2007
    @tol = 0.005
  end

  def teardown
    File.delete(@tmp_hpxml_path) if File.exist? @tmp_hpxml_path
    File.delete(@tmp_schedule_file_path) if File.exist? @tmp_schedule_file_path
    FileUtils.rm_rf(@tmp_output_path)
  end

  def test_stochastic
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=CO') })
    assert(!info_msgs.any? { |info_msg| info_msg.include?('RandomSeed') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-7.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.83') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-104.65') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    assert_in_epsilon(6689, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2086, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2086, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(534, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(213, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(134, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(151, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3016, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(5388, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1517, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(273, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(346, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(887, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
    assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
  end

  def test_stochastic_subset_of_columns
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    columns = [SchedulesFile::Columns[:CookingRange].name,
               SchedulesFile::Columns[:Dishwasher].name,
               SchedulesFile::Columns[:HotWaterDishwasher].name,
               SchedulesFile::Columns[:ClothesWasher].name,
               SchedulesFile::Columns[:HotWaterClothesWasher].name,
               SchedulesFile::Columns[:ClothesDryer].name,
               SchedulesFile::Columns[:HotWaterFixtures].name]

    @args_hash['schedules_type'] = 'stochastic'
    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    @args_hash['schedules_column_names'] = columns.join(', ')
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('ColumnNames') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    columns.each do |column|
      assert(sf.schedules.keys.include?(column))
    end
    (SchedulesFile::Columns.values.map { |c| c.name } - columns).each do |column|
      assert(!sf.schedules.keys.include?(column))
    end
  end

  def test_stochastic_subset_of_columns_invalid_name
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['schedules_type'] = 'stochastic'
    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    @args_hash['schedules_column_names'] = "foobar, #{SchedulesFile::Columns[:CookingRange].name}, foobar2"
    _hpxml, result = _test_measure(expect_fail: true)

    error_msgs = result.errors.map { |x| x.logMessage }
    assert(error_msgs.any? { |error_msg| error_msg.include?("Invalid column name specified: 'foobar'.") })
    assert(error_msgs.any? { |error_msg| error_msg.include?("Invalid column name specified: 'foobar2'.") })
  end

  def test_stochastic_location_detailed
    hpxml = _create_hpxml('base-location-detailed.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=CO') })
    assert(!info_msgs.any? { |info_msg| info_msg.include?('RandomSeed') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-6.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.77') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-104.73') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    assert_in_epsilon(6689, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1992, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1992, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(534, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(213, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(134, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(151, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3016, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(5388, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1517, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(273, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(346, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(887, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
    assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
  end

  def test_stochastic_debug
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    @args_hash['debug'] = true
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=CO') })
    assert(!info_msgs.any? { |info_msg| info_msg.include?('RandomSeed') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-7.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.83') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-104.65') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    assert_in_epsilon(6689, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2086, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2086, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(534, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(213, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(134, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(151, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3016, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(5388, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1517, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(273, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(346, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(887, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3067, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Sleeping].name, schedules: sf.tmp_schedules), @tol)
  end

  def test_random_seed
    hpxml = _create_hpxml('base-location-baltimore-md.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['schedules_random_seed'] = 1
    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=MD') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('RandomSeed=1') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-5.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.17') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-76.68') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    assert_in_epsilon(6689, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2070, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2070, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(534, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(233, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(134, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(151, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3233, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(5388, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1517, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(288, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(320, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(889, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
    assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))

    @args_hash['schedules_random_seed'] = 2
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=MD') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('RandomSeed=2') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-5.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.17') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-76.68') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    assert_in_epsilon(6072, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1753, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1753, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(356, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(174, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(101, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(166, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3276, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(5292, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1205, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(233, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(244, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1077, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
    assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
  end

  def test_10_min_timestep
    hpxml = _create_hpxml('base-simcontrol-timestep-10-mins.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=10') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=CO') })
    assert(!info_msgs.any? { |info_msg| info_msg.include?('RandomSeed') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-7.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.83') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-104.65') })

    sf = SchedulesFile.new(schedules_paths: hpxml.buildings[0].header.schedules_filepaths,
                           year: @year,
                           output_path: @tmp_schedule_file_path)

    assert_in_epsilon(6707, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2077, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(2077, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(534, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(213, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(105, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(151, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(3009, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(5393, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(1505, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(146, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(154, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
    assert_in_epsilon(397, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
    assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
  end

  def test_non_integer_number_of_occupants
    num_occupants = 3.2

    hpxml = _create_hpxml('base.xml')
    hpxml.buildings[0].building_occupancy.number_of_residents = num_occupants
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    _hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?("GeometryNumOccupants=#{Float(Integer(num_occupants))}") })
  end

  def test_zero_occupants
    num_occupants = 0.0

    hpxml = _create_hpxml('base.xml')
    hpxml.buildings[0].building_occupancy.number_of_residents = num_occupants
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    _hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(1, info_msgs.size)
    assert(info_msgs.any? { |info_msg| info_msg.include?('Number of occupants set to zero; skipping generation of stochastic schedules.') })
    assert(!File.exist?(@args_hash['output_csv_path']))
    assert_empty(hpxml.buildings[0].header.schedules_filepaths)
  end

  def test_multiple_buildings
    hpxml = _create_hpxml('base-bldgtype-mf-whole-building.xml')
    hpxml.buildings.each do |hpxml_bldg|
      hpxml_bldg.header.schedules_filepaths = nil
    end
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic.csv'))
    @args_hash['building_id'] = 'ALL'
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=CO') })
    assert(!info_msgs.any? { |info_msg| info_msg.include?('RandomSeed') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-7.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.83') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-104.65') })

    hpxml.buildings.each do |hpxml_bldg|
      sf = SchedulesFile.new(schedules_paths: hpxml_bldg.header.schedules_filepaths,
                             year: @year,
                             output_path: @tmp_schedule_file_path)

      if hpxml_bldg.building_id == 'MyBuilding'
        assert_equal(1, hpxml_bldg.header.schedules_filepaths.size)
        assert(hpxml_bldg.header.schedules_filepaths[0].include? 'occupancy-stochastic.csv')
        assert_in_epsilon(6689, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(2086, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(2086, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(534, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(213, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(134, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(151, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(3016, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(5388, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1517, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(273, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(346, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(887, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
        assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
      elsif hpxml_bldg.building_id == 'MyBuilding_2'
        assert_equal(1, hpxml_bldg.header.schedules_filepaths.size)
        assert(hpxml_bldg.header.schedules_filepaths[0].include? 'occupancy-stochastic_2.csv')
        assert_in_epsilon(6072, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1765, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1765, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(356, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(165, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(101, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(166, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(3103, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(5292, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1205, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(221, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(266, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(894, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
        assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
      elsif hpxml_bldg.building_id == 'MyBuilding_3'
        assert_equal(1, hpxml_bldg.header.schedules_filepaths.size)
        assert(hpxml_bldg.header.schedules_filepaths[0].include? 'occupancy-stochastic_3.csv')
        assert_in_epsilon(6045, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1745, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1745, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(421, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(239, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(81, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(127, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(3079, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(5314, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1162, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(224, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(209, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(970, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
        assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
      end
    end
  end

  def test_multiple_buildings_id
    hpxml = _create_hpxml('base-bldgtype-mf-whole-building.xml')
    hpxml.buildings.each do |hpxml_bldg|
      hpxml_bldg.header.schedules_filepaths = nil
    end
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)

    @args_hash['output_csv_path'] = File.absolute_path(File.join(@tmp_output_path, 'occupancy-stochastic_2.csv'))
    @args_hash['building_id'] = 'MyBuilding_2'
    hpxml, result = _test_measure()

    info_msgs = result.info.map { |x| x.logMessage }
    assert(info_msgs.any? { |info_msg| info_msg.include?('stochastic schedule') })
    assert(info_msgs.any? { |info_msg| info_msg.include?("SimYear=#{@year}") })
    assert(info_msgs.any? { |info_msg| info_msg.include?('MinutesPerStep=60') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('State=CO') })
    assert(!info_msgs.any? { |info_msg| info_msg.include?('RandomSeed') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('GeometryNumOccupants=3.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('TimeZoneUTCOffset=-7.0') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Latitude=39.83') })
    assert(info_msgs.any? { |info_msg| info_msg.include?('Longitude=-104.65') })

    hpxml.buildings.each do |hpxml_bldg|
      building_id = hpxml_bldg.building_id

      if building_id == @args_hash['building_id']
        sf = SchedulesFile.new(schedules_paths: hpxml_bldg.header.schedules_filepaths,
                               year: @year,
                               output_path: @tmp_schedule_file_path)

        assert_equal(1, hpxml_bldg.header.schedules_filepaths.size)
        assert(hpxml_bldg.header.schedules_filepaths[0].include? 'occupancy-stochastic_2.csv')
        assert_in_epsilon(6072, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Occupants].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1765, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingInterior].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1765, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:LightingGarage].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(356, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CookingRange].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(165, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:Dishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(101, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(166, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:ClothesDryer].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(3103, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:CeilingFan].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(5292, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsOther].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(1205, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:PlugLoadsTV].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(221, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterDishwasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(266, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterClothesWasher].name, schedules: sf.tmp_schedules), @tol)
        assert_in_epsilon(894, sf.annual_equivalent_full_load_hrs(col_name: SchedulesFile::Columns[:HotWaterFixtures].name, schedules: sf.tmp_schedules), @tol)
        assert(!sf.schedules.keys.include?(SchedulesFile::Columns[:Sleeping].name))
      else
        assert_empty(hpxml_bldg.header.schedules_filepaths)
      end
    end
  end

  def test_append_output
    existing_csv_path = File.join(File.dirname(__FILE__), '..', '..', 'HPXMLtoOpenStudio', 'resources', 'schedule_files', 'setpoints.csv')
    orig_cols = File.readlines(existing_csv_path)[0].strip.split(',')

    # Test w/ append_output=false
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)
    FileUtils.cp(existing_csv_path, @tmp_schedule_file_path)
    @args_hash['output_csv_path'] = @tmp_schedule_file_path
    @args_hash['append_output'] = false
    _test_measure()

    assert(File.exist?(@tmp_schedule_file_path))
    outdata = File.readlines(@tmp_schedule_file_path)
    expected_cols = ScheduleGenerator.export_columns
    assert_equal(expected_cols, outdata[0].strip.split(',')) # Header
    assert_equal(expected_cols.size, outdata[1].split(',').size) # Data

    # Test w/ append_output=true
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)
    FileUtils.cp(existing_csv_path, @tmp_schedule_file_path)
    @args_hash['output_csv_path'] = @tmp_schedule_file_path
    @args_hash['append_output'] = true
    _test_measure()

    assert(File.exist?(@tmp_schedule_file_path))
    outdata = File.readlines(@tmp_schedule_file_path)
    expected_cols = orig_cols + ScheduleGenerator.export_columns
    assert_equal(expected_cols, outdata[0].strip.split(',')) # Header
    assert_equal(expected_cols.size, outdata[1].split(',').size) # Data

    # Test w/ append_output=true and inconsistent data
    existing_csv_path = File.join(File.dirname(__FILE__), '..', '..', 'HPXMLtoOpenStudio', 'resources', 'schedule_files', 'setpoints-10-mins.csv')
    hpxml = _create_hpxml('base.xml')
    XMLHelper.write_file(hpxml.to_doc, @tmp_hpxml_path)
    FileUtils.cp(existing_csv_path, @tmp_schedule_file_path)
    @args_hash['output_csv_path'] = @tmp_schedule_file_path
    @args_hash['append_output'] = true
    _hpxml, result = _test_measure(expect_fail: true)

    error_msgs = result.errors.map { |x| x.logMessage }
    assert(error_msgs.any? { |error_msg| error_msg.include?('Invalid number of rows (52561) in file.csv. Expected 8761 rows (including the header row).') })
  end

  private

  def _test_measure(expect_fail: false)
    # create an instance of the measure
    measure = BuildResidentialScheduleFile.new

    runner = OpenStudio::Measure::OSRunner.new(OpenStudio::WorkflowJSON.new)
    model = OpenStudio::Model::Model.new

    # get arguments
    arguments = measure.arguments(model)
    argument_map = OpenStudio::Measure.convertOSArgumentVectorToMap(arguments)

    # populate argument with specified hash value if specified
    arguments.each do |arg|
      temp_arg_var = arg.clone
      if @args_hash.has_key?(arg.name)
        assert(temp_arg_var.setValue(@args_hash[arg.name]))
      end
      argument_map[arg.name] = temp_arg_var
    end

    # run the measure
    measure.run(model, runner, argument_map)
    result = runner.result

    # assert that it ran correctly
    if expect_fail
      show_output(result) unless result.value.valueName == 'Fail'
      assert_equal('Fail', result.value.valueName)
    else
      show_output(result) unless result.value.valueName == 'Success'
      assert_equal('Success', result.value.valueName)
    end

    hpxml = HPXML.new(hpxml_path: @tmp_hpxml_path)

    return hpxml, result
  end

  def _create_hpxml(hpxml_name)
    return HPXML.new(hpxml_path: File.join(@sample_files_path, hpxml_name))
  end
end

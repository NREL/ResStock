require 'csv'
require 'parallel'
require 'openstudio'
require_relative '../../../resources/buildstock'
require_relative '../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/minitest_helper'
require_relative '../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/hpxml'
require_relative '../resources/hvac_flexibility/setpoint_modifier.rb'
require_relative '../measure.rb'
require 'pathname'

class ResStockArgumentsPostHPXMLTest < Minitest::Test
  def setup
    @runner = OpenStudio::Measure::OSRunner.new(OpenStudio::WorkflowJSON.new)
    parent_path = File.expand_path('../../../../', __FILE__)
    epw_path = File.join(parent_path, 'resources/hpxml-measures/weather/USA_CO_Denver.Intl.AP.725650_TMY3.epw')
    weather = WeatherFile.new(epw_path: epw_path, runner: nil)
    @schedule_modifier_15 = HVACScheduleModifier.new(state: 'CO',
                                                     sim_year: 2024,
                                                     weather: weather,
                                                     epw_path: epw_path,
                                                     minutes_per_step: 15,
                                                     runner: @runner)

    @schedule_modifier_60 = HVACScheduleModifier.new(state: 'CO',
                                                     sim_year: 2024,
                                                     weather: weather,
                                                     epw_path: epw_path,
                                                     minutes_per_step: 60,
                                                     runner: @runner)
    @non_leap_modifier = HVACScheduleModifier.new(state: 'CO',
                                                  sim_year: 2023,
                                                  weather: weather,
                                                  epw_path: epw_path,
                                                  minutes_per_step: 15,
                                                  runner: @runner)
  end

  def test_get_peak_hour
    assert_equal(18, @schedule_modifier_15._get_peak_hour(month: 6))
    assert_equal(19, @schedule_modifier_15._get_peak_hour(month: 1))
  end

  def test_get_month
    assert_equal(2, @schedule_modifier_15._get_month(index: 31 * 24 * 4 + 28 * 24 * 4 + 1))  # First 15 minutes of Feb 29
    assert_equal(2, @schedule_modifier_60._get_month(index: 31 * 24 + 28 * 24 + 1)) # First 1 hour of Feb 29
    assert_equal(3, @non_leap_modifier._get_month(index: 31 * 24 * 4 + 28 * 24 * 4 + 1)) # First 15 minutes of March 1

    assert_equal(12, @schedule_modifier_15._get_month(index: 366 * 24 * 4 - 1))
    assert_equal(12, @non_leap_modifier._get_month(index: 365 * 24 * 4 - 1))

    assert_equal(1, @schedule_modifier_15._get_month(index: 0))
    assert_equal(1, @non_leap_modifier._get_month(index: 0))
  end

  def test_modify_setpoints
    setpoints = {
      heating_setpoint: [71] * 365 * 24 * 4,
      cooling_setpoint: [78] * 365 * 24 * 4
    }
    flexibility_inputs = FlexibilityInputs.new(
      random_shift_steps: 0,
      pre_peak_duration_steps: 4 * 4,
      peak_duration_steps: 2 * 4,
      pre_peak_offset: 3,
      peak_offset: 4
    )

    modified_setpoints_15 = @schedule_modifier_15.modify_setpoints(setpoints, flexibility_inputs)

    winter_peak = 4 * @schedule_modifier_15._get_peak_hour(month: 1)
    summer_peak = 4 * @schedule_modifier_15._get_peak_hour(month: 7)

    summer_midnight = 3 * 31 * 24 * 4 + 29 * 24 * 4 + 3 * 30 * 24 * 4 # index from Jan to Jun

    assert_equal(71, modified_setpoints_15[:heating_setpoint][0])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][0])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][winter_peak]) # peak offset
    assert_equal(71 - 4, modified_setpoints_15[:heating_setpoint][winter_peak]) # peak offset
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][winter_peak - 1]) # pre-peak offset
    assert_equal(71 + 3, modified_setpoints_15[:heating_setpoint][winter_peak - 1]) # pre-peak offset

    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][summer_midnight])
    assert_equal(78 + 4, modified_setpoints_15[:cooling_setpoint][summer_midnight + summer_peak]) # peak offset
    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight + summer_peak]) # peak offset
    assert_equal(78 - 3, modified_setpoints_15[:cooling_setpoint][summer_midnight + summer_peak - 1]) # pre-peak offset
    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight + summer_peak - 1]) # pre-peak offset

    flexibility_inputs = FlexibilityInputs.new(
      random_shift_steps: 2,
      pre_peak_duration_steps: 4 * 4,
      peak_duration_steps: 2 * 4,
      pre_peak_offset: 3,
      peak_offset: 4
    )
    modified_setpoints_15 = @schedule_modifier_15.modify_setpoints(setpoints, flexibility_inputs)
    assert_equal(71, modified_setpoints_15[:heating_setpoint][0])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][0])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][winter_peak + 2]) # peak offset
    assert_equal(71 - 4, modified_setpoints_15[:heating_setpoint][winter_peak + 2]) # peak offset
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][winter_peak + 2 - 4 * 4])  # start of pre-peak offset
    assert_equal(71 + 3, modified_setpoints_15[:heating_setpoint][winter_peak + 2 - 1])  # end of pre-peak offset

    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][summer_midnight])
    assert_equal(78 + 4, modified_setpoints_15[:cooling_setpoint][summer_midnight + summer_peak + 2]) # start of peak period
    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight + summer_peak + 2 + 2 * 4 - 1]) # end of peak period
    assert_equal(78 - 0, modified_setpoints_15[:cooling_setpoint][summer_midnight + summer_peak + 2 - 4 * 4 - 1]) # before pre-peak period
    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight + summer_peak + 2 + 2 * 4]) # after peak period

    flexibility_inputs = FlexibilityInputs.new(
      random_shift_steps: -2,
      pre_peak_duration_steps: 0,
      peak_duration_steps: 2 * 4,
      pre_peak_offset: 3, # unused since pre_peak_duration_steps is 0
      peak_offset: 2
    )
    modified_setpoints_15 = @schedule_modifier_15.modify_setpoints(setpoints, flexibility_inputs)
    assert_equal(71, modified_setpoints_15[:heating_setpoint][0])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][0])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][winter_peak - 2]) # peak offset
    assert_equal(71 - 2, modified_setpoints_15[:heating_setpoint][winter_peak - 2])  # peak offset
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][winter_peak - 2 - 1])  # end of pre-peak period
    assert_equal(71 + 0, modified_setpoints_15[:heating_setpoint][winter_peak - 2 - 1]) # end of pre-peak period

    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight])
    assert_equal(78, modified_setpoints_15[:cooling_setpoint][summer_midnight])
    assert_equal(78 + 2, modified_setpoints_15[:cooling_setpoint][summer_midnight + summer_peak - 2]) # peak offset
    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight + summer_peak - 2]) # peak offset
    assert_equal(78 - 0, modified_setpoints_15[:cooling_setpoint][summer_midnight + summer_peak - 2 - 1]) # before peak period
    assert_equal(71, modified_setpoints_15[:heating_setpoint][summer_midnight + summer_peak - 2 - 1])  # before peak period
  end
end

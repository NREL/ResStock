# frozen_string_literal: true

require_relative '../resources/minitest_helper'
require 'openstudio'
require 'openstudio/measure/ShowRunnerOutput'
require 'fileutils'
require_relative '../measure.rb'
require_relative '../resources/util.rb'

class HPXMLtoOpenStudioBatteryTest < Minitest::Test
  def sample_files_dir
    return File.join(File.dirname(__FILE__), '..', '..', 'workflow', 'sample_files')
  end

  def get_battery(model, name)
    model.getElectricLoadCenterStorageLiIonNMCBatterys.each do |b|
      next unless b.name.to_s.start_with? "#{name} "

      return b
    end
    return
  end

  def calc_nom_capacity(battery)
    return (battery.numberofCellsinSeries * battery.numberofStringsinParallel *
            battery.cellVoltageatEndofNominalZone * battery.fullyChargedCellCapacity)
  end

  def test_ev_battery_default
    args_hash = {}
    args_hash['hpxml_path'] = File.absolute_path(File.join(sample_files_dir, 'base-misc-defaults.xml'))
    model, _hpxml, hpxml_bldg = _test_measure(args_hash)

    hpxml_bldg.vehicles.each do |hpxml_ev|
      next unless hpxml_ev.id.include? 'ElectricVehicle'

      ev_battery = get_battery(model, hpxml_ev.id)
      assert_nil(ev_battery) # no defaulted schedule means no EV is generated

      elcds = model.getElectricLoadCenterDistributions
      elcds.each do |elcd|
        assert(!elcd.name.to_s.include?(hpxml_ev.id))
      end
    end
  end

  def test_ev_battery
    # EV battery w/ no schedules
    args_hash = {}
    args_hash['hpxml_path'] = File.absolute_path(File.join(sample_files_dir, 'base-battery-ev.xml'))
    model, _hpxml, hpxml_bldg = _test_measure(args_hash)

    hpxml_bldg.vehicles.each do |hpxml_ev|
      ev_battery = get_battery(model, hpxml_ev.id)
      assert_nil(ev_battery)

      elcds = model.getElectricLoadCenterDistributions
      elcds.each do |elcd|
        assert(!elcd.name.to_s.include?(hpxml_ev.id))
      end
    end
  end

  def test_ev_battery_scheduled
    args_hash = {}
    args_hash['hpxml_path'] = File.absolute_path(File.join(sample_files_dir, 'base-battery-ev-scheduled.xml'))
    model, _hpxml, hpxml_bldg = _test_measure(args_hash)

    hpxml_bldg.vehicles.each do |hpxml_ev|
      ev_battery = get_battery(model, hpxml_ev.id)
      assert_equal(HPXML::LocationGarage, ev_battery.thermalZone.get.name.get)
      assert_equal(0.9, ev_battery.radiativeFraction)
      assert_equal(0.925, ev_battery.dctoDCChargingEfficiency)
      assert_equal(HPXML::BatteryLifetimeModelNone, ev_battery.lifetimeModel)
      assert_in_epsilon(15, ev_battery.numberofCellsinSeries, 0.01)
      assert_in_epsilon(623, ev_battery.numberofStringsinParallel, 0.01)
      assert_in_epsilon(0.95, ev_battery.initialFractionalStateofCharge, 0.01)
      assert_in_epsilon(990.0, ev_battery.batteryMass, 0.01)
      assert_in_epsilon(6.59, ev_battery.batterySurfaceArea, 0.01)
      assert_in_epsilon(100000, calc_nom_capacity(ev_battery), 0.01)

      ev_elcd = nil
      model.getElectricLoadCenterDistributions.each do |elcd|
        if elcd.name.to_s.include? hpxml_ev.id
          ev_elcd = elcd
          break
        end
      end
      assert_equal('AlternatingCurrentWithStorage', ev_elcd.electricalBussType)
      assert_equal(0.15, ev_elcd.minimumStorageStateofChargeFraction)
      assert_equal(0.95, ev_elcd.maximumStorageStateofChargeFraction)
      assert_equal(7200.0, ev_elcd.designStorageControlChargePower.get)
      assert_equal(6000.0, ev_elcd.designStorageControlDischargePower.get)
      assert(!ev_elcd.demandLimitSchemePurchasedElectricDemandLimit.is_initialized)
      assert_equal('TrackChargeDischargeSchedules', ev_elcd.storageOperationScheme)
      assert(ev_elcd.storageChargePowerFractionSchedule.is_initialized)
      assert(ev_elcd.storageDischargePowerFractionSchedule.is_initialized)
      assert(ev_elcd.storageConverter.is_initialized)
    end
  end

  def test_ev_battery_home_battery
    # TO-DO: test two batteries, one EV, one home
  end

  def test_ev_battery_scheduled_default
    # TO-DO: test ev battery with schedule (so it is modeled) but with all other fields defaulted
  end

  def _test_measure(args_hash)
    # create an instance of the measure
    measure = HPXMLtoOpenStudio.new

    runner = OpenStudio::Measure::OSRunner.new(OpenStudio::WorkflowJSON.new)
    model = OpenStudio::Model::Model.new

    # get arguments
    args_hash['output_dir'] = File.dirname(__FILE__)
    arguments = measure.arguments(model)
    argument_map = OpenStudio::Measure.convertOSArgumentVectorToMap(arguments)

    # populate argument with specified hash value if specified
    arguments.each do |arg|
      temp_arg_var = arg.clone
      if args_hash.has_key?(arg.name)
        assert(temp_arg_var.setValue(args_hash[arg.name]))
      end
      argument_map[arg.name] = temp_arg_var
    end

    # run the measure
    measure.run(model, runner, argument_map)
    result = runner.result

    # show the output
    show_output(result) unless result.value.valueName == 'Success'

    # assert that it ran correctly
    assert_equal('Success', result.value.valueName)

    hpxml = HPXML.new(hpxml_path: args_hash['hpxml_path'])

    # File.delete(File.join(File.dirname(__FILE__), 'in.xml'))

    return model, hpxml, hpxml.buildings[0]
  end
end

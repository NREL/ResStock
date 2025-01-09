# frozen_string_literal: true

require 'openstudio'
require_relative '../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/minitest_helper'
require_relative '../measure.rb'

class UpgradeCostsTest < Minitest::Test
  def test_SFD_1story_FB_UA_GRG_MSHP_FuelTanklessWH
    cost_multipliers = {
      'Fixed (1)' => 1,
      'Wall Area, Above-Grade, Conditioned (ft^2)' => 196.0 + 96.0 * 2 + 429.0 + 292.0 + 525.0,
      'Wall Area, Above-Grade, Exterior (ft^2)' => 196.0 + 429.0 + 166.0 * 2 + 96.0 * 2 + 18.0 + 192.0 + 292.0 + 525.0,
      'Wall Area, Below-Grade (ft^2)' => 292.0 + 525.0 + 196.0 + 429.0 + 96.0 * 2,
      'Floor Area, Conditioned (ft^2)' => 2250.0 * 2,
      'Floor Area, Conditioned * Infiltration Reduction (ft^2 * Delta ACH50)' => (3 - 2.25) * (2250.0 * 2),
      'Floor Area, Attic (ft^2)' => 2250.0,
      'Floor Area, Attic * Insulation Increase (ft^2 * Delta R-value)' => (60.0 - 38.0) * 2250.0,
      'Floor Area, Lighting (ft^2)' => 2250.0 * 2 + 12.0 * 24.0,
      'Floor Area, Foundation (ft^2)' => 2250.0,
      'Roof Area (ft^2)' => 1338.0 + 101.0 * 2 + 1237.0 + 61.0,
      'Window Area (ft^2)' => 0.12 * (196.0 + 96.0 * 2 + 429.0 + 292.0 + 525.0 - 96.0 * 2),
      'Door Area (ft^2)' => 30.0,
      'Duct Unconditioned Surface Area (ft^2)' => 0.0, # excludes ducts in conditioned space
      'Size, Heating System Primary (kBtu/h)' => 60.0,
      'Size, Heating System Secondary (kBtu/h)' => 0.0,
      'Size, Cooling System Primary (kBtu/h)' => 60.0,
      'Size, Heat Pump Backup Primary (kBtu/h)' => 100.0, # backup
      'Size, Water Heater (gal)' => 0.0,
      'Flow Rate, Mechanical Ventilation (cfm)' => 0.0,
      'Slab Perimeter, Exposed, Conditioned (ft)' => 180.0,
      'Rim Joist Area, Above-Grade, Exterior (ft^2)' => 157.5
    }
    _test_cost_multipliers('SFD_1story_FB_UA_GRG_MSHP_FuelTanklessWH.osw', cost_multipliers)
  end

  private

  def _run_osw(model, osw)
    measures = {}

    osw_hash = JSON.parse(File.read(osw))
    measures_dir = File.join(File.dirname(__FILE__), osw_hash['measure_paths'][0])
    osw_hash['steps'].each do |step|
      measures[step['measure_dir_name']] = [step['arguments']]
    end
    runner = OpenStudio::Measure::OSRunner.new(OpenStudio::WorkflowJSON.new)

    # Apply measure
    cdir = File.expand_path('.')
    success = apply_measures(measures_dir, measures, runner, model)
    Dir.chdir(cdir) # we need this because of Dir.chdir in HPXMLtoOS

    # Report warnings/errors
    runner.result.stepWarnings.each do |s|
      puts "Warning: #{s}"
    end
    runner.result.stepErrors.each do |s|
      puts "Error: #{s}"
    end

    assert(success)
  end

  def _upgrade_osw(osw)
    upgrades = { 'ceiling_assembly_r' => 61.6,
                 'air_leakage_value' => 2.25 }

    osw_hash = JSON.parse(File.read(osw))
    osw_hash['steps'].each do |step|
      step['arguments']['hpxml_path'] = step['arguments']['hpxml_path'].gsub('tests/', 'tests/Upgrade_')
      if step['measure_dir_name'] == 'BuildResidentialHPXML'
        step['arguments'].update(upgrades)
      end
    end
    File.open(osw, 'w') { |json| json.write(JSON.pretty_generate(osw_hash)) }
  end

  def _set_additional_properties(existing_hpxml, upgraded_hpxml)
    existing_hpxml.header.extension_properties = { 'ceiling_insulation_r' => 38 }
    upgraded_hpxml.header.extension_properties = { 'ceiling_insulation_r' => 60 }
  end

  def _test_cost_multipliers(osw_file, cost_multipliers)
    require 'json'

    puts "\nTesting #{osw_file}..."
    this_dir = File.dirname(__FILE__)

    values = { 'hpxml_output' => {} }

    # Existing
    model = OpenStudio::Model::Model.new
    osw = File.absolute_path("#{this_dir}/#{osw_file}")
    _run_osw(model, osw)

    hpxml_path = File.join(this_dir, 'in.xml')
    hpxml_in = HPXML.new(hpxml_path: hpxml_path)

    existing_path = File.join(this_dir, osw_file.gsub('osw', 'xml'))
    existing_hpxml = HPXML.new(hpxml_path: existing_path)

    # Upgraded
    upgrade_osw_file = "Upgrade_#{osw_file}"
    upgrade_osw = File.absolute_path("#{this_dir}/#{upgrade_osw_file}")
    FileUtils.cp(osw, upgrade_osw)
    _upgrade_osw(upgrade_osw)
    _run_osw(model, upgrade_osw)

    upgraded_path = File.join(this_dir, upgrade_osw_file.gsub('osw', 'xml'))
    upgraded_hpxml = HPXML.new(hpxml_path: upgraded_path)

    # Set additional properties
    _set_additional_properties(existing_hpxml.buildings[0], upgraded_hpxml.buildings[0])

    # Create instance of the measures
    upgrade_costs = UpgradeCosts.new

    hpxml_in.buildings.each do |hpxml_bldg|
      # Check for correct cost multiplier values
      upgrade_costs.assign_primary_and_secondary(hpxml_bldg, cost_multipliers)
      hpxml = values['hpxml_output']
      cost_multipliers.keys.each do |cost_mult_type|
        if cost_mult_type == 'Wall Area, Above-Grade, Conditioned (ft^2)'
          hpxml['enclosure_wall_area_thermal_boundary_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Wall Area Thermal Boundary')
        elsif cost_mult_type == 'Wall Area, Above-Grade, Exterior (ft^2)'
          hpxml['enclosure_wall_area_exterior_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Wall Area Exterior')
        elsif cost_mult_type == 'Wall Area, Below-Grade (ft^2)'
          hpxml['enclosure_foundation_wall_area_exterior_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Foundation Wall Area Exterior')
        elsif cost_mult_type == 'Floor Area, Conditioned (ft^2)'
          hpxml['enclosure_floor_area_conditioned_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Floor Area Conditioned')
        elsif cost_mult_type == 'Floor Area, Lighting (ft^2)'
          hpxml['enclosure_floor_area_lighting_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Floor Area Lighting')
        elsif cost_mult_type == 'Floor Area, Foundation (ft^2)'
          hpxml['enclosure_floor_area_foundation_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Floor Area Foundation')
        elsif cost_mult_type == 'Floor Area, Attic (ft^2)'
          hpxml['enclosure_ceiling_area_thermal_boundary_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Ceiling Area Thermal Boundary')
        elsif cost_mult_type == 'Roof Area (ft^2)'
          hpxml['enclosure_roof_area_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Roof Area')
        elsif cost_mult_type == 'Window Area (ft^2)'
          hpxml['enclosure_window_area_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Window Area')
        elsif cost_mult_type == 'Door Area (ft^2)'
          hpxml['enclosure_door_area_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Door Area')
        elsif cost_mult_type == 'Duct Unconditioned Surface Area (ft^2)'
          hpxml['enclosure_duct_area_unconditioned_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Duct Area Unconditioned')
        elsif cost_mult_type == 'Rim Joist Area, Above-Grade, Exterior (ft^2)'
          hpxml['enclosure_rim_joist_area_ft_2'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Rim Joist Area')
        elsif cost_mult_type == 'Slab Perimeter, Exposed, Conditioned (ft)'
          hpxml['enclosure_slab_exposed_perimeter_thermal_boundary_ft'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Enclosure: Slab Exposed Perimeter Thermal Boundary')
        elsif cost_mult_type == 'Size, Heating System Primary (kBtu/h)'
          hpxml['primary_systems_heating_capacity_btu_h'] = 0.0
          if cost_multipliers.keys.include?('Primary Systems: Heating Capacity')
            hpxml['primary_systems_heating_capacity_btu_h'] = cost_multipliers['Primary Systems: Heating Capacity'].output
          end
        elsif cost_mult_type == 'Size, Heating System Secondary (kBtu/h)'
          hpxml['secondary_systems_heating_capacity_btu_h'] = 0.0
          if cost_multipliers.keys.include?('Secondary Systems: Heating Capacity')
            hpxml['secondary_systems_heating_capacity_btu_h'] = cost_multipliers['Secondary Systems: Heating Capacity'].output
          end
        elsif cost_mult_type == 'Size, Cooling System Primary (kBtu/h)'
          hpxml['primary_systems_cooling_capacity_btu_h'] = 0.0
          if cost_multipliers.keys.include?('Primary Systems: Cooling Capacity')
            hpxml['primary_systems_cooling_capacity_btu_h'] = cost_multipliers['Primary Systems: Cooling Capacity'].output
          end
        elsif cost_mult_type == 'Size, Heat Pump Backup Primary (kBtu/h)'
          hpxml['primary_systems_heat_pump_backup_capacity_btu_h'] = 0.0
          if cost_multipliers.keys.include?('Primary Systems: Heat Pump Backup Capacity')
            hpxml['primary_systems_heat_pump_backup_capacity_btu_h'] = cost_multipliers['Primary Systems: Heat Pump Backup Capacity'].output
          end
        elsif cost_mult_type == 'Size, Water Heater (gal)'
          hpxml['systems_water_heater_tank_volume_gal'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Systems: Water Heater Tank Volume')
        elsif cost_mult_type == 'Flow Rate, Mechanical Ventilation (cfm)'
          hpxml['systems_mechanical_ventilation_flow_rate_cfm'] = upgrade_costs.get_hpxml_output(hpxml_bldg, 'Systems: Mechanical Ventilation Flow Rate')
        end
      end

      cost_multipliers.each do |mult_type, mult_value|
        next if mult_type.include?('Systems:')

        value = upgrade_costs.get_bldg_output(mult_type, values, existing_hpxml, upgraded_hpxml)
        assert(!value.nil?)
        if mult_type.include?('ft^2') || mult_type.include?('gal')
          assert_in_epsilon(mult_value, value, 0.005)
        else
          assert_in_epsilon(mult_value, value, 0.05)
        end
      end
    end

  end
end

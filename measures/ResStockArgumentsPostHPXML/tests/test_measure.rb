# frozen_string_literal: true

require 'openstudio'
require_relative '../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/minitest_helper'
require_relative '../measure.rb'

class ResStockArgumentsPostHPXMLTest < Minitest::Test
  def test_load_flexibility_measure
    osw_file = 'SFD_1story_FB_UA_GRG_MSHP_FuelTanklessWH_upgrade.osw'
    puts "\nTesting #{File.basename(osw_file)}..."
    _test_measure(osw_file)
  end
  private

  def _run_osw(model, osw)
    measures = {}

    osw_hash = JSON.parse(File.read(osw))
    measures_dirs = osw_hash['measure_paths'].map { |path| File.join(File.dirname(__FILE__), path) }
    osw_hash['steps'].each do |step|
      measures[step['measure_dir_name']] = [step['arguments']]
    end
    runner = OpenStudio::Measure::OSRunner.new(OpenStudio::WorkflowJSON.new)

    # Apply measure
    cdir = File.expand_path('.')
    success = apply_measures(measures_dirs, measures, runner, model)
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

  def _test_measure(osw_file)
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

    # Create instance of the measures
    load_flexibility = ResStockArgumentsPostHPXML.new

    # Clean up
    File.delete(File.join(File.dirname(__FILE__), osw_file.gsub('.osw', '.xml')))
    File.delete(File.join(File.dirname(__FILE__), upgrade_osw_file))
    File.delete(File.join(File.dirname(__FILE__), upgrade_osw_file.gsub('.osw', '.xml')))
    Dir.glob(File.join(File.dirname(__FILE__), 'in.*')).each { |f| File.delete(f) }
  end
end
# frozen_string_literal: true

require 'openstudio'
require_relative '../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/minitest_helper'
require_relative '../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/hpxml'
require_relative '../measure.rb'

class ResStockArgumentsPostHPXMLTest < Minitest::Test
  def test_load_flexibility_measure
    osw_file = '../resources/load_flex_post_hpxml_upgrade.osw'
    puts "\nTesting #{File.basename(osw_file)}..."

    _test_measure(osw_file)

  end


  def _test_measure(osw_file)
    require 'json'

    this_dir = File.dirname(__FILE__)
    osw = File.absolute_path("#{this_dir}/#{osw_file}")

    measures = {}

    osw_hash = JSON.parse(File.read(osw))
    measures_dir = File.join(File.dirname(__FILE__), osw_hash['measure_paths'][0])
    puts measures_dir
    osw_hash['steps'].each do |step|
      measures[step['measure_dir_name']] = [step['arguments']]
    end

    model = OpenStudio::Model::Model.new
    runner = OpenStudio::Measure::OSRunner.new(OpenStudio::WorkflowJSON.new)

    # Apply measure
    success = apply_measures(measures_dir, measures, runner, model)

    # Report warnings/errors
    runner.result.stepWarnings.each do |s|
      puts "Warning: #{s}"
    end
    runner.result.stepErrors.each do |s|
      puts "Error: #{s}"
    end

    assert(success)
  end
end

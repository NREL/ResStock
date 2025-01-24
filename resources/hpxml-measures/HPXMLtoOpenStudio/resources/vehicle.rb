# frozen_string_literal: true

# Collection of methods for adding vehicle-related OpenStudio objects, built on the Battery class
class Vehicle
  # Adds any HPXML Vehicles to the OpenStudio model.
  # Currently only models electric vehicles.
  #
  # @param runner [OpenStudio::Measure::OSRunner] Object typically used to display warnings
  # @param model [OpenStudio::Model::Model] OpenStudio Model object
  # @param spaces [Hash] Map of HPXML locations => OpenStudio Space objects
  # @param hpxml_bldg [HPXML::Building] HPXML Building object representing an individual dwelling unit
  # @param schedules_file [SchedulesFile] SchedulesFile wrapper class instance of detailed schedule files
  # @return [nil]
  def self.apply(runner, model, spaces, hpxml_bldg, schedules_file)
    hpxml_bldg.vehicles.each do |vehicle|
      next unless vehicle.vehicle_type == HPXML::VehicleTypeBEV

      apply_electric_vehicle(runner, model, spaces, hpxml_bldg, vehicle, schedules_file)
    end
  end

  # Retrieves EV charging and discharging schedules
  #
  # @param runner [OpenStudio::Measure::OSRunner] Object typically used to display warnings
  # @param model [OpenStudio::Model::Model] OpenStudio Model object
  # @param vehicle [HPXML::Vehicle] Object that defines a single electric vehicle
  # @param schedules_file [SchedulesFile] SchedulesFile wrapper class instance of detailed schedule files
  # @return [Array<OpenStudio::Model::ScheduleRuleset or OpenStudio::Model::ScheduleFile>] The charging and discharging schedules, either as a ScheduleRuleset or as a ScheduleFile
  def self.get_ev_charging_schedules(runner, model, vehicle, schedules_file)
    charging_schedule, discharging_schedule = nil, nil
    charging_col, discharging_col = SchedulesFile::Columns[:EVBatteryCharging].name, SchedulesFile::Columns[:EVBatteryDischarging].name
    if not schedules_file.nil?
      charging_schedule = schedules_file.create_schedule_file(model, col_name: charging_col)
      discharging_schedule = schedules_file.create_schedule_file(model, col_name: discharging_col)
    end
    if charging_schedule.nil? && discharging_schedule.nil?
      charge_name, discharge_name = "#{vehicle.id} charging schedule", "#{vehicle.id} discharging schedule"
      charging_schedule = model.getScheduleRulesets.find { |s| s.name.to_s == charge_name }
      discharging_schedule = model.getScheduleRulesets.find { |s| s.name.to_s == discharge_name }
      if charging_schedule.nil? || discharging_schedule.nil?
        weekday_charge, weekday_discharge = Schedule.split_signed_charging_schedule(vehicle.ev_charging_weekday_fractions)
        weekend_charge, weekend_discharge = Schedule.split_signed_charging_schedule(vehicle.ev_charging_weekend_fractions)
        charging_schedule = MonthWeekdayWeekendSchedule.new(model, charge_name, weekday_charge, weekend_charge, vehicle.ev_charging_monthly_multipliers, EPlus::ScheduleTypeLimitsFraction, false)
        charging_schedule = charging_schedule.schedule
        discharging_schedule = MonthWeekdayWeekendSchedule.new(model, discharge_name, weekday_discharge, weekend_discharge, vehicle.ev_charging_monthly_multipliers, EPlus::ScheduleTypeLimitsFraction, false)
        discharging_schedule = discharging_schedule.schedule
      end
    else
      runner.registerWarning("Both schedule file and weekday fractions provided for '#{charging_col}' and '#{discharging_col}'; weekday fractions will be ignored.") if !vehicle.ev_charging_weekday_fractions.nil?
      runner.registerWarning("Both schedule file and weekend fractions provided for '#{charging_col}' and '#{discharging_col}'; weekend fractions will be ignored.") if !vehicle.ev_charging_weekend_fractions.nil?
      runner.registerWarning("Both schedule file and monthly multipliers provided for '#{charging_col}' and '#{discharging_col}'; monthly multipliers will be ignored.") if !vehicle.ev_charging_monthly_multipliers.nil?
    end

    return charging_schedule, discharging_schedule
  end

  # Apply an electric vehicle to the model using the battery.rb Battery class, which assigns OpenStudio ElectricLoadCenterStorageLiIonNMCBattery, ElectricLoadCenterDistribution, OtherEquipment, and EMS objects.
  # Custom adjustments for EV operation are made with an EMS object within this class and in the Battery class.
  # An EMS program models the effect of ambient temperature on the effective power output.
  # An EMS program writes a 'discharge offset' variable to omit this from aggregate home electricity outputs.
  # If no charging/discharging schedule is provided, then the electric vehicle is not modeled.
  # Bi-directional charging is not currently implemented
  #
  # @param runner [OpenStudio::Measure::OSRunner] Object typically used to display warnings
  # @param model [OpenStudio::Model::Model] OpenStudio Model object
  # @param spaces [Hash] Map of HPXML locations => OpenStudio Space objects
  # @param hpxml_bldg [HPXML::Building] HPXML Building object representing an individual dwelling unit
  # @param vehicle [HPXML::Vehicle] Object that defines a single electric vehicle
  # @param schedules_file [SchedulesFile] SchedulesFile wrapper class instance of detailed schedule files
  # @return [nil]
  def self.apply_electric_vehicle(runner, model, spaces, hpxml_bldg, vehicle, schedules_file)
    model.getElectricEquipments.sort.each do |ee|
      if ee.endUseSubcategory.start_with? Constants::ObjectTypeMiscElectricVehicleCharging
        runner.registerWarning('Electric vehicle was specified as a plug load and as a battery, vehicle charging will be modeled as a plug load.')
        return
      end
    end

    # Assign charging and vehicle space
    ev_charger = vehicle.ev_charger
    if ev_charger.nil?
      runner.registerWarning('Electric vehicle specified with no charger provided; battery will not be modeled.')
      return
    else
      ev_charger.additional_properties.space = Geometry.get_space_from_location(ev_charger.location, spaces)
      vehicle.location = ev_charger.location
      vehicle.additional_properties.space = Geometry.get_space_from_location(vehicle.ev_charger.location, spaces)
    end

    # Get schedules to calculate effective discharge power
    charging_schedule, discharging_schedule = get_ev_charging_schedules(runner, model, vehicle, schedules_file)
    if charging_schedule.nil? && discharging_schedule.nil?
      runner.registerWarning('Electric vehicle battery specified with no charging/discharging schedule provided; battery will not be modeled.')
      return
    end

    # Calculate annual driving hours
    if discharging_schedule.to_ScheduleFile.is_initialized
      dis_sch = discharging_schedule.to_ScheduleFile.get
      col = dis_sch.columnNumber - 1
      discharge_vals = dis_sch.csvFile.get.getColumnAsStringVector(col).map(&:to_f)[1..]

      # Scale based on timestep and schedule length
      timestep_hours = dis_sch.minutesperItem.get.to_f / 60.0
      driving_hrs = discharge_vals.sum * timestep_hours
      schedule_hours = discharge_vals.size * timestep_hours
      annual_driving_hours = driving_hrs / schedule_hours * UnitConversions.convert(1, 'yr', 'hr')
    elsif discharging_schedule.to_ScheduleRuleset.is_initialized
      model_year = model.yearDescription.get.assumedYear
      year_start_date = OpenStudio::Date.new(OpenStudio::MonthOfYear.new('January'), 1, model_year)
      year_end_date = OpenStudio::Date.new(OpenStudio::MonthOfYear.new('December'), 31, model_year)
      discharge_day_schs = discharging_schedule.to_ScheduleRuleset.get.getDaySchedules(year_start_date, year_end_date)
      annual_driving_hours = discharge_day_schs.sum { |day_sch| day_sch.timeSeries.values.sum }
    end

    # Check for discrepancy between inputted and calculated hours per week
    sch_hours_per_week = annual_driving_hours / UnitConversions.convert(1, 'yr', 'day') * 7
    hours_differ = sch_hours_per_week.round(1) != vehicle.hours_per_week.round(1)
    if hours_differ
      if !(vehicle.hours_per_week_isdefaulted || vehicle.ev_charging_weekday_fractions_isdefaulted || vehicle.ev_charging_weekend_fractions_isdefaulted)
        runner.registerWarning("Electric vehicle hours per week inputted (#{vehicle.hours_per_week.round(1)}) do not match the hours per week calculated from the discharging schedule (#{sch_hours_per_week.round(1)}). The inputted hours per week value will be ignored.")
      end
      vehicle.hours_per_week = sch_hours_per_week
    end

    # Calculate effective discharge power and rated power output
    # Scale the effective discharge power by 2.25 to assign the rated discharge power. This value reflects the maximum power adjustment allowed in the EMS EV discharge program at -17.8 C.
    ev_annl_energy = vehicle.energy_efficiency * vehicle.miles_per_year # kWh/year
    eff_discharge_power = UnitConversions.convert(ev_annl_energy / annual_driving_hours, 'kw', 'w') # W
    vehicle.rated_power_output = eff_discharge_power * 2.25

    # Apply vehicle battery to model
    Battery.apply_battery(runner, model, spaces, hpxml_bldg, vehicle, schedules_file)

    # Apply EMS program to adjust discharge power based on ambient temperature.
    model.getElectricLoadCenterStorageLiIonNMCBatterys.each do |elcs|
      next unless elcs.name.to_s.include? vehicle.id

      ev_elcd = nil
      model.getElectricLoadCenterDistributions.each do |elcd|
        if elcd.name.to_s.include? vehicle.id
          ev_elcd = elcd
          break
        end
      end

      eff_charge_power = ev_elcd.designStorageControlChargePower
      min_soc = ev_elcd.minimumStorageStateofChargeFraction
      discharging_schedule = ev_elcd.storageDischargePowerFractionSchedule.get
      charging_schedule = ev_elcd.storageChargePowerFractionSchedule.get

      discharge_power_act = Model.add_ems_actuator(
        name: 'battery_discharge_power_act',
        model_object: ev_elcd,
        comp_type_and_control: ['Electrical Storage', 'Power Draw Rate']
      )
      charge_power_act = Model.add_ems_actuator(
        name: 'battery_charge_power_act',
        model_object: ev_elcd,
        comp_type_and_control: ['Electrical Storage', 'Power Charge Rate']
      )

      temp_sensor = Model.add_ems_sensor(
        model,
        name: 'site_temp',
        output_var_or_meter_name: 'Site Outdoor Air Drybulb Temperature',
        key_name: 'Environment'
      )
      discharge_sch_sensor = Model.add_ems_sensor(
        model,
        name: 'discharge_sch_sensor',
        output_var_or_meter_name: 'Schedule Value',
        key_name: discharging_schedule.name.to_s
      )
      charge_sch_sensor = Model.add_ems_sensor(
        model,
        name: 'charge_sch_sensor',
        output_var_or_meter_name: 'Schedule Value',
        key_name: charging_schedule.name.to_s
      )
      soc_sensor = Model.add_ems_sensor(
        model,
        name: 'soc_sensor',
        output_var_or_meter_name: 'Electric Storage Charge Fraction',
        key_name: elcs.name.to_s
      )

      ev_discharge_program = Model.add_ems_program(
        model,
        name: 'ev_discharge_program'
      )
      ev_discharge_program.additionalProperties.setFeature('ObjectType', Constants::ObjectTypeBEVDischargeProgram)
      unmet_hr_var = OpenStudio::Model::EnergyManagementSystemOutputVariable.new(model, 'unmet_driving_hours')
      unmet_hr_var.setName('unmet_driving_hours')
      unmet_hr_var.setTypeOfDataInVariable('Summed')
      unmet_hr_var.setUpdateFrequency('SystemTimestep')
      unmet_hr_var.setEMSProgramOrSubroutineName(ev_discharge_program)
      unmet_hr_var.setUnits('hr')
      # unmet_hr_var.additionalProperties.setFeature('HPXML_ID', vehicle.id) # Used by reporting measure
      # unmet_hr_var.additionalProperties.setFeature('ObjectType', Constants::ObjectTypeUnmetDrivingHours) # Used by reporting measure

      # Power adjustment vs ambient temperature curve; derived from most recent data in Figure 9 of https://www.nrel.gov/docs/fy23osti/83916.pdf
      # This adjustment scales power demand based on ambient temeprature, and encompasses losses due to battery and space conditioning (i.e., discharging losses), as well as charging losses.
      coefs = [1.412768, -3.910397E-02, 9.408235E-04, 8.971560E-06, -7.699244E-07, 1.265614E-08]
      power_curve = ''
      coefs.each_with_index do |coef, i|
        power_curve += "+(#{coef}*(site_temp_adj^#{i}))"
      end
      power_curve = power_curve[1..]
      ev_discharge_program.addLine("  Set power_mult = #{power_curve}")
      ev_discharge_program.addLine("  Set site_temp_adj = #{temp_sensor.name}")
      ev_discharge_program.addLine("  If #{temp_sensor.name} < -17.778")
      ev_discharge_program.addLine('    Set site_temp_adj = -17.778')
      ev_discharge_program.addLine("  ElseIf #{temp_sensor.name} > 37.609")
      ev_discharge_program.addLine('    Set site_temp_adj = 37.609')
      ev_discharge_program.addLine('  EndIf')
      ev_discharge_program.addLine("  If #{discharge_sch_sensor.name} > 0.0")
      ev_discharge_program.addLine("    Set #{discharge_power_act.name} = #{eff_discharge_power} * power_mult * #{discharge_sch_sensor.name}")
      ev_discharge_program.addLine("    Set #{charge_power_act.name} = 0")
      ev_discharge_program.addLine("      If #{soc_sensor.name} <= #{min_soc}")
      ev_discharge_program.addLine("        Set #{unmet_hr_var.name} = #{discharge_sch_sensor.name}")
      ev_discharge_program.addLine('      Else')
      ev_discharge_program.addLine("        Set #{unmet_hr_var.name} = 0")
      ev_discharge_program.addLine('      EndIf')
      ev_discharge_program.addLine("  ElseIf #{charge_sch_sensor.name} > 0.0")
      ev_discharge_program.addLine("    Set #{charge_power_act.name} = #{eff_charge_power} * #{charge_sch_sensor.name}")
      ev_discharge_program.addLine("    Set #{discharge_power_act.name} = 0")
      ev_discharge_program.addLine("    Set #{unmet_hr_var.name} = 0")
      ev_discharge_program.addLine('  Else')
      ev_discharge_program.addLine("    Set #{charge_power_act.name} = 0")
      ev_discharge_program.addLine("    Set #{discharge_power_act.name} = 0")
      ev_discharge_program.addLine("    Set #{unmet_hr_var.name} = 0")
      ev_discharge_program.addLine('  EndIf')

      Model.add_ems_program_calling_manager(
        model,
        name: 'ev_discharge_pcm',
        calling_point: 'BeginTimestepBeforePredictor',
        ems_programs: [ev_discharge_program]
      )
    end
  end
end

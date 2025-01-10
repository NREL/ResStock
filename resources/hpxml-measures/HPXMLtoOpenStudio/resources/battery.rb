# frozen_string_literal: true

# Collection of methods related to batteries.
module Battery
  # Adds any HPXML Batteries to the OpenStudio model.
  #
  # @param runner [OpenStudio::Measure::OSRunner] Object typically used to display warnings
  # @param model [OpenStudio::Model::Model] OpenStudio Model object
  # @param spaces [Hash] Map of HPXML locations => OpenStudio Space objects
  # @param hpxml_bldg [HPXML::Building] HPXML Building object representing an individual dwelling unit
  # @param schedules_file [SchedulesFile] SchedulesFile wrapper class instance of detailed schedule files
  # @return [nil]
  def self.apply(runner, model, spaces, hpxml_bldg, schedules_file)
    hpxml_bldg.batteries.each do |battery|
      apply_battery(runner, model, spaces, hpxml_bldg, battery, schedules_file)
    end
  end

  # Add the HPXML Battery to the OpenStudio model.
  #
  # Apply a home battery to the model using OpenStudio ElectricLoadCenterStorageLiIonNMCBattery, ElectricLoadCenterDistribution, ElectricLoadCenterStorageConverter, OtherEquipment, and EMS objects.
  # Battery without PV specified, and no charging/discharging schedule provided; battery is assumed to operate as backup and will not be modeled.
  # The system may be shared, in which case nominal/usable capacity (kWh) and usable fraction are apportioned to the dwelling unit by total number of bedrooms served.
  # A battery may share an ElectricLoadCenterDistribution object with PV; electric buss type and storage operation scheme are therefore changed.
  # Round trip efficiency is (temporarily) applied as an EMS program b/c E+ input is not hooked up.
  #
  # @param runner [OpenStudio::Measure::OSRunner] Object typically used to display warnings
  # @param model [OpenStudio::Model::Model] OpenStudio Model object
  # @param spaces [Hash] Map of HPXML locations => OpenStudio Space objects
  # @param hpxml_bldg [HPXML::Building] HPXML Building object representing an individual dwelling unit
  # @param battery [HPXML::Battery] Object that defines a single home battery
  # @param schedules_file [SchedulesFile] SchedulesFile wrapper class instance of detailed schedule files
  # @return [nil] for unscheduled battery w/out PV; in this case battery is not modeled
  def self.apply_battery(runner, model, spaces, hpxml_bldg, battery, schedules_file)
    nbeds = hpxml_bldg.building_construction.number_of_bedrooms
    unit_multiplier = hpxml_bldg.building_construction.number_of_units
    pv_systems = hpxml_bldg.pv_systems

    charging_schedule = nil
    discharging_schedule = nil
    if not schedules_file.nil?
      charging_schedule = schedules_file.create_schedule_file(model, col_name: SchedulesFile::Columns[:BatteryCharging].name)
      discharging_schedule = schedules_file.create_schedule_file(model, col_name: SchedulesFile::Columns[:BatteryDischarging].name)
    end

    if pv_systems.empty? && charging_schedule.nil? && discharging_schedule.nil?
      runner.registerWarning('Battery without PV specified, and no charging/discharging schedule provided; battery is assumed to operate as backup and will not be modeled.')
      return
    end

    obj_name = battery.id

    space = Geometry.get_space_from_location(battery.location, spaces)

    rated_power_output = battery.rated_power_output # W
    if not battery.nominal_capacity_kwh.nil?
      if battery.usable_capacity_kwh.nil?
        fail "UsableCapacity and NominalCapacity for Battery '#{battery.id}' must be in the same units."
      end

      nominal_capacity_kwh = battery.nominal_capacity_kwh # kWh
      usable_capacity_kwh = battery.usable_capacity_kwh
      usable_fraction = usable_capacity_kwh / nominal_capacity_kwh
    else
      if battery.usable_capacity_ah.nil?
        fail "UsableCapacity and NominalCapacity for Battery '#{battery.id}' must be in the same units."
      end

      nominal_capacity_kwh = get_kWh_from_Ah(battery.nominal_capacity_ah, battery.nominal_voltage) # kWh
      usable_capacity_kwh = get_kWh_from_Ah(battery.usable_capacity_ah, battery.nominal_voltage) # kWh
      usable_fraction = battery.usable_capacity_ah / battery.nominal_capacity_ah
    end

    return if rated_power_output <= 0 || nominal_capacity_kwh <= 0 || battery.nominal_voltage <= 0

    if battery.is_shared_system
      # Apportion to single dwelling unit by # bedrooms
      fail if battery.number_of_bedrooms_served.to_f <= nbeds.to_f # EPvalidator.xml should prevent this

      nominal_capacity_kwh = nominal_capacity_kwh * nbeds.to_f / battery.number_of_bedrooms_served.to_f
      usable_capacity_kwh = usable_capacity_kwh * nbeds.to_f / battery.number_of_bedrooms_served.to_f
      rated_power_output = rated_power_output * nbeds.to_f / battery.number_of_bedrooms_served.to_f
    end

    nominal_capacity_kwh *= unit_multiplier
    usable_capacity_kwh *= unit_multiplier
    rated_power_output *= unit_multiplier

    is_outside = (battery.location == HPXML::LocationOutside)
    if not is_outside
      frac_sens = 1.0
    else # Internal gains outside unit
      frac_sens = 0.0
    end

    default_nominal_cell_voltage = 3.342 # V, EnergyPlus default
    default_cell_capacity = 3.2 # Ah, EnergyPlus default

    number_of_cells_in_series = Integer((battery.nominal_voltage / default_nominal_cell_voltage).round)
    number_of_strings_in_parallel = Integer(((nominal_capacity_kwh * 1000.0) / ((default_nominal_cell_voltage * number_of_cells_in_series) * default_cell_capacity)).round)
    battery_mass = (nominal_capacity_kwh / 10.0) * 99.0 # kg
    battery_surface_area = 0.306 * (nominal_capacity_kwh**(2.0 / 3.0)) # m^2

    # Assuming 3/4 of unusable charge is minimum SOC and 1/4 of unusable charge is maximum SOC, based on SAM defaults
    unusable_fraction = 1.0 - usable_fraction
    minimum_storage_state_of_charge_fraction = 0.75 * unusable_fraction
    maximum_storage_state_of_charge_fraction = 1.0 - 0.25 * unusable_fraction

    # disable voltage dependency unless lifetime model is requested: this prevents some scenarios where changes to SoC didn't seem to reflect charge rate due to voltage dependency and constant current
    voltage_dependence = false
    if battery.lifetime_model == HPXML::BatteryLifetimeModelKandlerSmith
      voltage_dependence = true
    end

    elcs = OpenStudio::Model::ElectricLoadCenterStorageLiIonNMCBattery.new(model, number_of_cells_in_series, number_of_strings_in_parallel, battery_mass, battery_surface_area)
    elcs.setName("#{obj_name} li ion")
    if not is_outside
      elcs.setThermalZone(space.thermalZone.get)
    end
    elcs.setRadiativeFraction(0.9 * frac_sens)
    # elcs.setLifetimeModel(battery.lifetime_model)
    elcs.setLifetimeModel(HPXML::BatteryLifetimeModelNone)
    elcs.setNumberofCellsinSeries(number_of_cells_in_series)
    elcs.setNumberofStringsinParallel(number_of_strings_in_parallel)
    elcs.setInitialFractionalStateofCharge(0.0)
    elcs.setBatteryMass(battery_mass)
    elcs.setDCtoDCChargingEfficiency(battery.round_trip_efficiency) # Note: This is currently unused in E+, so we use an EMS program below instead
    elcs.setBatterySurfaceArea(battery_surface_area)
    elcs.setDefaultNominalCellVoltage(default_nominal_cell_voltage)
    elcs.setFullyChargedCellCapacity(default_cell_capacity)
    elcs.setCellVoltageatEndofNominalZone(default_nominal_cell_voltage)
    if not voltage_dependence
      elcs.setBatteryCellInternalElectricalResistance(0.002) # 2 mOhm/cell, based on OCHRE defaults (which are based on fitting to lab results)
      # Note: if the voltage reported during charge/discharge is different, energy may not balance
      # elcs.setFullyChargedCellVoltage(default_nominal_cell_voltage)
      # elcs.setCellVoltageatEndofExponentialZone(default_nominal_cell_voltage)
    end
    elcs.setFullyChargedCellVoltage(default_nominal_cell_voltage)
    elcs.setCellVoltageatEndofExponentialZone(default_nominal_cell_voltage)

    elcds = model.getElectricLoadCenterDistributions
    elcds = elcds.select { |elcd| elcd.inverter.is_initialized } # i.e., not generators
    if elcds.empty?
      elcd = OpenStudio::Model::ElectricLoadCenterDistribution.new(model)
      elcd.setName('Battery elec load center dist')
      elcd.setElectricalBussType('AlternatingCurrentWithStorage')
    else
      elcd = elcds[0] # i.e., pv

      elcd.setElectricalBussType('DirectCurrentWithInverterACStorage')
      elcd.setStorageOperationScheme('TrackFacilityElectricDemandStoreExcessOnSite')
    end

    elcd.setMinimumStorageStateofChargeFraction(minimum_storage_state_of_charge_fraction)
    elcd.setMaximumStorageStateofChargeFraction(maximum_storage_state_of_charge_fraction)
    elcd.setElectricalStorage(elcs)
    elcd.setDesignStorageControlDischargePower(rated_power_output)
    elcd.setDesignStorageControlChargePower(rated_power_output)

    if (not charging_schedule.nil?) && (not discharging_schedule.nil?)
      elcd.setStorageOperationScheme('TrackChargeDischargeSchedules')
      elcd.setStorageChargePowerFractionSchedule(charging_schedule)
      elcd.setStorageDischargePowerFractionSchedule(discharging_schedule)

      elcsc = OpenStudio::Model::ElectricLoadCenterStorageConverter.new(model)
      elcsc.setName("#{obj_name} li ion converter")
      elcsc.setSimpleFixedEfficiency(1.0)
      elcd.setStorageConverter(elcsc)
    end

    frac_lost = 0.0
    if space.nil?
      space = model.getSpaces[0]
      frac_lost = 1.0
    end

    # Apply round trip efficiency as EMS program b/c E+ input is not hooked up.
    # Replace this when the first item in https://github.com/NREL/EnergyPlus/issues/9176 is fixed.
    charge_sensor = Model.add_ems_sensor(
      model,
      name: 'battery_charge',
      output_var_or_meter_name: 'Electric Storage Charge Energy',
      key_name: elcs.name
    )

    discharge_sensor = Model.add_ems_sensor(
      model,
      name: 'battery_discharge',
      output_var_or_meter_name: 'Electric Storage Discharge Energy',
      key_name: elcs.name
    )

    loss_adj_object = Model.add_other_equipment(
      model,
      name: Constants::ObjectTypeBatteryLossesAdjustment,
      end_use: Constants::ObjectTypeBatteryLossesAdjustment,
      space: space,
      design_level: 0.01,
      frac_radiant: 0,
      frac_latent: 0,
      frac_lost: frac_lost,
      schedule: model.alwaysOnDiscreteSchedule,
      fuel_type: HPXML::FuelTypeElectricity
    )
    loss_adj_object.additionalProperties.setFeature('ObjectType', Constants::ObjectTypeBatteryLossesAdjustment)

    battery_adj_actuator = Model.add_ems_actuator(
      name: 'battery loss adj act',
      model_object: loss_adj_object,
      comp_type_and_control: EPlus::EMSActuatorOtherEquipmentPower
    )

    battery_losses_program = Model.add_ems_program(
      model,
      name: 'battery losses'
    )
    battery_losses_program.addLine("Set charge_losses = (-1 * #{charge_sensor.name} * (1 - (#{battery.round_trip_efficiency} ^ 0.5))) / #{unit_multiplier}")
    battery_losses_program.addLine("Set discharge_losses = (-1 * #{discharge_sensor.name} * (1 - (#{battery.round_trip_efficiency} ^ 0.5))) / #{unit_multiplier}")
    battery_losses_program.addLine('Set losses = charge_losses + discharge_losses')
    battery_losses_program.addLine("Set #{battery_adj_actuator.name} = -1 * losses / ( 3600 * SystemTimeStep )")

    Model.add_ems_program_calling_manager(
      model,
      name: 'battery losses calling manager',
      calling_point: 'EndOfSystemTimestepBeforeHVACReporting',
      ems_programs: [battery_losses_program]
    )

    elcd.additionalProperties.setFeature('HPXML_ID', battery.id)
    elcs.additionalProperties.setFeature('HPXML_ID', battery.id)
    elcs.additionalProperties.setFeature('UsableCapacity_kWh', Float(usable_capacity_kwh))
  end

  # Get nominal capacity (amp-hours) from nominal capacity (kWh) and voltage (V).
  #
  # @param nominal_capacity_kwh [Double] nominal (total) capacity (kWh)
  # @param nominal_voltage [Double] nominal voltage (V)
  # @return [Double] nominal (total) capacity (Ah)
  def self.get_Ah_from_kWh(nominal_capacity_kwh, nominal_voltage)
    return nominal_capacity_kwh * 1000.0 / nominal_voltage
  end

  # Get nominal capacity (kWh) from nominal capacity (amp-hours) and voltage (V).
  #
  # @param nominal_capacity_ah [Double] nominal (total) capacity (Ah)
  # @param nominal_voltage [Double] nominal voltage (V)
  # @return [Double] nominal (total) capacity (kWh)
  def self.get_kWh_from_Ah(nominal_capacity_ah, nominal_voltage)
    return nominal_capacity_ah * nominal_voltage / 1000.0
  end
end

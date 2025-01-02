# frozen_string_literal: true

require 'csv'
require 'matrix'

# Collection of methods related to the generation of stochastic occupancy schedules.
class ScheduleGenerator
  # @param runner [OpenStudio::Measure::OSRunner] Object typically used to display warnings
  # @param state [String] State code from the HPXML file
  # @param column_names [Array<String>] list of the schedule column names to generate
  # @param random_seed [Integer] the seed for the random number generator
  # @param minutes_per_step [Integer] the simulation timestep (minutes)
  # @param steps_in_day [Integer] the number of steps in a 24-hour day
  # @param mkc_ts_per_day [Integer] Markov chain timesteps per day
  # @param mkc_ts_per_hour [Integer] Markov chain timesteps per hour
  # @param total_days_in_year [Integer] number of days in the calendar year
  # @param sim_year [Integer] the calendar year
  # @param sim_start_day [DateTime] the DateTime object corresponding to Jan 1 of the calendar year
  # @param debug [Boolean] If true, writes extra column(s) (e.g., sleeping) for informational purposes.
  # @param append_output [Boolean] If true and the output CSV file already exists, appends columns to the file rather than overwriting it. The existing output CSV file must have the same number of rows (i.e., timeseries frequency) as the new columns being appended.
  def initialize(runner:,
                 hpxml_bldg:,
                 state:,
                 column_names: nil,
                 random_seed: nil,
                 minutes_per_step:,
                 steps_in_day:,
                 mkc_ts_per_day:,
                 mkc_ts_per_hour:,
                 total_days_in_year:,
                 sim_year:,
                 sim_start_day:,
                 debug:,
                 append_output:,
                 **)
    @runner = runner
    @hpxml_bldg = hpxml_bldg
    @state = state
    @column_names = column_names
    @random_seed = random_seed
    @minutes_per_step = minutes_per_step
    @steps_in_day = steps_in_day
    @mkc_ts_per_day = mkc_ts_per_day
    @mkc_ts_per_hour = mkc_ts_per_hour
    @total_days_in_year = total_days_in_year
    @sim_year = sim_year
    @sim_start_day = sim_start_day
    @debug = debug
    @append_output = append_output
  end

  attr_accessor(:schedules)

  # Get the subset of schedule column names that the stochastic schedule generator supports.
  #
  # @return [Array<String>] list of all schedule column names whose schedules can be stochastically generated
  def self.export_columns
    return SchedulesFile::Columns.values.select { |c| c.can_be_stochastic }.map { |c| c.name }
  end

  # The top-level method for initializing the schedules hash just before calling the main stochastic schedules method.
  #
  # @param args [Hash] Map of :argument_name => value
  # @param weather [WeatherFile] Weather object containing EPW information
  # @return [Boolean] true if successful
  def create(args:,
             weather:)
    @schedules = {}

    ScheduleGenerator.export_columns.each do |col_name|
      @schedules[col_name] = Array.new(@total_days_in_year * @steps_in_day, 0.0)
    end

    if @column_names.nil?
      @column_names = SchedulesFile::Columns.values.map { |c| c.name }
    end

    invalid_columns = (@column_names - SchedulesFile::Columns.values.map { |c| c.name })
    invalid_columns.each do |invalid_column|
      @runner.registerError("Invalid column name specified: '#{invalid_column}'.")
    end
    return false unless invalid_columns.empty?

    success = create_stochastic_schedules(args: args, weather: weather)
    return false if not success

    return true
  end

  # The main method for creating stochastic schedules.
  #
  # @param args [Hash] Map of :argument_name => value
  # @param weather [WeatherFile] Weather object containing EPW information
  # @return [Boolean] true if successful
  def create_stochastic_schedules(args:,
                                  weather:)
    default_schedules_csv_data = Defaults.get_schedules_csv_data()
    schedules_csv_data = get_schedules_csv_data()

    # initialize a random number generator
    @prng = Random.new(@random_seed)
    @num_occupants = args[:geometry_num_occupants].to_i
    # pre-load the probability distribution csv files for speed
    cluster_size_prob_map = read_activity_cluster_size_probs(resources_path: args[:resources_path])
    event_duration_prob_map = read_event_duration_probs(resources_path: args[:resources_path])
    activity_duration_prob_map = read_activity_duration_prob(resources_path: args[:resources_path])
    appliance_power_dist_map = read_appliance_power_dist(resources_path: args[:resources_path])
    weekday_monthly_shift_dict = read_monthly_shift_minutes(resources_path: args[:resources_path], daytype: 'weekday')
    weekend_monthly_shift_dict = read_monthly_shift_minutes(resources_path: args[:resources_path], daytype: 'weekend')

    all_simulated_values = [] # holds the markov-chain state for each of the seven simulated states for each occupant.
    # States are: 'sleeping', 'shower', 'laundry', 'cooking', 'dishwashing', 'absent', 'nothingAtHome'
    # if geometry_num_occupants = 2, period_in_a_year = 35040,  num_of_states = 7, then
    # shape of all_simulated_values is [2, 35040, 7]
    occupancy_types_probabilities = Schedule.validate_values(Constants::OccupancyTypesProbabilities, 4, 'occupancy types probabilities')
    for _n in 1..args[:geometry_num_occupants]
      occ_type_id = weighted_random(occupancy_types_probabilities)
      init_prob_file_weekday = args[:resources_path] + "/weekday/mkv_chain_initial_prob_cluster_#{occ_type_id}.csv"
      initial_prob_weekday = CSV.read(init_prob_file_weekday)
      initial_prob_weekday = initial_prob_weekday.map { |x| x[0].to_f }
      init_prob_file_weekend = args[:resources_path] + "/weekend/mkv_chain_initial_prob_cluster_#{occ_type_id}.csv"
      initial_prob_weekend = CSV.read(init_prob_file_weekend)
      initial_prob_weekend = initial_prob_weekend.map { |x| x[0].to_f }

      transition_matrix_file_weekday = args[:resources_path] + "/weekday/mkv_chain_transition_prob_cluster_#{occ_type_id}.csv"
      transition_matrix_weekday = CSV.read(transition_matrix_file_weekday)
      transition_matrix_weekday = transition_matrix_weekday.map { |x| x.map { |y| y.to_f } }
      transition_matrix_file_weekend = args[:resources_path] + "/weekend/mkv_chain_transition_prob_cluster_#{occ_type_id}.csv"
      transition_matrix_weekend = CSV.read(transition_matrix_file_weekend)
      transition_matrix_weekend = transition_matrix_weekend.map { |x| x.map { |y| y.to_f } }

      simulated_values = []
      @total_days_in_year.times do |day|
        today = @sim_start_day + day
        day_of_week = today.wday
        if [0, 6].include?(day_of_week)
          # Weekend
          day_type = 'weekend'
          initial_prob = initial_prob_weekend
          transition_matrix = transition_matrix_weekend
        else
          # weekday
          day_type = 'weekday'
          initial_prob = initial_prob_weekday
          transition_matrix = transition_matrix_weekday
        end
        j = 0
        state_prob = initial_prob # [] shape = 1x7. probability of transitioning to each of the 7 states
        while j < @mkc_ts_per_day do
          active_state = weighted_random(state_prob) # Randomly pick the next state
          state_vector = [0] * 7 # there are 7 states
          state_vector[active_state] = 1 # Transition to the new state
          # sample the duration of the state, and skip markov-chain based state transition until the end of the duration
          activity_duration = sample_activity_duration(activity_duration_prob_map, occ_type_id, active_state, day_type, j / 4)
          for _i in 1..activity_duration
            # repeat the same activity for the duration times
            simulated_values << state_vector
            j += 1
            if j >= @mkc_ts_per_day then break end # break as soon as we have filled activities for the day
          end
          if j >= @mkc_ts_per_day then break end # break as soon as we have filled activities for the day

          transition_probs = transition_matrix[(j - 1) * 7..j * 7 - 1] # obtain the transition matrix for current timestep
          state_prob = transition_probs[active_state]
        end
      end
      # Markov-chain transition probabilities is based on ATUS data, and the starting time of day for the data is
      # 4 am. We need to shift everything forward by 16 timesteps to make it midnight-based.
      simulated_values = simulated_values.rotate(-4 * 4) # 4am shifting (4 hours  = 4 * 4 steps of 15 min intervals)
      all_simulated_values << Matrix[*simulated_values]
    end
    # shape of all_simulated_values is [2, 35040, 7] i.e. (geometry_num_occupants, period_in_a_year, number_of_states)
    plugload_other_weekday_sch = Schedule.validate_values(default_schedules_csv_data[SchedulesFile::Columns[:PlugLoadsOther].name]['WeekdayScheduleFractions'], 24, 'weekday') # Table C.3(1) of ANSI/RESNET/ICC 301-2022 Addendum C
    plugload_other_weekend_sch = Schedule.validate_values(default_schedules_csv_data[SchedulesFile::Columns[:PlugLoadsOther].name]['WeekendScheduleFractions'], 24, 'weekend') # Table C.3(1) of ANSI/RESNET/ICC 301-2022 Addendum C
    plugload_other_monthly_multiplier = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:PlugLoadsOther].name]['PlugLoadsOtherMonthlyMultipliers'], 12, 'monthly') # Figure 24 of the 2010 BAHSP
    plugload_tv_weekday_sch = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:PlugLoadsTV].name]['PlugLoadsTVWeekdayFractions'], 24, 'weekday') # American Time Use Survey
    plugload_tv_weekend_sch = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:PlugLoadsTV].name]['PlugLoadsTVWeekendFractions'], 24, 'weekend') # American Time Use Survey
    plugload_tv_monthly_multiplier = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:PlugLoadsTV].name]['PlugLoadsTVMonthlyMultipliers'], 12, 'monthly') # American Time Use Survey
    ceiling_fan_weekday_sch = Schedule.validate_values(default_schedules_csv_data[SchedulesFile::Columns[:CeilingFan].name]['WeekdayScheduleFractions'], 24, 'weekday') # Table C.3(5) of ANSI/RESNET/ICC 301-2022 Addendum C
    ceiling_fan_weekend_sch = Schedule.validate_values(default_schedules_csv_data[SchedulesFile::Columns[:CeilingFan].name]['WeekendScheduleFractions'], 24, 'weekend') # Table C.3(5) of ANSI/RESNET/ICC 301-2022 Addendum C
    ceiling_fan_monthly_multiplier = Schedule.validate_values(Defaults.get_ceiling_fan_months(weather).join(', '), 12, 'monthly') # based on monthly average outdoor temperatures per ANSI/RESNET/ICC 301

    sch = get_building_america_lighting_schedule(args[:time_zone_utc_offset], args[:latitude], args[:longitude], schedules_csv_data)
    interior_lighting_schedule = []
    num_days_in_months = Calendar.num_days_in_months(@sim_year)
    for month in 0..11
      interior_lighting_schedule << sch[month] * num_days_in_months[month]
    end
    interior_lighting_schedule = interior_lighting_schedule.flatten
    m = interior_lighting_schedule.max
    interior_lighting_schedule = interior_lighting_schedule.map { |s| s / m }

    sleep_schedule = []
    away_schedule = []
    idle_schedule = []
    ev_occupant_presence = []
    present_occupants = [] # Binary representation of the presence of accupant. Each bit represents presence of one occupant
    @ev_occupant_number = get_ev_occupant_number(all_simulated_values)

    # fill in the yearly time_step resolution schedule for plug/lighting and ceiling fan based on weekday/weekend sch
    # States are: 0='sleeping', 1='shower', 2='laundry', 3='cooking', 4='dishwashing', 5='absent', 6='nothingAtHome'
    @total_days_in_year.times do |day|
      today = @sim_start_day + day
      month = today.month
      day_of_week = today.wday
      [0, 6].include?(day_of_week) ? is_weekday = false : is_weekday = true
      @steps_in_day.times do |step|
        minute = day * 1440 + step * @minutes_per_step
        index_15 = (minute / 15).to_i
        sleep_schedule << sum_across_occupants(all_simulated_values, 0, index_15).to_f / args[:geometry_num_occupants]
        away_schedule << sum_across_occupants(all_simulated_values, 5, index_15).to_f / args[:geometry_num_occupants]
        ev_occupant_presence << (1 - all_simulated_values[@ev_occupant_number][index_15, 5])
        present_occupants << get_present_occupants(all_simulated_values, index_15)
        idle_schedule << sum_across_occupants(all_simulated_values, 6, index_15).to_f / args[:geometry_num_occupants]
        active_occupancy_percentage = 1 - (away_schedule[-1] + sleep_schedule[-1])
        @schedules[SchedulesFile::Columns[:PlugLoadsOther].name][day * @steps_in_day + step] = get_value_from_daily_sch(plugload_other_weekday_sch, plugload_other_weekend_sch, plugload_other_monthly_multiplier, month, is_weekday, minute, active_occupancy_percentage)
        @schedules[SchedulesFile::Columns[:PlugLoadsTV].name][day * @steps_in_day + step] = get_value_from_daily_sch(plugload_tv_weekday_sch, plugload_tv_weekend_sch, plugload_tv_monthly_multiplier, month, is_weekday, minute, active_occupancy_percentage)
        @schedules[SchedulesFile::Columns[:LightingInterior].name][day * @steps_in_day + step] = scale_lighting_by_occupancy(interior_lighting_schedule, minute, active_occupancy_percentage)
        @schedules[SchedulesFile::Columns[:CeilingFan].name][day * @steps_in_day + step] = get_value_from_daily_sch(ceiling_fan_weekday_sch, ceiling_fan_weekend_sch, ceiling_fan_monthly_multiplier, month, is_weekday, minute, active_occupancy_percentage)
      end
    end
    @schedules[SchedulesFile::Columns[:PlugLoadsOther].name] = normalize(@schedules[SchedulesFile::Columns[:PlugLoadsOther].name])
    @schedules[SchedulesFile::Columns[:PlugLoadsTV].name] = normalize(@schedules[SchedulesFile::Columns[:PlugLoadsTV].name])
    @schedules[SchedulesFile::Columns[:LightingInterior].name] = normalize(@schedules[SchedulesFile::Columns[:LightingInterior].name])
    @schedules[SchedulesFile::Columns[:LightingGarage].name] = @schedules[SchedulesFile::Columns[:LightingInterior].name]
    @schedules[SchedulesFile::Columns[:CeilingFan].name] = normalize(@schedules[SchedulesFile::Columns[:CeilingFan].name])

    # Generate the Sink Schedule
    # 1. Find indexes (minutes) when at least one occupant can have sink event (they aren't sleeping or absent)
    # 2. Determine number of cluster per day
    # 3. Sample flow-rate for the sink
    # 4. For each cluster
    #   a. sample for number_of_events
    #   b. Re-normalize onset probability by removing invalid indexes (invalid = where we already have sink events)
    #   b. Probabilistically determine the start of the first event based on onset probability.
    #   c. For each event in number_of_events
    #      i. Sample the duration
    #      ii. Add the time occupied by event to invalid_index
    #      ii. if more events, offset by fixed wait time and goto c
    #   d. if more cluster, go to 4.
    mins_in_year = 1440 * @total_days_in_year
    mkc_steps_in_a_year = @total_days_in_year * @mkc_ts_per_day
    sink_activity_probable_mins = [0] * mkc_steps_in_a_year # 0 indicates sink activity cannot happen at that time
    sink_activity_sch = [0] * 1440 * @total_days_in_year
    # mark minutes when at least one occupant is doing nothing at home as possible sink activity time
    # States are: 0='sleeping', 1='shower', 2='laundry', 3='cooking', 4='dishwashing', 5='absent', 6='nothingAtHome'
    mkc_steps_in_a_year.times do |step|
      all_simulated_values.size.times do |i| # across occupants
        # if at least one occupant is not sleeping and not absent from home, then sink event can occur at that time
        if not ((all_simulated_values[i][step, 0] == 1) || (all_simulated_values[i][step, 5] == 1))
          sink_activity_probable_mins[step] = 1
        end
      end
    end

    sink_duration_probs = Schedule.validate_values(Constants::SinkDurationProbability, 9, 'sink_duration_probability')
    events_per_cluster_probs = Schedule.validate_values(Constants::SinkEventsPerClusterProbs, 15, 'sink_events_per_cluster_probs')
    hourly_onset_prob = Schedule.validate_values(Constants::SinkHourlyOnsetProb, 24, 'sink_hourly_onset_prob')
    # Lookup avg_sink_clusters_per_hh from constants
    avg_sink_clusters_per_hh = Constants::SinkAvgSinkClustersPerHH
    # Adjust avg_sink_clusters_per_hh for number of occupants in household
    total_clusters = avg_sink_clusters_per_hh * (0.29 * args[:geometry_num_occupants] + 0.26) # Eq based on cluster scaling in Building America DHW Event Schedule Generator (fewer sink draw clusters for larger households)
    sink_minutes_between_event_gap = Constants::SinkMinutesBetweenEventGap
    cluster_per_day = (total_clusters / @total_days_in_year).to_i
    sink_flow_rate_mean = Constants::SinkFlowRateMean
    sink_flow_rate_std = Constants::SinkFlowRateStd
    sink_flow_rate = gaussian_rand(sink_flow_rate_mean, sink_flow_rate_std)
    @total_days_in_year.times do |day|
      for _n in 1..cluster_per_day
        todays_probable_steps = sink_activity_probable_mins[day * @mkc_ts_per_day..((day + 1) * @mkc_ts_per_day - 1)]
        todays_probablities = todays_probable_steps.map.with_index { |p, i| p * hourly_onset_prob[i / @mkc_ts_per_hour] }
        prob_sum = todays_probablities.sum(0)
        normalized_probabilities = todays_probablities.map { |p| p * 1 / prob_sum }
        cluster_start_index = weighted_random(normalized_probabilities)
        if sink_activity_probable_mins[cluster_start_index] != 0
          sink_activity_probable_mins[cluster_start_index] = 0 # mark the 15-min interval as unavailable for another sink event
        end
        num_events = weighted_random(events_per_cluster_probs) + 1
        start_min = cluster_start_index * 15
        end_min = (cluster_start_index + 1) * 15
        for _i in 1..num_events
          duration = weighted_random(sink_duration_probs) + 1
          if start_min + duration > end_min then duration = (end_min - start_min) end
          sink_activity_sch.fill(sink_flow_rate, (day * 1440) + start_min, duration)
          start_min += duration + sink_minutes_between_event_gap # Two minutes gap between sink activity
          if start_min >= end_min then break end
        end
      end
    end

    # Generate minute level schedule for shower and bath
    # 1. Identify the shower time slots from the mkc schedule. This corresponds to personal hygiene time
    # For each slot:
    # 2. Determine if the personal hygiene is to be bath/shower using bath_to_shower_ratio probability
    # 3. Sample for the shower and bath flow rate. (These will remain same throughout the year for a given building)
    #    However, the duration of each shower/bath event can be different, so, in 15-minute aggregation, the shower/bath
    #    Water consumption might appear different between different events
    # 4. If it is shower
    #   a. Determine the number of events in the shower cluster (there can be multiple showers)
    #   b. For each event, sample the shower duration
    #   c. Fill in the time period of personal hygiene using that many events of corresponding duration
    #      separated by shower_minutes_between_event_gap.
    #      TODO If there is room in the mkc personal hygiene slot, shift uniform randomly
    # 5. If it is bath
    #   a. Sample the bath duration
    #   b. Fill in the mkc personal hygiene slot with the bath duration and flow rate.
    #      TODO If there is room in the mkc personal hygiene slot, shift uniform randomly
    # 6. Repeat process 2-6 for each occupant
    shower_minutes_between_event_gap = Constants::ShowerMinutesBetweenEventGap
    shower_flow_rate_mean = Constants::ShowerFlowRateMean
    shower_flow_rate_std = Constants::ShowerFlowRateStd
    bath_ratio = Constants::BathToShowerRatio
    bath_duration_mean = Constants::BathDurationMean
    bath_duration_std = Constants::BathDurationStd
    bath_flow_rate_mean = Constants::BathFlowRateMean
    bath_flow_rate_std = Constants::BathFlowRateStd
    m = 0
    shower_activity_sch = [0] * mins_in_year
    bath_activity_sch = [0] * mins_in_year
    bath_flow_rate = gaussian_rand(bath_flow_rate_mean, bath_flow_rate_std)
    shower_flow_rate = gaussian_rand(shower_flow_rate_mean, shower_flow_rate_std)
    # States are: 'sleeping','shower','laundry','cooking', 'dishwashing', 'absent', 'nothingAtHome'
    step = 0
    while step < mkc_steps_in_a_year
      # shower_state will be equal to number of occupant taking shower/bath in the given 15-minute mkc interval
      shower_state = sum_across_occupants(all_simulated_values, 1, step)
      step_jump = 1
      for _n in 1..shower_state.to_i
        r = @prng.rand
        if r <= bath_ratio
          # fill in bath for this time
          duration = gaussian_rand(bath_duration_mean, bath_duration_std)
          int_duration = duration.ceil
          # since we are rounding duration to integer minute, we compensate by scaling flow rate
          flow_rate = bath_flow_rate * duration / int_duration
          start_min = step * 15
          m = 0
          int_duration.times do
            bath_activity_sch[start_min + m] += flow_rate
            m += 1
            if (start_min + m) >= mins_in_year then break end
          end
          step_jump = [step_jump, 1 + (m / 15)].max # jump additional step if the bath occupies multiple 15-min slots
        else
          # fill in the shower
          num_events = sample_activity_cluster_size(cluster_size_prob_map, 'shower')
          start_min = step * 15
          m = 0
          num_events.times do
            duration = sample_event_duration(event_duration_prob_map, 'shower')
            int_duration = duration.ceil
            flow_rate = shower_flow_rate * duration / int_duration
            # since we are rounding duration to integer minute, we compensate by scaling flow rate
            int_duration.times do
              shower_activity_sch[start_min + m] += flow_rate
              m += 1
              if (start_min + m) >= mins_in_year then break end
            end
            shower_minutes_between_event_gap.times do
              # skip the gap between events
              m += 1
              if (start_min + m) >= mins_in_year then break end
            end
            if start_min + m >= mins_in_year then break end
          end
          step_jump = [step_jump, 1 + (m / 15)].max
        end
      end
      step += step_jump
    end

    # Generate minute level schedule for dishwasher and clothes washer
    # 1. Identify the dishwasher/clothes washer time slots from the mkc schedule.
    # 2. Sample for the flow_rate
    # 3. Determine the number of events in the dishwasher/clothes washer cluster
    #    (it's typically composed of multiple water draw events)
    # 4. For each event, sample the event duration
    # 5. Fill in the dishwasher/clothes washer time slot using those water draw events
    dw_flow_rate_mean = Constants::HotWaterDishwasherFlowRateMean
    dw_flow_rate_std = Constants::HotWaterDishwasherFlowRateStd
    dw_minutes_between_event_gap = Constants::HotWaterDishwasherMinutesBetweenEventGap
    dw_activity_sch = [0] * mins_in_year
    m = 0
    dw_flow_rate = gaussian_rand(dw_flow_rate_mean, dw_flow_rate_std)

    # States are: 'sleeping','shower','laundry','cooking', 'dishwashing', 'absent', 'nothingAtHome'
    # Fill in dw_water draw schedule
    step = 0
    while step < mkc_steps_in_a_year
      dish_state = sum_across_occupants(all_simulated_values, 4, step, max_clip: 1)
      step_jump = 1
      if dish_state > 0
        cluster_size = sample_activity_cluster_size(cluster_size_prob_map, 'hot_water_dishwasher')
        start_minute = step * 15
        m = 0
        cluster_size.times do
          duration = sample_event_duration(event_duration_prob_map, 'hot_water_dishwasher')
          int_duration = duration.ceil
          flow_rate = dw_flow_rate * duration / int_duration
          int_duration.times do
            dw_activity_sch[start_minute + m] = flow_rate
            m += 1
            if start_minute + m >= mins_in_year then break end
          end
          if start_minute + m >= mins_in_year then break end

          dw_minutes_between_event_gap.times do
            m += 1
            if start_minute + m >= mins_in_year then break end
          end
          if start_minute + m >= mins_in_year then break end
        end
        step_jump = [step_jump, 1 + (m / 15)].max
      end
      step += step_jump
    end

    cw_flow_rate_mean = Constants::HotWaterClothesWasherFlowRateMean
    cw_flow_rate_std = Constants::HotWaterClothesWasherFlowRateStd
    cw_minutes_between_event_gap = Constants::HotWaterClothesWasherMinutesBetweenEventGap
    cw_activity_sch = [0] * mins_in_year # this is the clothes_washer water draw schedule
    cw_load_size_probability = Schedule.validate_values(Constants::HotWaterClothesWasherLoadSizeProbability, 4, 'hot_water_clothes_washer_load_size_probability')
    m = 0
    cw_flow_rate = gaussian_rand(cw_flow_rate_mean, cw_flow_rate_std)
    # States are: 'sleeping','shower','laundry','cooking', 'dishwashing', 'absent', 'nothingAtHome'
    step = 0
    # Fill in clothes washer water draw schedule based on markov-chain state 2 (laundry)
    while step < mkc_steps_in_a_year
      clothes_state = sum_across_occupants(all_simulated_values, 2, step, max_clip: 1)
      step_jump = 1
      if clothes_state > 0
        num_loads = weighted_random(cw_load_size_probability) + 1
        start_minute = step * 15
        m = 0
        num_loads.times do
          cluster_size = sample_activity_cluster_size(cluster_size_prob_map, 'hot_water_clothes_washer')
          cluster_size.times do
            duration = sample_event_duration(event_duration_prob_map, 'hot_water_clothes_washer')
            int_duration = duration.ceil
            flow_rate = cw_flow_rate * duration.to_f / int_duration
            int_duration.times do
              cw_activity_sch[start_minute + m] = flow_rate
              m += 1
              if start_minute + m >= mins_in_year then break end
            end
            if start_minute + m >= mins_in_year then break end

            cw_minutes_between_event_gap.times do
              # skip the gap between events
              m += 1
              if start_minute + m >= mins_in_year then break end
            end
            if start_minute + m >= mins_in_year then break end
          end
        end
        if start_minute + m >= mins_in_year then break end

        step_jump = [step_jump, 1 + (m / 15)].max
      end
      step += step_jump
    end

    # States are: 'sleeping', 'shower', 'laundry', 'cooking', 'dishwashing', 'absent', 'nothingAtHome'
    # Fill in dishwasher and clothes_washer power draw schedule based on markov-chain
    # This follows similar pattern as filling in water draw events, except we use different set of probability
    # distribution csv files for power level and duration of each event. And there is only one event per mkc slot.
    dw_power_sch = [0] * mins_in_year
    step = 0
    last_state = 0
    start_time = Time.new(@sim_year, 1, 1)
    hot_water_dishwasher_monthly_multiplier = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:Dishwasher].name]['HotWaterDishwasherMonthlyMultiplier'], 12, 'hot_water_dishwasher_monthly_multiplier')
    while step < mkc_steps_in_a_year
      dish_state = sum_across_occupants(all_simulated_values, 4, step, max_clip: 1)
      step_jump = 1
      if (dish_state > 0) && (last_state == 0) # last_state == 0 prevents consecutive dishwasher power without gap
        duration_15min, avg_power = sample_appliance_duration_power(appliance_power_dist_map, 'dishwasher')

        month = (start_time + step * 15 * 60).month
        duration_min = (duration_15min * 15 * hot_water_dishwasher_monthly_multiplier[month - 1]).to_i

        duration = [duration_min, mins_in_year - step * 15].min
        dw_power_sch.fill(avg_power, step * 15, duration)
        step_jump = duration_15min
      end
      last_state = dish_state
      step += step_jump
    end

    # Fill in cw and clothes dryer power schedule
    # States are: 'sleeping', 'shower', 'laundry', 'cooking', 'dishwashing', 'absent', 'nothingAtHome'
    cw_power_sch = [0] * mins_in_year
    cd_power_sch = [0] * mins_in_year
    step = 0
    last_state = 0
    start_time = Time.new(@sim_year, 1, 1)
    clothes_dryer_monthly_multiplier = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:ClothesDryer].name]['ClothesDryerMonthlyMultiplier'], 12, 'clothes_dryer_monthly_multiplier')
    hot_water_clothes_washer_monthly_multiplier = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:ClothesWasher].name]['HotWaterClothesWasherMonthlyMultiplier'], 12, 'hot_water_clothes_washer_monthly_multiplier')
    while step < mkc_steps_in_a_year
      clothes_state = sum_across_occupants(all_simulated_values, 2, step, max_clip: 1)
      step_jump = 1
      if (clothes_state > 0) && (last_state == 0) # last_state == 0 prevents consecutive washer power without gap
        cw_duration_15min, cw_avg_power = sample_appliance_duration_power(appliance_power_dist_map, 'clothes_washer')
        cd_duration_15min, cd_avg_power = sample_appliance_duration_power(appliance_power_dist_map, 'clothes_dryer')

        month = (start_time + step * 15 * 60).month
        cd_duration_min = (cd_duration_15min * 15 * clothes_dryer_monthly_multiplier[month - 1]).to_i
        cw_duration_min = (cw_duration_15min * 15 * hot_water_clothes_washer_monthly_multiplier[month - 1]).to_i

        cw_duration = [cw_duration_min, mins_in_year - step * 15].min
        cw_power_sch.fill(cw_avg_power, step * 15, cw_duration)
        cd_start_time = (step * 15 + cw_duration).to_i # clothes dryer starts immediately after washer ends\
        cd_duration = [cd_duration_min, mins_in_year - cd_start_time].min # cd_duration would be negative if cd_start_time > mins_in_year, and no filling would occur
        cd_power_sch = cd_power_sch.fill(cd_avg_power, cd_start_time, cd_duration)
        step_jump = cw_duration_15min + cd_duration_15min
      end
      last_state = clothes_state
      step += step_jump
    end

    # Fill in cooking power schedule
    # States are: 'sleeping', 'shower', 'laundry', 'cooking', 'dishwashing', 'absent', 'nothingAtHome'
    cooking_power_sch = [0] * mins_in_year
    step = 0
    last_state = 0
    start_time = Time.new(@sim_year, 1, 1)
    cooking_monthly_multiplier = Schedule.validate_values(schedules_csv_data[SchedulesFile::Columns[:CookingRange].name]['CookingMonthlyMultiplier'], 12, 'cooking_monthly_multiplier')
    while step < mkc_steps_in_a_year
      cooking_state = sum_across_occupants(all_simulated_values, 3, step, max_clip: 1)
      step_jump = 1
      if (cooking_state > 0) && (last_state == 0) # last_state == 0 prevents consecutive cooking power without gap
        duration_15min, avg_power = sample_appliance_duration_power(appliance_power_dist_map, 'cooking')
        month = (start_time + step * 15 * 60).month
        duration_min = (duration_15min * 15 * cooking_monthly_multiplier[month - 1]).to_i
        duration = [duration_min, mins_in_year - step * 15].min
        cooking_power_sch.fill(avg_power, step * 15, duration)
        step_jump = duration_15min
      end
      last_state = cooking_state
      step += step_jump
    end

    offset_range = 30

    # showers, sinks, baths

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    shower_activity_sch = shower_activity_sch.rotate(random_offset)
    shower_activity_sch = apply_monthly_offsets(array: shower_activity_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    shower_activity_sch = aggregate_array(shower_activity_sch, @minutes_per_step)
    shower_peak_flow = shower_activity_sch.max
    showers = shower_activity_sch.map { |flow| flow / shower_peak_flow }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    sink_activity_sch = sink_activity_sch.rotate(-4 * 60 + random_offset) # 4 am shifting
    sink_activity_sch = apply_monthly_offsets(array: sink_activity_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    sink_activity_sch = aggregate_array(sink_activity_sch, @minutes_per_step)
    sink_peak_flow = sink_activity_sch.max
    sinks = sink_activity_sch.map { |flow| flow / sink_peak_flow }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    bath_activity_sch = bath_activity_sch.rotate(random_offset)
    bath_activity_sch = apply_monthly_offsets(array: bath_activity_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    bath_activity_sch = aggregate_array(bath_activity_sch, @minutes_per_step)
    bath_peak_flow = bath_activity_sch.max
    baths = bath_activity_sch.map { |flow| flow / bath_peak_flow }

    # hot water dishwasher/clothes washer/fixtures, cooking range, clothes washer/dryer, dishwasher, occupants

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    dw_activity_sch = dw_activity_sch.rotate(random_offset)
    dw_activity_sch = apply_monthly_offsets(array: dw_activity_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    dw_activity_sch = aggregate_array(dw_activity_sch, @minutes_per_step)
    dw_peak_flow = dw_activity_sch.max
    @schedules[SchedulesFile::Columns[:HotWaterDishwasher].name] = dw_activity_sch.map { |flow| flow / dw_peak_flow }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    cw_activity_sch = cw_activity_sch.rotate(random_offset)
    cw_activity_sch = apply_monthly_offsets(array: cw_activity_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    cw_activity_sch = aggregate_array(cw_activity_sch, @minutes_per_step)
    cw_peak_flow = cw_activity_sch.max
    @schedules[SchedulesFile::Columns[:HotWaterClothesWasher].name] = cw_activity_sch.map { |flow| flow / cw_peak_flow }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    cooking_power_sch = cooking_power_sch.rotate(random_offset)
    cooking_power_sch = apply_monthly_offsets(array: cooking_power_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    cooking_power_sch = aggregate_array(cooking_power_sch, @minutes_per_step)
    cooking_peak_power = cooking_power_sch.max
    @schedules[SchedulesFile::Columns[:CookingRange].name] = cooking_power_sch.map { |power| power / cooking_peak_power }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    cw_power_sch = cw_power_sch.rotate(random_offset)
    cw_power_sch = apply_monthly_offsets(array: cw_power_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    cw_power_sch = aggregate_array(cw_power_sch, @minutes_per_step)
    cw_peak_power = cw_power_sch.max
    @schedules[SchedulesFile::Columns[:ClothesWasher].name] = cw_power_sch.map { |power| power / cw_peak_power }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    cd_power_sch = cd_power_sch.rotate(random_offset)
    cd_power_sch = apply_monthly_offsets(array: cd_power_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    cd_power_sch = aggregate_array(cd_power_sch, @minutes_per_step)
    cd_peak_power = cd_power_sch.max
    @schedules[SchedulesFile::Columns[:ClothesDryer].name] = cd_power_sch.map { |power| power / cd_peak_power }

    random_offset = (@prng.rand * 2 * offset_range).to_i - offset_range
    dw_power_sch = dw_power_sch.rotate(random_offset)
    dw_power_sch = apply_monthly_offsets(array: dw_power_sch, weekday_monthly_shift_dict: weekday_monthly_shift_dict, weekend_monthly_shift_dict: weekend_monthly_shift_dict)
    dw_power_sch = aggregate_array(dw_power_sch, @minutes_per_step)
    dw_peak_power = dw_power_sch.max
    @schedules[SchedulesFile::Columns[:Dishwasher].name] = dw_power_sch.map { |power| power / dw_peak_power }

    @schedules[SchedulesFile::Columns[:Occupants].name] = away_schedule.map { |i| 1.0 - i }
    @schedules[SchedulesFile::Columns[:EVOccupant].name] = ev_occupant_presence
    @schedules[SchedulesFile::Columns[:PresentOccupants].name] = present_occupants

    if @debug
      @schedules[SchedulesFile::Columns[:Sleeping].name] = sleep_schedule
    end

    @schedules[SchedulesFile::Columns[:HotWaterFixtures].name] = [showers, sinks, baths].transpose.map { |flow| flow.sum }
    fixtures_peak_flow = @schedules[SchedulesFile::Columns[:HotWaterFixtures].name].max
    @schedules[SchedulesFile::Columns[:HotWaterFixtures].name] = @schedules[SchedulesFile::Columns[:HotWaterFixtures].name].map { |flow| flow / fixtures_peak_flow }
    fill_ev_battery_schedule(all_simulated_values)
    return true
  end

  # Aggregate array values by summing groups of elements.
  #
  # @param array [Array] Array of values to aggregate
  # @param group_size [Integer] Number of consecutive elements to sum together
  # @return [Array] New array with values aggregated by group_size
  def aggregate_array(array, group_size)
    new_array_size = array.size / group_size
    new_array = [0] * new_array_size
    new_array_size.times do |j|
      new_array[j] = array[(j * group_size)..(j + 1) * group_size - 1].sum(0)
    end
    return new_array
  end

  # Apply monthly schedule shifts based on weekday/weekend patterns.
  #
  # @param array [Array] Array of minute-level schedule values to shift
  # @param weekday_monthly_shift_dict [Hash] Map of month name to number of minutes to shift weekday schedules
  # @param weekend_monthly_shift_dict [Hash] Map of month name to number of minutes to shift weekend schedules
  # @return [Array] New array with values shifted according to monthly patterns
  def apply_monthly_offsets(array:, weekday_monthly_shift_dict:, weekend_monthly_shift_dict:)
    month_strs = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    new_array = []
    @total_days_in_year.times do |day|
      today = @sim_start_day + day
      day_of_week = today.wday
      month = month_strs[today.month - 1]
      if [0, 6].include?(day_of_week)
        # Weekend
        lead = weekend_monthly_shift_dict[month]
      else
        # weekday
        lead = weekday_monthly_shift_dict[month]
      end
      if lead.nil?
        raise "Could not find the entry for month #{month}, day #{day_of_week} and state #{@state}"
      end

      new_array.concat(array[day * 1440, 1440].rotate(lead))
    end
    return new_array
  end

  # Read monthly schedule shift minutes from CSV file for a given state and day type.
  #
  # @param resources_path [String] Path to directory containing schedule shift CSV files
  # @param daytype [String] Type of day ('weekday' or 'weekend') to get shifts for
  # @return [Hash] Map of month name to number of minutes to shift schedules
  def read_monthly_shift_minutes(resources_path:, daytype:)
    shift_file = resources_path + "/#{daytype}/state_and_monthly_schedule_shift.csv"
    shifts = CSV.read(shift_file)
    state_index = shifts[0].find_index('State')
    lead_index = shifts[0].find_index('Lead')
    month_index = shifts[0].find_index('Month')
    state_shifts = shifts.select { |row| row[state_index] == @state }
    monthly_shifts_dict = Hash[state_shifts.map { |row| [row[month_index], row[lead_index].to_i] }]
    return monthly_shifts_dict
  end

  # Read appliance power distribution data from CSV files.
  #
  # @param resources_path [String] Path to directory containing appliance power distribution CSV files
  # @return [Hash] Map of appliance name to array containing duration and consumption distributions
  def read_appliance_power_dist(resources_path:)
    activity_names = ['clothes_washer', 'dishwasher', 'clothes_dryer', 'cooking']
    power_dist_map = {}
    activity_names.each do |activity|
      duration_file = resources_path + "/#{activity}_duration_dist.csv"
      consumption_file = resources_path + "/#{activity}_consumption_dist.csv"
      duration_vals = CSV.read(duration_file)
      consumption_vals = CSV.read(consumption_file)
      duration_vals = duration_vals.map { |a| a.map { |i| i.to_i } }
      consumption_vals = consumption_vals.map { |a| a[0].to_f }
      power_dist_map[activity] = [duration_vals, consumption_vals]
    end
    return power_dist_map
  end

  # Sample the duration and power consumption for an appliance event.
  #
  # @param power_dist_map [Hash] Map of appliance name to array containing duration and consumption distributions
  # @param appliance_name [String] Name of the appliance to sample duration and power for
  # @return [Array<Integer, Float>] Array containing [duration in 15-min intervals, average power in watts]
  def sample_appliance_duration_power(power_dist_map, appliance_name)
    # returns number number of 15-min interval the appliance runs, and the average 15-min power
    duration_vals, consumption_vals = power_dist_map[appliance_name]
    if @consumption_row.nil?
      # initialize and pick the consumption and duration row only the first time
      # checking only consumption_row is sufficient because duration_row always go side by side with consumption row
      @consumption_row = {}
      @duration_row = {}
    end
    if !@consumption_row.has_key?(appliance_name)
      @consumption_row[appliance_name] = (@prng.rand * consumption_vals.size).to_i
      @duration_row[appliance_name] = (@prng.rand * duration_vals.size).to_i
    end
    power = consumption_vals[@consumption_row[appliance_name]]
    sample = @prng.rand(0..(duration_vals[@duration_row[appliance_name]].length - 1))
    duration = duration_vals[@duration_row[appliance_name]][sample]
    return [duration, power]
  end

  # Read activity cluster size probability distributions from CSV files.
  #
  # @param resources_path [String] Path to directory containing activity cluster size probability CSV files
  # @return [Hash] Map of activity name to array containing cluster size probabilities
  def read_activity_cluster_size_probs(resources_path:)
    activity_names = ['hot_water_clothes_washer', 'hot_water_dishwasher', 'shower']
    cluster_size_prob_map = {}
    activity_names.each do |activity|
      cluster_size_file = resources_path + "/#{activity}_cluster_size_probability.csv"
      cluster_size_probabilities = CSV.read(cluster_size_file)
      cluster_size_probabilities = cluster_size_probabilities.map { |entry| entry[0].to_f }
      cluster_size_prob_map[activity] = cluster_size_probabilities
    end
    return cluster_size_prob_map
  end

  # Read event duration probability distributions from CSV files.
  #
  # @param resources_path [String] Path to directory containing event duration probability CSV files
  # @return [Hash] Map of activity name to array containing durations and probabilities
  def read_event_duration_probs(resources_path:)
    activity_names = ['hot_water_clothes_washer', 'hot_water_dishwasher', 'shower']
    event_duration_probabilites_map = {}
    activity_names.each do |activity|
      duration_file = resources_path + "/#{activity}_event_duration_probability.csv"
      duration_probabilities = CSV.read(duration_file)
      durations = duration_probabilities.map { |entry| entry[0].to_f / 60 } # convert to minute
      probabilities = duration_probabilities.map { |entry| entry[1].to_f }
      event_duration_probabilites_map[activity] = [durations, probabilities]
    end
    return event_duration_probabilites_map
  end

  # Read activity duration probability distributions from CSV files.
  #
  # @param resources_path [String] Path to directory containing activity duration probability CSV files
  # @return [Hash] Map of activity name to array containing durations and probabilities
  def read_activity_duration_prob(resources_path:)
    cluster_types = ['0', '1', '2', '3']
    day_types = ['weekday', 'weekend']
    time_of_days = ['morning', 'midday', 'evening']
    activity_names = ['shower', 'cooking', 'dishwashing', 'laundry']
    activity_duration_prob_map = {}
    cluster_types.each do |cluster_type|
      day_types.each do |day_type|
        time_of_days.each do |time_of_day|
          activity_names.each do |activity_name|
            duration_file = resources_path + "/#{day_type}/duration_probability/cluster_#{cluster_type}_#{activity_name}_#{time_of_day}_duration_probability.csv"
            duration_probabilities = CSV.read(duration_file)
            durations = duration_probabilities.map { |entry| entry[0].to_i }
            probabilities = duration_probabilities.map { |entry| entry[1].to_f }
            activity_duration_prob_map["#{cluster_type}_#{activity_name}_#{day_type}_#{time_of_day}"] = [durations, probabilities]
          end
        end
      end
    end
    return activity_duration_prob_map
  end

  # Sample the number of events in a cluster for a given activity type.
  #
  # @param cluster_size_prob_map [Hash] Map of activity name to array of probabilities for different cluster sizes
  # @param activity_type_name [String] Name of the activity type to sample cluster size for
  # @return [Integer] Number of events in the cluster (1-based)
  def sample_activity_cluster_size(cluster_size_prob_map, activity_type_name)
    cluster_size_probabilities = cluster_size_prob_map[activity_type_name]
    return weighted_random(cluster_size_probabilities) + 1
  end

  # Sample a duration for a given event type based on its probability distribution.
  #
  # @param duration_probabilites_map [Hash] Map of event type to array containing durations and probabilities
  # @param event_type [String] Type of event to sample duration for (e.g. 'hot_water_clothes_washer')
  # @return [Float] Duration in minutes for the sampled event
  def sample_event_duration(duration_probabilites_map, event_type)
    durations = duration_probabilites_map[event_type][0]
    probabilities = duration_probabilites_map[event_type][1]
    return durations[weighted_random(probabilities)]
  end

  # Sample a duration for an activity based on occupant type, activity type, day type and hour.
  #
  # @param activity_duration_prob_map [Hash] Map of activity parameters to arrays containing durations and probabilities
  # @param occ_type_id [String] Occupant type ID (cluster type)
  # @param activity [Integer] Activity state number (1=shower, 2=laundry, 3=cooking, 4=dishwashing)
  # @param day_type [String] Type of day ('weekday' or 'weekend')
  # @param hour [Integer] Hour of the day (0-23)
  # @return [Integer] Duration in minutes for the sampled activity
  def sample_activity_duration(activity_duration_prob_map, occ_type_id, activity, day_type, hour)
    # States are: 'sleeping', 'shower', 'laundry', 'cooking', 'dishwashing', 'absent', 'nothingAtHome'
    if hour < 8
      time_of_day = 'morning'
    elsif hour < 16
      time_of_day = 'midday'
    else
      time_of_day = 'evening'
    end

    if activity == 1
      activity_name = 'shower'
    elsif activity == 2
      activity_name = 'laundry'
    elsif activity == 3
      activity_name = 'cooking'
    elsif activity == 4
      activity_name = 'dishwashing'
    else
      return 1 # all other activity will span only one mkc step
    end
    durations = activity_duration_prob_map["#{occ_type_id}_#{activity_name}_#{day_type}_#{time_of_day}"][0]
    probabilities = activity_duration_prob_map["#{occ_type_id}_#{activity_name}_#{day_type}_#{time_of_day}"][1]
    return durations[weighted_random(probabilities)]
  end

  # Export the generated schedules to a CSV file.
  #
  # @param schedules_path [String] Path to write the schedules CSV file to
  # @return [Boolean] Returns true if successful, false if there was an error
  def export(schedules_path:)
    (SchedulesFile::Columns.values.map { |c| c.name } - @column_names).each do |col_to_remove|
      @schedules.delete(col_to_remove)
    end
    schedule_keys = @schedules.keys
    schedule_rows = @schedules.values.transpose.map { |row| row.map { |x| '%.3g' % x } }
    if @append_output && File.exist?(schedules_path)
      table = CSV.read(schedules_path)
      if table.size != schedule_rows.size + 1
        @runner.registerError("Invalid number of rows (#{table.size}) in file.csv. Expected #{schedule_rows.size + 1} rows (including the header row).")
        return false
      end
      schedule_keys = table[0] + schedule_keys
      schedule_rows = schedule_rows.map.with_index { |row, i| table[i + 1] + row }
    end

    # Note: We don't use the CSV library here because it's slow for large files
    File.open(schedules_path, 'w') do |csv|
      csv << "#{schedule_keys.join(',')}\n"
      schedule_rows.each do |row|
        csv << "#{row.join(',')}\n"
      end
    end

    return true
  end

  # Generate a random number from a Gaussian (normal) distribution with the given parameters.
  #
  # @param mean [Float] The mean (average) value of the distribution
  # @param std [Float] The standard deviation of the distribution
  # @param min [Float] The minimum allowed value (defaults to 0.1)
  # @param max [Float] The maximum allowed value (optional)
  # @return [Float] A random number drawn from the specified Gaussian distribution, clipped to min/max if specified
  def gaussian_rand(mean, std, min = 0.1, max = nil)
    t = 2 * Math::PI * @prng.rand
    r = Math.sqrt(-2 * Math.log(1 - @prng.rand))
    scale = std * r
    x = mean + scale * Math.cos(t)
    if (not min.nil?) && (x < min) then x = min end
    if (not max.nil?) && (x > max) then x = max end
    # y = mean + scale * Math.sin(t)
    return x
  end

  # Sum the activity state values across all occupants at a given time index.
  #
  # @param all_simulated_values [Array<Matrix>] Array of matrices containing Markov chain activity states for each occupant
  # @param activity_index [Integer] Index of the activity state to sum (0=sleeping, 1=shower, etc)
  # @param time_index [Integer] Time index to sum the activity state values at
  # @param max_clip [Integer, nil] Optional maximum value to clip the sum to
  # @return [Integer] Sum of the activity state values across occupants, clipped to max_clip if specified
  def sum_across_occupants(all_simulated_values, activity_index, time_index, max_clip: nil)
    sum = 0
    all_simulated_values.size.times do |i|
      sum += all_simulated_values[i][time_index, activity_index]
    end
    if (not max_clip.nil?) && (sum > max_clip)
      sum = max_clip
    end
    return sum
  end

  # Get a binary representation of occupant presence at a given time index.
  #
  # @param all_simulated_values [Array<Matrix>] Array of matrices containing Markov chain activity states for each occupant
  # @param time_index [int] time index in the array
  # @return [int] The integer whose binary representation indicates the presence of occupants. Bit 0
  # is presence of the first occupant, bit 1 is the presence of the second occupant, etc.
  def get_present_occupants(all_simulated_values, time_index)
    sum = 0
    multiplier = 1
    all_simulated_values.size.times do |i|
      # Since all_simulated_values[i][time_index, 5]) is 1 when the occupant is away, we need to subtract it from 1
      sum += (1 - all_simulated_values[i][time_index, 5]) * multiplier
      multiplier *= 2
    end
    return sum
  end

  # Define get_ev_occupant_number function
  # Determines which occupant will be assigned as the EV driver based on their away hours
  #
  # @param all_simulated_values [Array<Matrix>] Array of matrices containing Markov chain activity states for each occupant
  def get_ev_occupant_number(all_simulated_values)
    if @hpxml_bldg.vehicles.to_a.empty?
      return 0
    end

    vehicle = @hpxml_bldg.vehicles[0]
    hours_per_year = (vehicle.hours_per_week / 7) * UnitConversions.convert(1, 'yr', 'day')

    occupant_away_hours_per_year = []
    all_simulated_values.size.times do |i|
      occupant_away_hours_per_year[i] = all_simulated_values[i].column(5).sum() / 4
    end
    # Only keep occupants whose 80% (the portion available for driving) away hours are sufficent to meet hours_per_year
    elligible_occupant = occupant_away_hours_per_year.each_with_index.filter { |value, _| value * 0.8 > hours_per_year }
    if elligible_occupant.empty?
      # if nobody has enough away hours, find the index of the occupant with the highest away hours
      _, ev_occupant = occupant_away_hours_per_year.each_with_index.max_by { |value, _| value }
      return ev_occupant
    else
      # return the index of a random elligible occupant
      _, ev_occupant = elligible_occupant.sample(random: @prng)
      return ev_occupant
    end
  end

  # Normalize an array by dividing all values by the maximum value.
  #
  # @param arr [Array] Array of numeric values to normalize
  # @return [Array] Array with values normalized to between 0 and 1
  def normalize(arr)
    m = arr.max
    arr = arr.map { |a| a / m }
    return arr
  end

  # Scale lighting schedule values based on occupancy.
  #
  # @param sch [Array] Array of hourly lighting schedule values
  # @param minute [Integer] Current minute in simulation
  # @param active_occupant_percentage [Float] Percentage of occupants that are active (not sleeping/away)
  # @return [Float] Scaled lighting schedule value based on occupancy
  def scale_lighting_by_occupancy(sch, minute, active_occupant_percentage)
    day_start = minute / 1440
    day_sch = sch[day_start * 24, 24]
    current_val = sch[minute / 60]
    return day_sch.min + (current_val - day_sch.min) * active_occupant_percentage
  end

  # Get schedule value for current minute based on weekday/weekend schedule and occupancy.
  #
  # @param weekday_sch [Array] Array of hourly schedule values for weekdays
  # @param weekend_sch [Array] Array of hourly schedule values for weekends
  # @param monthly_multiplier [Array] Array of monthly multipliers to apply to schedule values
  # @param month [Integer] Current month (1-12)
  # @param is_weekday [Boolean] Whether current day is a weekday
  # @param minute [Integer] Current minute in simulation
  # @param active_occupant_percentage [Float] Percentage of occupants that are active (not sleeping/away)
  # @return [Float] Schedule value scaled by occupancy and monthly multiplier
  def get_value_from_daily_sch(weekday_sch, weekend_sch, monthly_multiplier, month, is_weekday, minute, active_occupant_percentage)
    is_weekday ? sch = weekday_sch : sch = weekend_sch
    full_occupancy_current_val = sch[((minute % 1440) / 60).to_i].to_f * monthly_multiplier[month - 1].to_f
    return sch.min + (full_occupancy_current_val - sch.min) * active_occupant_percentage
  end

  # Randomly select an index based on weighted probabilities.
  #
  # @param weights [Array<Float>] Array of probability weights that sum to 1
  # @return [Integer] Randomly selected index based on probability weights
  def weighted_random(weights)
    n = @prng.rand
    cum_weights = 0
    weights.each_with_index do |w, index|
      cum_weights += w
      if n <= cum_weights
        return index
      end
    end
    return weights.size - 1 # If the prob weight don't sum to n, return last index
  end

  # Get the Building America lighting schedule based on location and time zone.
  #
  # @param time_zone_utc_offset [Integer] Offset from UTC in hours
  # @param latitude [Float] Latitude in degrees
  # @param longitude [Float] Longitude in degrees
  # @param schedules_csv_data [Hash] Schedule data from CSV files
  # @return [Array] Array of hourly lighting schedule values
  def get_building_america_lighting_schedule(time_zone_utc_offset, latitude, longitude, schedules_csv_data)
    # Sunrise and sunset hours
    sunrise_hour = []
    sunset_hour = []
    std_long = -time_zone_utc_offset * 15
    normalized_hourly_lighting = [[1..24], [1..24], [1..24], [1..24], [1..24], [1..24], [1..24], [1..24], [1..24], [1..24], [1..24], [1..24]]
    for month in 0..11
      if latitude < 51.49
        m_num = month + 1
        jul_day = m_num * 30 - 15
        if not ((m_num < 4) || (m_num > 10))
          offset = 1
        else
          offset = 0
        end
        declination = 23.45 * Math.sin(0.9863 * (284 + jul_day) * 0.01745329)
        deg_rad = Math::PI / 180
        rad_deg = 1 / deg_rad
        b = (jul_day - 1) * 0.9863
        equation_of_time = (0.01667 * (0.01719 + 0.42815 * Math.cos(deg_rad * b) - 7.35205 * Math.sin(deg_rad * b) - 3.34976 * Math.cos(deg_rad * (2 * b)) - 9.37199 * Math.sin(deg_rad * (2 * b))))
        sunset_hour_angle = rad_deg * Math.acos(-1 * Math.tan(deg_rad * latitude) * Math.tan(deg_rad * declination))
        sunrise_hour[month] = offset + (12.0 - 1 * sunset_hour_angle / 15.0) - equation_of_time - (std_long + longitude) / 15
        sunset_hour[month] = offset + (12.0 + 1 * sunset_hour_angle / 15.0) - equation_of_time - (std_long + longitude) / 15
      else
        sunrise_hour = [8.125726064, 7.449258072, 6.388688653, 6.232405257, 5.27722936, 4.84705384, 5.127512162, 5.860163988, 6.684378904, 7.521267411, 7.390441945, 8.080667697]
        sunset_hour = [16.22214058, 17.08642353, 17.98324493, 19.83547864, 20.65149672, 21.20662992, 21.12124777, 20.37458274, 19.25834757, 18.08155615, 16.14359164, 15.75571306]
      end
    end

    june_kws = [0.060, 0.040, 0.035, 0.025, 0.020, 0.020, 0.020, 0.020, 0.020, 0.020, 0.020, 0.020, 0.020, 0.025, 0.030, 0.030, 0.025, 0.020, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.015, 0.020, 0.020, 0.020, 0.025, 0.025, 0.030, 0.030, 0.035, 0.045, 0.060, 0.085, 0.125, 0.145, 0.130, 0.105, 0.080]
    lighting_seasonal_multiplier = schedules_csv_data[SchedulesFile::Columns[:LightingInterior].name]['LightingInteriorMonthlyMultipliers'].split(',').map { |v| v.to_f }
    amplConst1 = 0.929707907917098
    sunsetLag1 = 2.45016230615269
    stdDevCons1 = 1.58679810983444
    amplConst2 = 1.1372291802273
    sunsetLag2 = 20.1501965859073
    stdDevCons2 = 2.36567663279954

    monthly_kwh_per_day = []
    days_m = Calendar.num_days_in_months(1999) # Intentionally excluding leap year designation
    wtd_avg_monthly_kwh_per_day = 0
    for monthNum in 1..12
      month = monthNum - 1
      monthHalfHourKWHs = [0]
      for hourNum in 0..9
        monthHalfHourKWHs[hourNum] = june_kws[hourNum]
      end
      for hourNum in 9..17
        hour = (hourNum + 1.0) * 0.5
        monthHalfHourKWHs[hourNum] = (monthHalfHourKWHs[8] - (0.15 / (2 * Math::PI)) * Math.sin((2 * Math::PI) * (hour - 4.5) / 3.5) + (0.15 / 3.5) * (hour - 4.5)) * lighting_seasonal_multiplier[month]
      end
      for hourNum in 17..29
        hour = (hourNum + 1.0) * 0.5
        monthHalfHourKWHs[hourNum] = (monthHalfHourKWHs[16] - (-0.02 / (2 * Math::PI)) * Math.sin((2 * Math::PI) * (hour - 8.5) / 5.5) + (-0.02 / 5.5) * (hour - 8.5)) * lighting_seasonal_multiplier[month]
      end
      for hourNum in 29..45
        hour = (hourNum + 1.0) * 0.5
        monthHalfHourKWHs[hourNum] = (monthHalfHourKWHs[28] + amplConst1 * Math.exp((-1.0 * (hour - (sunset_hour[month] + sunsetLag1))**2) / (2.0 * ((25.5 / ((6.5 - monthNum).abs + 20.0)) * stdDevCons1)**2)) / ((25.5 / ((6.5 - monthNum).abs + 20.0)) * stdDevCons1 * (2.0 * Math::PI)**0.5))
      end
      for hourNum in 45..46
        hour = (hourNum + 1.0) * 0.5
        temp1 = (monthHalfHourKWHs[44] + amplConst1 * Math.exp((-1.0 * (hour - (sunset_hour[month] + sunsetLag1))**2) / (2.0 * ((25.5 / ((6.5 - monthNum).abs + 20.0)) * stdDevCons1)**2)) / ((25.5 / ((6.5 - monthNum).abs + 20.0)) * stdDevCons1 * (2.0 * Math::PI)**0.5))
        temp2 = (0.04 + amplConst2 * Math.exp((-1.0 * (hour - sunsetLag2)**2) / (2.0 * stdDevCons2**2)) / (stdDevCons2 * (2.0 * Math::PI)**0.5))
        if sunsetLag2 < sunset_hour[month] + sunsetLag1
          monthHalfHourKWHs[hourNum] = [temp1, temp2].min
        else
          monthHalfHourKWHs[hourNum] = [temp1, temp2].max
        end
      end
      for hourNum in 46..47
        hour = (hourNum + 1) * 0.5
        monthHalfHourKWHs[hourNum] = (0.04 + amplConst2 * Math.exp((-1.0 * (hour - sunsetLag2)**2) / (2.0 * stdDevCons2**2)) / (stdDevCons2 * (2.0 * Math::PI)**0.5))
      end

      sum_kWh = 0.0
      for timenum in 0..47
        sum_kWh += monthHalfHourKWHs[timenum]
      end
      for hour in 0..23
        ltg_hour = (monthHalfHourKWHs[hour * 2] + monthHalfHourKWHs[hour * 2 + 1]).to_f
        normalized_hourly_lighting[month][hour] = ltg_hour / sum_kWh
        monthly_kwh_per_day[month] = sum_kWh / 2.0
      end
      wtd_avg_monthly_kwh_per_day += monthly_kwh_per_day[month] * days_m[month] / 365.0
    end

    # Calculate normalized monthly lighting fractions
    seasonal_multiplier = []
    sumproduct_seasonal_multiplier = 0
    normalized_monthly_lighting = seasonal_multiplier
    for month in 0..11
      seasonal_multiplier[month] = (monthly_kwh_per_day[month] / wtd_avg_monthly_kwh_per_day)
      sumproduct_seasonal_multiplier += seasonal_multiplier[month] * days_m[month]
    end

    for month in 0..11
      normalized_monthly_lighting[month] = seasonal_multiplier[month] * days_m[month] / sumproduct_seasonal_multiplier
    end

    # Calculate schedule values
    lighting_sch = [[], [], [], [], [], [], [], [], [], [], [], []]
    for month in 0..11
      for hour in 0..23
        lighting_sch[month][hour] = normalized_monthly_lighting[month] * normalized_hourly_lighting[month][hour] / days_m[month]
      end
    end

    return lighting_sch
  end

  # Generates EV battery charging and discharging schedules based on away schedule and annual driving hours
  #
  # @param away_schedule [Array<Integer>] Array of 0s and 1s indicating when occupants are away (1) or home (0)
  # @param hours_driven_per_year [Float] Number of hours the EV is driven per year
  # @return [Array<Array<Integer>>] Two arrays - charging schedule and discharging schedule, each containing 0s and 1s
  def _get_ev_battery_schedule(away_schedule, hours_driven_per_year)
    total_driving_minutes_per_year = (hours_driven_per_year * 60).ceil
    expanded_away_schedule = away_schedule.flat_map { |status| [status] * 15 }
    charging_schedule = []
    discharging_schedule = []
    driving_minutes_used = 0
    chunk_counts = expanded_away_schedule.chunk(&:itself).map { |value, elements| [value, elements.size] }
    total_away_minutes = chunk_counts.map { |value, size| value * size }.sum
    extra_drive_minutes = 0 # accumulator for keeping track of extra driving minutes used due to ceil to upper integer
    chunk_counts.each do |is_away, activity_minutes|
      if is_away == 1
        current_chunk_proportion = (1.0 * activity_minutes) / total_away_minutes

        expected_driving_time = (total_driving_minutes_per_year * current_chunk_proportion - extra_drive_minutes).ceil
        max_driving_time = [expected_driving_time, total_driving_minutes_per_year - driving_minutes_used].min

        max_possible_driving_time = (activity_minutes * 0.8).ceil
        actual_driving_time = [max_driving_time, max_possible_driving_time].min
        extra_drive_minutes += actual_driving_time - total_driving_minutes_per_year * current_chunk_proportion

        idle_time = activity_minutes - actual_driving_time
        first_half_driving = (actual_driving_time / 2.0).ceil
        second_half_driving = actual_driving_time - first_half_driving

        discharging_schedule += [1] * first_half_driving  # Start driving
        discharging_schedule += [0] * idle_time           # Idle in the middle
        discharging_schedule += [1] * second_half_driving # End driving
        charging_schedule += [0] * activity_minutes

        driving_minutes_used += actual_driving_time
      else
        charging_schedule += [1] * activity_minutes
        discharging_schedule += [0] * activity_minutes
      end
    end
    if driving_minutes_used < total_driving_minutes_per_year
      msg = "Insufficient away minutes (#{total_away_minutes}) for required driving minutes (#{hours_driven_per_year * 60})"
      msg += "Only #{driving_minutes_used} minutes was used."
      @runner.registerWarning(msg)
    end

    return charging_schedule, discharging_schedule
  end

  # Fill EV battery charging and discharging schedules based on Markov chain simulation results
  #
  # @param markov_chain_simulation_result [Array<Matrix>] Array of matrices containing Markov chain simulation results for each occupant
  # @return [void] Updates @schedules with EV battery charging and discharging schedules
  def fill_ev_battery_schedule(markov_chain_simulation_result)
    if @hpxml_bldg.vehicles.to_a.empty?
      return
    end

    vehicle = @hpxml_bldg.vehicles[0]
    hours_per_year = (vehicle.hours_per_week / 7) * UnitConversions.convert(1, 'yr', 'day')
    away_index = 5 # Index of away activity in the markov-chain simulator
    away_schedule = markov_chain_simulation_result[@ev_occupant_number].column(away_index)
    charging_schedule, discharging_schedule = _get_ev_battery_schedule(away_schedule, hours_per_year)
    agg_charging_schedule = aggregate_array(charging_schedule, @minutes_per_step).map { |val| val.to_f / @minutes_per_step }
    agg_discharging_schedule = aggregate_array(discharging_schedule, @minutes_per_step).map { |val| val.to_f / @minutes_per_step }
    @schedules[SchedulesFile::Columns[:EVBatteryCharging].name] = agg_charging_schedule
    @schedules[SchedulesFile::Columns[:EVBatteryDischarging].name] = agg_discharging_schedule
  end

  # Get the weekday/weekend schedule fractions for TV plug loads and monthly multipliers for interior lighting, dishwasher, clothes washer/dryer, cooking range, and other/TV plug loads.
  #
  # @return [Hash] { schedule_name => { element => values, ... }, ... }
  def get_schedules_csv_data()
    schedules_csv = File.join(File.dirname(__FILE__), 'schedules.csv')
    if not File.exist?(schedules_csv)
      fail 'Could not find schedules.csv'
    end

    require 'csv'
    schedules_csv_data = {}
    CSV.foreach(schedules_csv, headers: true) do |row|
      schedule_name = row['Schedule Name']
      element = row['Element']
      values = row['Values']

      schedules_csv_data[schedule_name] = {} if !schedules_csv_data.keys.include?(schedule_name)
      schedules_csv_data[schedule_name][element] = values
    end

    return schedules_csv_data
  end
end

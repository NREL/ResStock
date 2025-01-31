require 'date'
require 'csv'
require 'json'
require 'openstudio'

Dir["#{File.dirname(__FILE__)}/../../../../resources/hpxml-measures/HPXMLtoOpenStudio/resources/*.rb"].each do |resource_file|
  next if resource_file.include? 'minitest_helper.rb'
  require resource_file
end

FlexibilityInputs = Struct.new(:peak_offset, :pre_peak_duration_steps, :pre_peak_offset, :random_shift_steps, keyword_init: true)
DailyPeakIndices = Struct.new(:pre_peak_start_index, :peak_start_index, :peak_end_index)


class HVACScheduleModifier
  def initialize(state:, sim_year:, weather:, epw_path:, minutes_per_step:, runner:, hpxml:, building_index:)
    @state = state
    @minutes_per_step = minutes_per_step
    @runner = runner
    @weather = weather
    @epw_path = epw_path
    @daily_avg_temps = _get_daily_avg_temps
    @sim_year = Location.get_sim_calendar_year(sim_year, @weather)
    @total_days_in_year = Calendar.num_days_in_year(@sim_year)
    @sim_start_day = DateTime.new(@sim_year, 1, 1)
    @steps_in_day = 24 * 60 / @minutes_per_step
    @num_timesteps_per_hour = 60 / @minutes_per_step
    current_dir = File.dirname(__FILE__)
    @peak_hours_dict_shift = JSON.parse(File.read("#{current_dir}/seasonal_shifting_peak_hours.json"))
    @peak_hours_dict_shed = JSON.parse(File.read("#{current_dir}/seasonal_shedding_peak_hours.json"))
    @hpxml = hpxml
    @hpxml_bldg = @hpxml.buildings[building_index]
  end

  def modify_setpoints(setpoints, flexibility_inputs)
    log_inputs(flexibility_inputs)
    dst_info = _daylight_savings_month_day()
    puts dst_info
    heating_setpoint = setpoints[:heating_setpoint].dup
    cooling_setpoint = setpoints[:cooling_setpoint].dup
    raise "heating_setpoint.length != cooling_setpoint.length" unless heating_setpoint.length == cooling_setpoint.length

    total_indices = heating_setpoint.length
    total_indices.times do |index|
      offset_times = _get_peak_times(index, flexibility_inputs, dst_info)
      day_type = _get_day_type(index)
      if day_type == 'heating'
        heating_setpoint[index] += _get_setpoint_offset(index, 'heating', offset_times, flexibility_inputs)
        # If the offset causes the set points to be inverted, adjust the cooling setpoint to correct it
        # This can happen during pre-heating if originally the cooling and heating setpoints were the same
        if heating_setpoint[index] > cooling_setpoint[index]
          cooling_setpoint[index] = heating_setpoint[index]
        end
        heating_setpoint[index] = _clip_setpoints(day_type, heating_setpoint[index])
      else
        cooling_setpoint[index] += _get_setpoint_offset(index, 'cooling', offset_times, flexibility_inputs)
        # If the offset causes the set points to be inverted, adjust the heating setpoint to correct it
        # This can happen during pre-cooling if originally the cooling and heating setpoints were the same
        if heating_setpoint[index] > cooling_setpoint[index]
          heating_setpoint[index] = cooling_setpoint[index]
        end
        cooling_setpoint[index] = _clip_setpoints(day_type, cooling_setpoint[index])
      end
    end
    { heating_setpoint: heating_setpoint, cooling_setpoint: cooling_setpoint }
  end

  def _clip_setpoints(day_type, setpoint)
    return 80 if day_type == 'heating' && setpoint > 80
    return 55 if day_type == 'heating' && setpoint < 55
    return 80 if day_type == 'cooling' && setpoint > 80
    return 60 if day_type == 'cooling' && setpoint < 60
    setpoint
  end

  def _get_peak_times(index, flexibility_inputs, dst_info)
    month, day = _get_month_day(index:)

    pre_peak_duration = flexibility_inputs.pre_peak_duration_steps
    peak_hour_start, peak_hour_end = _get_peak_hour(pre_peak_duration, month:)
    dst_adjust_hour = _dst_ajustment(month, day, dst_info)
    peak_hour_start += dst_adjust_hour
    peak_hour_end += dst_adjust_hour

    peak_times = DailyPeakIndices.new
    random_shift_steps = flexibility_inputs.random_shift_steps
    peak_times.peak_start_index = peak_hour_start * @num_timesteps_per_hour + random_shift_steps
    peak_times.peak_end_index = peak_hour_end * @num_timesteps_per_hour + random_shift_steps
    peak_times.pre_peak_start_index = peak_times.peak_start_index - flexibility_inputs.pre_peak_duration_steps
    return peak_times
  end

  def _get_setpoint_offset(index, setpoint_type, offset_times, flexibility_inputs)
    case setpoint_type
    when 'heating'
      pre_peak_offset = flexibility_inputs.pre_peak_offset
      peak_offset = -flexibility_inputs.peak_offset
    when 'cooling'
      pre_peak_offset = -flexibility_inputs.pre_peak_offset
      peak_offset = flexibility_inputs.peak_offset
    else
      raise "Unsupported setpoint type: #{setpoint_type}"
    end

    index_in_day = index % (24 * @num_timesteps_per_hour)
    if offset_times.pre_peak_start_index <= index_in_day && index_in_day < offset_times.peak_start_index
      pre_peak_offset
    elsif offset_times.peak_start_index <= index_in_day && index_in_day < offset_times.peak_end_index
      peak_offset
    else
      0
    end
  end

  def _get_month_day(index:)
    start_of_year = Date.new(@sim_year, 1, 1)
    index_date = start_of_year + (index.to_f / @num_timesteps_per_hour / 24)
    index_date.month
    index_date.day
    return index_date.month, index_date.day
  end

  def _get_peak_hour(pre_peak_duration, month:)
    if pre_peak_duration == 0
      peak_hours = @peak_hours_dict_shed[@state]
    else
      peak_hours = @peak_hours_dict_shift[@state]
    end
    if [6, 7, 8, 9].include?(month)
      return peak_hours["summer_peak_start"][11..12].to_i, peak_hours["summer_peak_end"][11..12].to_i
    elsif [1, 2, 3, 12].include?(month)
      return peak_hours["winter_peak_start"][11..12].to_i, peak_hours["winter_peak_end"][11..12].to_i
    else
      return peak_hours["intermediate_peak_start"][11..12].to_i, peak_hours["intermediate_peak_end"][11..12].to_i
    end
  end

  def _daylight_savings_month_day()
    if @hpxml_bldg.dst_enabled
      if @hpxml_bldg.dst_begin_month.nil? || @hpxml_bldg.dst_begin_day.nil? || @hpxml_bldg.dst_end_month.nil? || @hpxml_bldg.dst_end_day.nil?
        if (not @weather.header.DSTStartDate.nil?) && (not @weather.header.DSTEndDate.nil?)
          # Use weather file DST dates if available
          dst_start_date = @weather.header.DSTStartDate
          dst_end_date = @weather.header.DSTEndDate
          @hpxml_bldg.dst_begin_month = dst_start_date.monthOfYear.value
          @hpxml_bldg.dst_begin_day = dst_start_date.dayOfMonth
          @hpxml_bldg.dst_end_month = dst_end_date.monthOfYear.value
          @hpxml_bldg.dst_end_day = dst_end_date.dayOfMonth
        else
          # Roughly average US dates according to https://en.wikipedia.org/wiki/Daylight_saving_time_in_the_United_States
          @hpxml_bldg.dst_begin_month = 3
          @hpxml_bldg.dst_begin_day = 12
          @hpxml_bldg.dst_end_month = 11
          @hpxml_bldg.dst_end_day = 5
        end
        @hpxml_bldg.dst_begin_month_isdefaulted = true
        @hpxml_bldg.dst_begin_day_isdefaulted = true
        @hpxml_bldg.dst_end_month_isdefaulted = true
        @hpxml_bldg.dst_end_day_isdefaulted = true
      end
    else
      @hpxml_bldg.dst_begin_month = 0
      @hpxml_bldg.dst_begin_day = 0
      @hpxml_bldg.dst_end_month = 0
      @hpxml_bldg.dst_end_day = 0
    end
    dst_info = {dst_begin_month: @hpxml_bldg.dst_begin_month,
                dst_begin_day: @hpxml_bldg.dst_begin_day,
                dst_end_month: @hpxml_bldg.dst_end_month,
                dst_end_day: @hpxml_bldg.dst_end_day}
    return dst_info
  end

  def _dst_ajustment(month, day, dst_info)
    if month > dst_info[:dst_begin_month] &&  month < dst_info[:dst_end_month]
      dst_adjust_hour = 1
    elsif month == dst_info[:dst_begin_month] && day >= dst_info[:dst_begin_day] # double check
      dst_adjust_hour = 1
    elsif month == dst_info[:dst_end_month] && day < dst_info[:dst_end_day] # double check
      dst_adjust_hour = 1
    else
      dst_adjust_hour = 0
    end
    return dst_adjust_hour
  end

  def _get_day_type(index)
    day = index / @steps_in_day
    if @daily_avg_temps[day] < 66.0
      return 'heating'
    else
      return 'cooling'
    end
  end

  def _get_daily_avg_temps
    epw_file = OpenStudio::EpwFile.new(@epw_path, true)
    daily_avg_temps = []
    hourly_temps = []
    epw_file.data.each_with_index do |epwdata, rownum|
      begin
        db_temp = epwdata.dryBulbTemperature.get
      rescue
        fail "Cannot retrieve dryBulbTemperature from the EPW for hour #{rownum + 1}."
      end
      hourly_temps << db_temp
      if (rownum + 1) % (24 * epw_file.recordsPerHour) == 0
        daily_avg_temps << hourly_temps.sum / hourly_temps.length
        hourly_temps = []
      end
    end
    daily_avg_temps.map { |temp| UnitConversions.convert(temp, 'C', 'F') }
  end

  def log_inputs(inputs)
    return unless @runner
    @runner.registerInfo("Modifying setpoints ...")
    @runner.registerInfo("pre_peak_duration_steps=#{inputs.pre_peak_duration_steps}")
    @runner.registerInfo("random_shift_steps=#{inputs.random_shift_steps}")
    @runner.registerInfo("pre_peak_offset=#{inputs.pre_peak_offset}")
    @runner.registerInfo("peak_offset=#{inputs.peak_offset}")
  end
end

require 'time'
require './calendar_days'

def time(hour, minute)
  Time.new(1970, 1, 1, hour, minute, 0)
end

def without_date(ruby_time)
  time(ruby_time.hour, ruby_time.min)
end

class TimeRange
  attr_reader :start_time, :end_time

  def initialize(start_time, end_time)
    @start_time = start_time
    @end_time = end_time
  end

  def includes?(time)
    (without_date(time) >= @start_time) && (without_date(time) <= @end_time)
  end
end

class Period < TimeRange
  attr_reader :block

  def self.from_range(range, block)
    Period.new(range.start_time, range.end_time, block)
  end

  def initialize(start_time, end_time, block)
    super(start_time, end_time)
    @block = block
  end
end

require './current_schedule'

class Schedule < TimeRange
  def self.of_day(day)
    case day
    when StandardDay, ExamDay, HalfDay
      Schedule.new(CurrentSchedule.periods_of_day(day))
    when UnknownDay, Holiday
      return nil
    else
      raise Exception, 'Unknown type of day passed to Schedule.of_day'
    end
  end

  attr_reader :periods

  # @param [Array[Period]] periods
  def initialize(periods)
    super(periods.first.start_time, periods.last.end_time)
    @periods = periods
  end

  def period_index_at_time(time)
    @periods.find_index { |p| p.includes? without_date(time) }
  end

  def period_at_time(time)
    index = period_index_at_time(time)

    index.nil? ? nil : @periods[index]
  end

  def periods_indices_before_after_time(datetime)
    time = without_date(datetime)

    (@periods.length - 1).times do |i|
      if @periods[i].end_time <= time &&
          @periods[i+1].start_time >= time
        return [i, i+1]
      end
      if @periods[i].includes? time
        return [i, i]
      end
    end

    @periods.last.includes?(time) ? [@periods.length-1, @periods.length-1] : nil
  end

  def periods_before_after_time(time)
    res = periods_indices_before_after_time(time)

    res.nil? ? nil : res.map { |i| @periods[i] }
  end
end

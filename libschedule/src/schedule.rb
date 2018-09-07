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
    (time >= @start_time) && (time <= @end_time)
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
    if day.is_a? StandardDay
      return Schedule.new(CurrentSchedule.periods_of_day(day.number))
    end

    if [UnknownDay, Holiday].include? day.class
      return nil
    end

  end

  attr_reader :periods

  def initialize(periods)
    super(periods.first.start_time, periods.last.end_time)
    @periods = periods
  end

  def period_index_at_time(time)
    @periods.find_index { |p| p.includes? without_date(time) }
  end

  def period_at_time(time)
    index = period_index_at_time(time)

    if index.nil?
      nil
    else
      @periods[index]
    end
  end
end
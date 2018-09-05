require 'calendar_days'

class Exclusion
  attr_reader :start_date, :end_date, :description

  def initialize(start, _end, day_gen)
    @start_date = start
    @end_date = _end
    @day = day_gen
  end

  def includes?(date)
    date >= @start_date and date <= @end_date
  end

  def included_day
    @day.call
  end
end

require 'current_calendar'

class Calendar
  def self.current
    Calendar.new([], CurrentCalendar.exclusions, CurrentCalendar.start_date, CurrentCalendar.end_date)
  end

  attr_reader :exclusions

  # @param [Array[Exclusion]] overrides
  # @param [Array[Exclusion]] exclusions
  def initialize(overrides, exclusions, start_date, end_date)
    @overrides = overrides
    @exclusions = exclusions
    @correlations = {start_date => 1}

    @start_date = start_date
    @end_date = end_date
  end

  def excluded?(date)
    @exclusions.any? { |out| out.includes? date }
  end

  def day_on(date)
    return weekend if weekend?(date)

    (@overrides + @exclusions).each do |holiday|
      if holiday.includes? date
        return holiday.included_day
      end
    end

    unless includes?(date)
      throw ArgumentError.new('Date out of range')
    end

    day_of_date = iterate_for_day(date)
    @correlations[date] = day_of_date
    day day_of_date
  end

  private

  def weekend?(date)
    date.cwday > 5
  end

  def includes?(date)
    date >= @start_date and date <= @end_date
  end

  def most_recent_correlation(query_date)
    date = query_date.clone
    until @correlations.key? date
      date -= 1
    end
    date
  end

  def iterate_for_day(query_date)
    date = most_recent_correlation(query_date)
    day = @correlations[date]

    while date != query_date
      date += 1
      unless excluded? date or weekend? date
        day += 1
        day = 1 if day == 9
      end
    end

    day
  end
end

def day(number)
  StandardDay.new(number)
end
def weekend
  Holiday.new('Weekend')
end
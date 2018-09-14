require './calendar_days'

class Exclusion
  attr_reader :start_date, :end_date

  def initialize(start, end_date, day)
    @start_date = start
    @end_date = end_date
    @day = day
  end

  def includes?(date)
    (date >= @start_date) && (date <= @end_date)
  end

  def included_day
    @day.clone
  end
end

require './current_calendar'

class Calendar
  def self.current
    Calendar.new(CurrentCalendar.overrides,
                 CurrentCalendar.exclusions,
                 CurrentCalendar.start_date,
                 CurrentCalendar.end_date)
  end

  attr_reader :overrides, :exclusions

  def initialize(overrides, exclusions, start_date, end_date)
    @overrides = overrides
    @exclusions = exclusions
    @correlations = {start_date => 1}

    @start_date = start_date
    @end_date = end_date
  end

  def excluded?(date)
    @exclusions.any? {|out| out.includes? date}
  end

  def day_on(date)
    throw ArgumentError.new('Date out of range') unless includes?(date)

    (@overrides + @exclusions).each do |holiday|
      return holiday.included_day if holiday.includes? date
    end

    return weekend if weekend?(date)

    day_of_date = iterate_for_day(date)
    @correlations[date] = day_of_date
    day day_of_date
  end

  def includes?(date)
    (date >= @start_date) && (date <= @end_date)
  end

  def next_nonholiday(date)
    loop do
      date += 1
      break unless day_on(date).is_a? Holiday
    end
    date
  end

  private

  def weekend?(date)
    date.cwday > 5
  end

  def most_recent_correlation(query_date)
    date = query_date.clone
    date -= 1 until @correlations.key? date
    date
  end

  def iterate_for_day(query_date)
    date = most_recent_correlation(query_date)
    day = @correlations[date]

    while date != query_date
      date += 1
      unless excluded?(date) || weekend?(date)
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

class Calendar
  def self.current
    Calendar.new
  end

  def day_on(date)
    return nil if date.cwday > 5
    day 5
  end
end

def day(number)
  Day.new(number)
end


# Describes all possible classifications of one day in the 7+H system.
# May include:
# - Standard days 1 to 8
# - Half day
# - Unknown schedule (Days X, Y, Z)
# - Exam day
# - No school (nil)
class Day
  attr_accessor :number

  def initialize(day_number)
    @number = day_number
  end
end
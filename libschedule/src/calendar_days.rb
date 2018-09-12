class Day
  def description
    'Generic Day'
  end
end

# Describes all possible classifications of one day in the 7+H system.
# May include:
# - Standard days 1 to 8
# - Half day
# - Unknown schedule (Days X, Y, Z)
# - Exam day
# - No school (nil)
# - Delayed
class StandardDay < Day
  attr_reader :number

  def initialize(day_number, delayed = false)
    @number = day_number
    @delayed = delayed
  end

  def description
    "Day #{@number}#{' (Delayed)' if @delayed}"
  end
end

class HalfDay < Day
  attr_reader :blocks

  def initialize(blocks)
    @blocks = blocks
  end

  def description
    'Half day'
  end
end

class UnknownDay < Day
  attr_reader :name

  def initialize(name)
    @name = name
  end

  def description
    "#{@name} (Unknown schedule)"
  end
end

class ExamDay < Day
  # Each exam day consists of finals from two blocks (e.g. C and F)
  # :test_blocks is an array of two str's
  attr_reader :test_blocks

  def initialize(blocks)
    @test_blocks = blocks
  end

  def description
    'Exam day'
  end
end

class Holiday < Day

  def initialize(description)
    @description = description
  end

  def description
    "#{@description} (No School)"
  end
end
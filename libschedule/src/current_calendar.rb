require 'calendar'
require 'date'

def holiday(start, _end, description)
  Exclusion.new(start, _end, lambda {Holiday.new(description)})
end

def single_holiday(date, description)
  holiday(date, date, description)
end

def half_day(date)
  Exclusion.new(date, date, lambda {HalfDay.new})
end

def unknown_day(date, letter)
  Exclusion.new(date, date, lambda {UnknownDay.new("Day #{letter}")})
end

def exam_day(date, block1, block2)
  Exclusion.new(date, date, lambda {ExamDay.new([block1, block2])})
end

module CurrentCalendar
  def self.start_date
    Date.new(2018, 8, 29)
  end
  def self.end_date
    Date.new(2019, 6, 14)
  end

  def self.exclusions
    [
        holiday(Date.new(2018, 8, 31), Date.new(2018, 9, 3), 'Labor Day Recess'),
        single_holiday(Date.new(2018, 9, 10), 'Rosh Hashanah'),
        single_holiday(Date.new(2018, 9, 19), 'Yom Kippur'),
        single_holiday(Date.new(2018, 10, 8), 'Columbus Day'),
        half_day(Date.new(2018, 10, 19)),
        single_holiday(Date.new(2018, 11, 6), 'Professional Day'),
        single_holiday(Date.new(2018, 11, 12), 'Veterans Day'),
        half_day(Date.new(2018, 11, 21)),
        holiday(Date.new(2018, 11, 22), Date.new(2018, 11, 23), 'Thanksgiving Break'),
        half_day(Date.new(2018, 12, 7)),
        holiday(Date.new(2018, 12, 24), Date.new(2019, 1, 1), 'Christmas Break'),

        unknown_day(Date.new(2019, 1, 15), 'X'),
        unknown_day(Date.new(2019, 1, 16), 'Y'),
        unknown_day(Date.new(2019, 1, 17), 'Z'),
        exam_day(Date.new(2019, 1, 18), 'A', 'E'),
        exam_day(Date.new(2019, 1, 22), 'B', 'F'),
        exam_day(Date.new(2019, 1, 23), 'C', 'G'),
        exam_day(Date.new(2019, 1, 24), 'D', 'Makeup'),

        single_holiday(Date.new(2019, 1, 21), 'Martin Luther King Day'),

        half_day(Date.new(2019, 2, 1)),
        holiday(Date.new(2019, 2, 18), Date.new(2019, 2, 22), 'Winter Break'),
        half_day(Date.new(2019, 3, 15)),
        holiday(Date.new(2019, 4, 15), Date.new(2019, 4, 19), 'Spring Break'),
        half_day(Date.new(2019, 5, 3)),
        single_holiday(Date.new(2019, 5, 27), 'Memorial Day'),

        unknown_day(Date.new(2018, 6, 6), 'X'),
        half_day(Date.new(2018, 6, 7)),
        unknown_day(Date.new(2018, 6, 10), 'Y'),

        exam_day(Date.new(2019, 6, 11), 'A', 'E'),
        exam_day(Date.new(2019, 6, 12), 'B', 'F'),
        exam_day(Date.new(2019, 6, 13), 'C', 'G'),
        exam_day(Date.new(2019, 6, 14), 'D', 'Makeup'),
    ]
  end
end
require './schedule'

module CurrentSchedule
  PERIOD_RANGES = [
      TimeRange.new(time(7, 44), time(8, 44)),
      TimeRange.new(time(8, 48), time(10, 3)),
      TimeRange.new(time(10, 7), time(11, 7)),
      TimeRange.new(time(11, 11), time(13, 1)),
      TimeRange.new(time(13, 5), time(14, 5))
  ].freeze

  def self.periods_of_day(day)
    range_block_pairs(day).map do |range, block|
      Period.from_range(range, block)
    end
  end

  BLOCKS = [
      %w[A C H E G],
      %w[B D F G E],
      %w[A H D C F],
      %w[B A H G E],
      %w[C B F D G],
      %w[A H E F C],
      %w[B A D E G],
      %w[C B H F D]
  ].freeze

  def self.is_valid_day(day)
    day > 0 && day <= BLOCKS.length
  end

  EXAM_DAY_RANGES = [
      TimeRange.new(time(8, 0), time(9, 30)),
      TimeRange.new(time(10, 0), time(11, 30)),
      TimeRange.new(time(13, 0), time(14, 0))
  ].freeze

  HALF_DAY_RANGES = [
      TimeRange.new(time(7, 44), time(8, 29)),
      TimeRange.new(time(8, 33), time(9, 16)),
      TimeRange.new(time(9, 20), time(10, 3)),
      TimeRange.new(time(10, 7), time(10, 50))
  ].freeze

  def self.range_block_pairs(day)
    case day
    when StandardDay
      PERIOD_RANGES.zip(BLOCKS[day.number - 1])
    when ExamDay
      EXAM_DAY_RANGES.zip(day.test_blocks + ['Academic Support'])
    when HalfDay
      HALF_DAY_RANGES.zip(day.blocks)
    else
      raise ArgumentError, 'Unknown type of day'
    end
  end
end

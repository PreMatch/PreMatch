require './schedule'

module CurrentSchedule
  PERIOD_RANGES = [
      TimeRange.new(time(7, 44), time(8, 44)),
      TimeRange.new(time(8, 48), time(10, 3)),
      TimeRange.new(time(10, 7), time(11, 7)),
      TimeRange.new(time(11, 11), time(13, 1)),
      TimeRange.new(time(13, 5), time(14, 5))
  ]

  def CurrentSchedule.periods_of_day(day_num)
    BLOCKS[day_num - 1].zip(PERIOD_RANGES).map do |block, range|
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
  ]

end
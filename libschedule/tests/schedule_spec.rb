require 'rspec'

require './calendar'
require './schedule'

def period_reflects(one, start_time, end_time, block)
  (one.is_a? Period) &&
    (start_time == one.start_time) &&
    (end_time == one.end_time) &&
    (block == one.block)
end

def expect_blocks_of_day(day_number)
  schedule = Schedule.of_day(StandardDay.new(day_number))
  expect(schedule.periods.map(&:block))
end

def standard_schedule(day)
  Schedule.of_day(StandardDay.new(day))
end

describe 'Obtaining time-based schedules for days' do

  it 'should have the correct schedule for standard days' do
    day = StandardDay.new(1)
    schedule = Schedule.of_day(day)

    expect(schedule.periods.length).to be(5)
    expect(period_reflects(
             schedule.periods[0],
             time(7, 44), time(8, 44), 'A')).to be_truthy

    expect_blocks_of_day(1).to eql %w[A C H E G]
    expect_blocks_of_day(3).to eql %w[A H D C F]
    expect_blocks_of_day(5).to eql %w[C B F D G]
    expect_blocks_of_day(7).to eql %w[B A D E G]
  end

  it 'should return nil for days without a schedule' do
    [Holiday, UnknownDay].each do |day_type|
      expect(Schedule.of_day(day_type.new(''))).to be_nil
    end
  end

  it 'should tell period at time' do
    expect(standard_schedule(2).period_index_at_time(time(12, 12))).to be 3
    expect(standard_schedule(6).period_index_at_time(time(7, 44))).to be 0
    expect(standard_schedule(8).period_at_time(time(16, 22))).to be_nil
  end
end
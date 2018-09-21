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
  schedule = standard_schedule(day_number)
  expect(schedule.periods.map(&:block))
end

def standard_schedule(day)
  Schedule.of_day(StandardDay.new(day))
end

describe 'Obtaining time-based schedules for days' do
  it 'should have the correct schedule for standard days' do
    schedule = standard_schedule(1)

    expect(schedule.periods.length).to be(5)
    expect(period_reflects(
               schedule.periods[0],
               time(7, 44), time(8, 44), 'A'
           )).to be_truthy

    expect_blocks_of_day(1).to eql %w[A C H E G]
    expect_blocks_of_day(3).to eql %w[A H D C F]
    expect_blocks_of_day(5).to eql %w[C B F D G]
    expect_blocks_of_day(7).to eql %w[B A D E G]
  end

  it 'should have the correct schedule for exam days' do
    blocks = Schedule.of_day(ExamDay.new(%w[C G])).periods

    expect(period_reflects(blocks[0],
                           time(8, 0), time(9, 30), 'C')).to be_truthy
    expect(period_reflects(blocks[2],
                           time(13, 0), time(14, 0), 'Academic Support')).to be_truthy
  end

  it 'should have the correct schedule for half days' do
    blocks = Schedule.of_day(HalfDay.new(%w[A C D F])).periods

    expect(period_reflects(blocks[0],
                           time(7, 44), time(8, 29), 'A'))
    expect(period_reflects(blocks[3],
                           time(10, 7), time(10, 50), 'F'))
  end

  it 'should return nil for days without a schedule' do
    [Holiday, UnknownDay].each do |day_type|
      expect(Schedule.of_day(day_type.new(''))).to be_nil
    end
  end
end
describe 'Relating schedules to given times' do
  it 'should tell period at time during standard day' do
    expect(standard_schedule(2).period_index_at_time(time(12, 12))).to be 3
    expect(standard_schedule(6).period_index_at_time(time(7, 44))).to be 0
    expect(standard_schedule(8).period_at_time(time(16, 22))).to be_nil
  end

  it 'should tell previous and next periods when given time between periods' do
    before, after = standard_schedule(4).periods_before_after_time(time(11, 10))
    expect(before.block).to eql 'H'
    expect(after.block).to eql 'G'

    before, after = standard_schedule(6).periods_before_after_time(time(10, 5))
    expect(before.block).to eql 'H'
    expect(after.block).to eql 'E'
  end

  it 'should return two equivalent periods when given time within period' do
    before, after = standard_schedule(2).periods_before_after_time(time(8, 0))
    expect(before.block).to eql after.block
  end

  it 'should return nil when given time outside school hours' do

  end
end

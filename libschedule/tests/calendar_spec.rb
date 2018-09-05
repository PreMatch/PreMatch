require 'rspec'

$LOAD_PATH << '../src'
require 'calendar'
require 'date'

def day_on_current_calendar(year, month, day)
  Calendar.current.day_on Date.new(year, month, day)
end

describe 'Correct calculation of 7+H day from date' do

  it 'should determine normal days' do
    day = day_on_current_calendar(2018, 9, 6)
    expect(day.number).to eq 5
  end

  it 'should consider normal weekends' do
    day = day_on_current_calendar(2018, 10, 13)
    expect(day).to be nil
  end

  it 'should consider single holidays' do
    day = day_on_current_calendar(2018, 11, 12)
    expect(day).to be nil
  end
end
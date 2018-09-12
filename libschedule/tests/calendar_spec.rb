require 'rspec'

require './calendar'
require 'date'

def day_on_current_calendar(year, month, day)
  Calendar.current.day_on Date.new(year, month, day)
end

describe 'Correct calculation of 7+H day from date' do

  it 'should determine normal days' do
    day = day_on_current_calendar(2018, 9, 6)
    expect(day).to be_a StandardDay
    expect(day.number).to be 5

    day = day_on_current_calendar(2018, 12, 13)
    expect(day).to be_a StandardDay
    expect(day.number).to be 1

    day = day_on_current_calendar(2019, 3, 20)
    expect(day).to be_a StandardDay
    expect(day.number).to be 8

    day = day_on_current_calendar(2019, 5, 30)
    expect(day).to be_a StandardDay
    expect(day.number).to be 4
    expect(day.description).to eql 'Day 4'
  end

  it 'should consider normal weekends' do
    day = day_on_current_calendar(2018, 10, 13)
    expect(day).to be_a Holiday
    expect(day.description).to eql 'Weekend (No School)'
  end

  it 'should consider single holidays' do
    day = day_on_current_calendar(2018, 11, 12)
    expect(day).to be_a Holiday
    expect(day.description).to eql 'Veterans Day (No School)'
  end

  it 'should consider long holidays' do
    day = day_on_current_calendar(2018, 12, 25)
    expect(day).to be_a Holiday
    expect(day.description).to eql 'Christmas Break (No School)'
  end

  it 'should consider half days' do
    day = day_on_current_calendar(2018, 10, 19)
    expect(day).to be_a HalfDay
  end

  it 'should consider unknown days' do
    day = day_on_current_calendar(2019, 1, 16)
    expect(day).to be_a UnknownDay
    expect(day.description).to eql 'Day Y (Unknown schedule)'
  end

  it 'should consider exam days' do
    day = day_on_current_calendar(2019, 6, 13)
    expect(day).to be_a ExamDay
    expect(day.description).to eql 'Exam day'
  end

  it 'should throw an ArgumentError for dates outside school year' do
    expect { day_on_current_calendar(2017, 12, 26) }.to raise_error ArgumentError
    expect { day_on_current_calendar(2019, 6, 27) }.to raise_error ArgumentError
  end

  it 'should have blocks for each half-day' do
    expect(day_on_current_calendar(2018, 11, 21).blocks).to eql %w[A D C PepRally]
    expect(day_on_current_calendar(2019, 5, 3).blocks).to eql %w[A C E G]
  end
end
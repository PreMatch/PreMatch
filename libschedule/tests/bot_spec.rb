require 'rspec'
require 'time'

require './bot'

Bot.initialize

describe 'Responding to day commands' do

  def report_for_day(time)
    Bot.response_to :day, time
  end

  it 'should respond with correct message outside school year' do
    expect(report_for_day(Date.new(2017, 9, 11)))
      .to eql 'September 11, 2017 is not in the currently defined calendar year.'
  end

  it 'should respond with correct message on holiday' do
    expect(report_for_day(Date.new(2018, 11, 12)))
      .to eql 'November 12, 2018 is Veterans Day (No School)'
  end

  it 'should respond with correct message on days without known schedule' do
    expect(report_for_day(Date.new(2019, 1, 15)))
      .to eql 'January 15, 2019 is Day X, and I don\'t know the schedule.'
  end

  it 'should respond with description and blocks for days with schedule' do
    expect(report_for_day(Date.new(2018, 11, 5)))
      .to eql 'November 5, 2018 is a Day 3 with blocks A, H, D, C, F'
    expect(report_for_day(Date.new(2018, 12, 7)))
      .to eql 'December 7, 2018 is a Half day with blocks B, A, G, E'
    expect(report_for_day(Date.new(2019, 1, 18)))
      .to eql 'January 18, 2019 is a Exam day with blocks A, E, Academic Support'
  end
end

describe 'Responding to report commands' do
  it 'should respond to calls outside school year correctly' do

  end
end
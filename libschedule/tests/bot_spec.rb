require 'rspec'
require 'time'

require './bot'

describe 'Responding with embeds' do
  Bot.initialize

  def report_for(time)
    Bot.response_to :report, time
  end

  it 'should respond with correct message outside school year' do
    expect(report_for(Time.new(2017, 9, 11, 7, 10, 0)))
      .to eql 'We are not in the currently defined calendar year.'
  end

  it 'should respond with correct message on holiday' do
    expect(report_for(Time.new(2018, 11, 12, 10, 30, 0)))
      .to eql 'Enjoy your day off! Today is Veterans Day (No School)'
  end

  it 'should respond with correct message on days without known schedule' do
    expect(report_for(Time.new(2019, 1, 15, 12, 0, 0)))
      .to eql 'Today is Day X, but I do not know what the schedule is.'
  end
end

$LOAD_PATH << 'src'
require 'time'
require './calendar'
require './schedule'

require 'discordrb'

today = Calendar.current.day_on(Date.today)
puts "It is day #{today.number}"

period = Schedule.of_day(today).period_index_at_time(Time.now)
puts "It is Period #{period + 1}, Block #{Schedule.of_day(today).periods[period].block}" unless period.nil?

bot = Discordrb::Commands::CommandBot.new \
  token: 'NDE4MDg5MzY5OTQyMDk3OTIx.DXcfwA.hGGJJUR66WnhL4qwWXe5sJpMn34', prefix: '$$'

DAY_LANGUAGE = { today: 0, tomorrow: 1, yesterday: -1 }.freeze

def parse_day(arg)
  Date.parse(arg)
rescue StandardError
  Date.today + DAY_LANGUAGE.get(arg.downcase, arg.to_i)
end

bot.command :day do |event, *args|
end

bot.run

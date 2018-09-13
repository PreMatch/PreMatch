#$LOAD_PATH << 'src'
require 'time'
require './bot'
require 'discordrb'

require 'chronic'

bot = Discordrb::Commands::CommandBot.new \
  token: 'NDE4MDg5MzY5OTQyMDk3OTIx.DXcfwA.hGGJJUR66WnhL4qwWXe5sJpMn34', prefix: '$$'

Bot.initialize

bot.command :day do |event, *args|
  unless Discord.channel_verified(event.channel)
    event.send_message 'This server is not a verified AHS server.'
    return
  end

  date = Chronic.parse(args.join(' '))

  if date.nil?
    event.send_message(':thinking: I don\'t know what you mean.')
    return
  end

  event.send_message(Bot.response_to(:day, date.to_date, event))
end

bot.command :personalize do |event, *_args|
  Bot.response_to(:personalize, Date.today, event)
end

bot.command :myday do |event, *_args|
  Bot.response_to(:myday, Date.today, event)
  nil
end

bot.run

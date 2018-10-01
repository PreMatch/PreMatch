#$LOAD_PATH << 'src'
require 'time'
require './bot'
require 'discordrb'

require 'chronic'

bot = Discordrb::Commands::CommandBot.new \
  token: 'NDE4MDg5MzY5OTQyMDk3OTIx.DXcfwA.hGGJJUR66WnhL4qwWXe5sJpMn34', prefix: '$$'

Bot.initialize

bot.command :day do |event, *args|
  if args.empty?
    event.send_message(':question: Provide a day number or a date expression (like "tomorrow")')
    return
  end

  input_num = args[0].to_i
  if input_num.to_s == args[0]
    response = Bot.day_number(input_num)
    event.send_message(response) unless response.nil?
    return
  end

  date = Chronic.parse(args.join(' '))
  if date.nil? || date.is_a?(Chronic::Span)
    event.send_message(':thinking: I don\'t know what you mean.')
    return
  end

  response = Bot.day_cmd(date)
  event.send_message(response) unless response.nil?
end

bot.command :personalize do |event, *_args|
  Bot.personalize(event)
end

bot.command :myday do |event, *_args|
  resp = Bot.myday(event)
  event.send(resp) unless resp.nil?
end

bot.run

require './calendar'
require './schedule'
require './database'
require './personal'
require 'discordrb'

require 'openssl'

$discord_auth_url = 'https://discordapp.com/api/oauth2/authorize?client_id=418089369942097921&redirect_uri=https%3A%2F%2Fprematch.org%2Fdiscord&response_type=code&scope=identify'.freeze
$discord_secret = 'IIx8xkGg52On9-EkZrxm0OiIGoyOHBkv'
$verified_guilds = [
    365183228459352067
]

module Discord
  def self.auth_state(caller_id)
    # noinspection RubyArgCount
    OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new('sha1'), $discord_secret, caller_id.to_s)
  end

  def self.auth_url(caller_id)
    "https://discordapp.com/api/oauth2/authorize?client_id=418089369942097921&redirect_uri=https%3A%2F%2Fprematch.org%2Fdiscord&response_type=code&scope=identify&state=#{auth_state(caller_id)}".freeze
  end

  def self.channel_verified(channel)
    (channel.type == 0 && $verified_guilds.include?(channel.server.id)) or channel.type == 1
  end

  def self.embed_author
    Discordrb::Webhooks::EmbedAuthor.new(
        name: 'PreMatch Discord',
        url: 'https://prematch.org/about/discord',
        icon_url: 'https://prematch.org/static/img/PreMatch%20Logo.png'
    )
  end
end

module Bot
  def self.initialize
    @calendar = Calendar.current
    @database = Database.new
  end

  def self.personalize(init_event)
    caller_id = init_event.author.id
    handle = @database.associated_handle(caller_id)

    unless handle.nil?
      return "#{init_event.author.mention}, you are already associated to #{handle}!"
    end

    auth_url = Discord.auth_url(caller_id)
    init_event.author.pm("To associate your Discord account with PreMatch, visit #{auth_url}")
    init_event.author.pm('This link applies to you only. **Please do not send it to other users!**')

    unless init_event.channel.type == 1
      "I have slid into DMs, #{init_event.author.mention}. Take a look."
    end
  end

  def self.day_cmd(date_or_day_num)

    unless date_or_day_num.is_a? Time
      schedule = Schedule.of_day(StandardDay.new(date_or_day_num))
      return "Day #{date_or_day_num} has blocks #{schedule.periods.map(&:block).join(', ')}"
    end

    return "#{express_date call_date} is not in the currently defined calendar year." unless @calendar.includes? call_date

    call_day = @calendar.day_on call_date

    case call_day
    when Holiday
      return "#{express_date call_date} is #{call_day.description}"
    when UnknownDay
      return "#{express_date call_date} is #{call_day.name}, and I don't know the schedule."
    else
      schedule = Schedule.of_day(call_day)
      return "#{express_date call_date} is a #{call_day.description} with blocks #{schedule.periods.map(&:block).join(', ')}"
    end
  end

  def self.myday(init_event)
      handle = @database.associated_handle(init_event.author.id)
      return 'You are not associated with PreMatch! Try `$$personalize`.' if handle.nil?

      PersonalResponder.new(handle, Time.now, init_event, @database).respond
  end

  def self.express_date(date)
    date.strftime('%B %-d, %Y')
  end
end

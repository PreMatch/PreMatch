require './calendar'
require './schedule'
require './database'

require 'openssl'

$discord_auth_url = 'https://discordapp.com/api/oauth2/authorize?client_id=418089369942097921&redirect_uri=https%3A%2F%2Fprematch.org%2Fdiscord&response_type=code&scope=identify'.freeze
$discord_secret = 'IIx8xkGg52On9-EkZrxm0OiIGoyOHBkv'

module Discord
  def self.auth_state(caller_id)
    # noinspection RubyArgCount
    OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new('sha1'), $discord_secret, caller_id.to_s)
  end

  def self.auth_url(caller_id)
    "https://discordapp.com/api/oauth2/authorize?client_id=418089369942097921&redirect_uri=https%3A%2F%2Fprematch.org%2Fdiscord&response_type=code&scope=identify&state=#{auth_state(caller_id)}".freeze
  end
end

module Bot
  def self.initialize
    @calendar = Calendar.current
    @database = Database.new
  end


  def self.response_to(command, call_date, event)

    case command
    when :personalize

      caller_id = event.author.id
      handle = @database.associated_handle(caller_id)

      unless handle.nil?
        return "#{event.author.mention}, you are already associated to #{handle}!"
      end

      auth_url = Discord.auth_url(caller_id)
      event.author.pm("To associate your Discord account with PreMatch, visit #{auth_url}")
      event.author.pm('This link applies to you only. Please do not send it to other users!')

      unless event.channel.type == 1
        return "I have slid into DMs, #{event.author.mention}. Take a look."
      end

    when :day

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
  end

  private

  def self.express_date(date)
    date.strftime('%B %-d, %Y')
  end
end

require './calendar'
require './schedule'
require './database'
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
end

module Bot
  def self.initialize
    @calendar = Calendar.current
    @database = Database.new
  end

  def self.embed_author
    Discordrb::Webhooks::EmbedAuthor.new(
        name: 'PreMatch Discord',
        url: 'https://prematch.org',
        icon_url: 'https://prematch.org/static/img/PreMatch%20Logo.png'
    )
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

    when :myday
      return 'We are not in the currently defined calendar year. Is this summer?' unless @calendar.includes? call_date

      handle = @database.associated_handle(event.author.id.to_s)
      return 'You are not associated with PreMatch! Try $$personalize.' if handle.nil?

      schedule = @database.read_schedule(handle)
      call_day = @calendar.day_on(call_date)

      personal_respond(schedule, call_date, call_day, event)
      'Here you go'
    end
  end

  def self.personal_respond(schedule, call_date, call_day, event)
    status, target_date, target_desc = current_status(schedule, call_day, call_date)

    event.channel.send_embed do |embed|
      embed.add_field(
          name: 'Current status',
          value: status
      )
      render_embed(embed, schedule, target_date, target_desc)
    end

  end

  private

  # Returns [message, target_date, target_desc]
  def self.current_status(schedule, call_day, call_date)
    case call_day
    when Holiday
      return ['Enjoy your day off! Prepare for the next school day.',
              @calendar.next_nonholiday(call_date), 'next school day']
    when UnknownDay
      return ["Today's schedule is unknown to me.",
              @calendar.next_nonholiday(call_date), 'next school day']
    else
      timetable = Schedule.of_day(call_day)
      now = Time.new(1970, 1, 1, Time.now.hour, Time.now.min, 0)

      if now < timetable.start_time
        return ['Good morning. Here is your schedule for today',
                call_date, 'today']
      elsif now > timetable.end_time
        return ['School has ended for today. Prepare for the next school day.',
                @calendar.next_nonholiday(call_date), 'next school day']
      else
        now_block = timetable.period_at_time now
        if now_block.nil?
          return ['You are in school, between periods.',
                  call_date, 'today']
        else
          now_teacher = schedule[now_block.block] || 'an unknown teacher'

          return ["You are in block #{now_block.block} with #{now_teacher}",
                  call_date, 'today']
        end
      end
    end
  end

  def self.render_embed(embed, user_schedule, target_date, target_desc)
    today = @calendar.day_on(Date.today)
    target_day = @calendar.day_on target_date
    target_schedule = Schedule.of_day(target_day)
    target_blocks = target_schedule.periods.map(&:block)

    embed.title = "Today is #{today.description}"
    embed.description = "Showing #{target_desc} (#{target_day.description})"
    embed.author = embed_author
    embed.add_field(
        name: "Blocks",
        value: target_blocks.join("\n"),
        inline: true)
    embed.add_field(
        name: teacher_expr,
        value: target_blocks.map {|blk| user_schedule[blk]}.join("\n"),
        inline: true)
  end

  def self.teacher_expr
    Random.rand < 0.05 ? 'Prison Guards Crossed with Babysitters' : 'Teachers'
  end

  def self.express_date(date)
    date.strftime('%B %-d, %Y')
  end
end

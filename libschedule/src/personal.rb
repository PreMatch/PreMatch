require './database'

class PersonalResponder

  # @param [String] handle
  # @param [Time] call_time
  # @param [Discordrb::Commands::CommandEvent] command_event
  # @param [Google::Cloud::Datastore] database
  def initialize(handle, call_time, command_event, database)
    @handle = handle
    @call_time = without_date(call_time)
    @event = command_event

    @user_schedule = database.read_schedule(handle)
    @call_date = call_time.to_date

    return unless Calendar.current.includes? @call_date
    return if @user_schedule.nil?
    return unless Discord.channel_verified @event.channel

    @call_day = Calendar.current.day_on @call_date
    @call_schedule = Schedule.of_day @call_day
  end

  def respond
    unless Calendar.current.includes? @call_date
      @event.send_message ':calendar: We are not in the currently defined calendar year. Is this summer?'
      return
    end
    if @user_schedule.nil?
      @event.send_message ":dizzy_face: I couldn't find your schedule."
      return
    end
    unless Discord.channel_verified @event.channel
      @event.send_message ":no_entry: This is not a verified AHS-only server."
      return
    end

    @situation = caller_situation
    @target_date = target_date
    @target_message = target_message

    @event.channel.send_embed do |embed|
      embed.author = Discord.embed_author
      embed.title = "Today is #{@call_day.description}"
      embed.description = @target_message
      render_schedule_field(embed)
    end
  end

  def caller_situation
    return Situation::UNKNOWN if @call_day.is_a? UnknownDay
    return Situation::ON_HOLIDAY if @call_day.is_a? Holiday
    return Situation::BEFORE_SCHOOL if @call_time < @call_schedule.start_time
    return Situation::AFTER_SCHOOL if @call_time > @call_schedule.end_time

    @call_schedule.period_index_at_time(@call_time).nil? ?
        Situation::BETWEEN_PERIODS : Situation::DURING_PERIOD
  end

  def target_date
    if [Situation::UNKNOWN,
        Situation::ON_HOLIDAY,
        Situation::AFTER_SCHOOL].include? @situation
      return Calendar.current.next_nonholiday(@call_date)
    end

    @call_date
  end
  def target_message
    case @situation
    when Situation::ON_HOLIDAY
      return "Enjoy your day off."

    when Situation::UNKNOWN
      return "I don't know what you're up to."

    when Situation::BEFORE_SCHOOL
      return "#{@call_day.description} is coming up."

    when Situation::AFTER_SCHOOL
      return "You finished #{@call_day.description}."

    when Situation::DURING_PERIOD
      block = @call_schedule.period_at_time(@call_time).block
      teacher = @user_schedule[block] || 'an unknown teacher'
      return "You are in Block #{block} with #{teacher}."

    when Situation::BETWEEN_PERIODS
      before, after = @call_schedule.periods_before_after_time(@call_time)
      prev_teacher = @user_schedule[before.block] || 'an unknown teacher'
      next_teacher = @user_schedule[after.block] || 'an unknown teacher'
      return "You are traveling from Block #{before.block} with #{prev_teacher} to Block #{after.block} with #{next_teacher}"

    else
      throw ArgumentError, 'Unknown situation'
    end
  end
  def render_schedule_field(embed)
    target_day = Calendar.current.day_on @target_date
    target_schedule = Schedule.of_day target_day

    if target_schedule.nil?
      embed.add_field(
               name: "#{date_expr(@target_date)}: Unknown schedule (#{target_day.description})",
               value: '_No schedule is available for this day_')
      return
    end

    prev_index, next_index = target_schedule.periods_indices_before_after_time(@call_time)
    field_value = target_schedule.periods.map.with_index do |p, i|
      teacher = @user_schedule[p.block]
      content = teacher.nil? ? p.block : p.block + " → " + teacher

      if [Situation::DURING_PERIOD, Situation::BETWEEN_PERIODS].include? @situation
        if i < prev_index
          next "~~#{content}~~"
        end
        if i == prev_index
          next "_#{content}_"
        end
        if i == next_index
          next "**#{content}**"
        end
      end
      next content
    end.join("\n")

    embed.add_field(
             name: "#{relative_expr(@target_date).capitalize}: Blocks and #{teacher_expr}",
             value: field_value)

    unless @call_schedule.nil?
      _, period = @call_schedule.periods_before_after_time(@call_time)
      embed.color = period.nil? ? nil : ScheduleColor::for(period.block)
    end
  end

  private

  module Situation
    BEFORE_SCHOOL = 0
    DURING_PERIOD = 1
    BETWEEN_PERIODS = 2
    AFTER_SCHOOL = 3
    ON_HOLIDAY = 4
    UNKNOWN = 5
  end

  module ScheduleColor
    def self.for(block)
      {
          A: 0xBDBDBD, B: 0xFCFCFC, C: 0xFFA000, D: 0x0288D1,
          E: 0xFFEB3B, F: 0x388E3C, G: 0x7B1FA2, H: 0xD32F2F
      }[block.to_sym]
    end
  end

  def relative_expr(date)
    today = Date.today

    case date
    when today
      return 'today'
    when today.next
      return 'tomorrow'
    when today.prev_day
      return 'yesterday'
    else
      return date.strftime('%A') if date.cweek == today.cweek
      return "next #{date.strftime('%A')}" if date.cweek == (today.cweek+1) % 53

      return date.strftime('%B %-d, %Y')
    end
  end

  def date_expr(date)
    date.strftime('%B %-d, %Y')
  end

  def teacher_expr
    Random.rand < 0.02 ? 'Prison Guards Crossed with Babysitters' : 'Teachers'
  end
end
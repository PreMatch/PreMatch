require './calendar'
require './schedule'

module Bot
  def self.initialize
    @calendar = Calendar.current
  end

  def self.response_to(command, call_time)
    call_date = call_time.to_date

    return 'We are not in the currently defined calendar year.' unless
        @calendar.includes? call_date

    call_day = @calendar.day_on call_date

    case call_day
    when Holiday
      return "Enjoy your day off! Today is #{call_day.description}. Next school day is #{@calendar.next_nonholiday(call_date)}"
    when UnknownDay
      return "Today is #{call_day.name}, but I do not know what the schedule is."
    else
      schedule = Schedule.of_day(call_day)
    end
  end
end

function leadingZero(num) {
    return num < 10 ? "0" + num.toString() : num.toString();
}

function countdown(endDate) {
    let days, hours, minutes, seconds;

    if (isNaN(endDate)) {
        return;
    }

    let intervalInitialized = false;

    updateCountDown();

    let updateInterval = setInterval(updateCountDown, 1000);
    intervalInitialized = true;

    function updateCountDown() {
        let startDate = new Date();

        let timeRemaining = endDate.getTime() - startDate.getTime();

        if (timeRemaining >= 0) {
            seconds = Math.floor((endDate - (startDate)) / 1000);
            minutes = Math.floor(seconds / 60);
            hours = Math.floor(minutes / 60);
            days = Math.floor(hours / 24);

            hours = hours - (days * 24);
            minutes = minutes - (days * 24 * 60) - (hours * 60);
            seconds = seconds - (days * 24 * 60 * 60) - (hours * 60 * 60) - (minutes * 60);

            // Update timer HTML
            let countdownTimer = $('#countdown-timer');

            let countdown = countdownTimer.children('.container').first().children('.countdown-text').first();

            countdown.children('.countdown-days').html(`${leadingZero(days)}<span class="timer-subtitle" id="days-subtitle">Days</span>`);
            countdown.children('.countdown-hours').html(`${leadingZero(hours)}<span class="timer-subtitle" id="hours-subtitle">Hours</span>`);
            countdown.children('.countdown-minutes').html(`${leadingZero(minutes)}<span class="timer-subtitle" id="minutes-subtitle">Minutes</span>`);
            countdown.children('.countdown-seconds').html(`${leadingZero(seconds)}<span class="timer-subtitle" id="seconds-subtitle">Seconds</span>`);
        } else {
            if (intervalInitialized)
                clearInterval(updateInterval);

            // Make sure there is a blank timer

            let countdown = $('#countdown-timer').children('.container').first().children('.countdown-text').first();

            countdown.children('.countdown-days').html('00<span class="timer-subtitle" id="days-subtitle">Days</span>');
            countdown.children('.countdown-hours').html('00<span class="timer-subtitle" id="hours-subtitle">Hours</span>');
            countdown.children('.countdown-minutes').html('00<span class="timer-subtitle" id="minutes-subtitle">Minutes</span>');
            countdown.children('.countdown-seconds').html('00<span class="timer-subtitle" id="seconds-subtitle">Seconds</span>');

            // Update title
            $('#stay-tuned').html("They're Here!");

            // Update subtitle
            $('#subtitle').html("Schedules for the coming school year have been released on <a href='https://ma-andover.myfollett.com/aspen/logon.do' target='_blank'>Aspen!</a>");

            // Update estimate
            $("#estimate").html(`Schedules were released on: ${$('#estimate').children('strong')[0].outerHTML}`);

            // Change title
            $('title').first().html('Schedules Are Out!');
        }
    }
}

// Month here is 1-indexed (January is 1, February is 2, etc). This is
// because we're using 0 as the day so that it returns the last day
// of the last month, so you have to add 1 to the month number
// so it returns the correct amount of days
function daysInMonth(month, year) {
    return new Date(year, month, 0).getDate();
}

jQuery.getJSON('/static/calendar.json', (data) => {
    let releaseDate = data.schedule_release;

    let releaseDateData = releaseDate.split('T');

    let dateData = releaseDateData[0].split('-');

    let year = parseInt(dateData[0]), month = parseInt(dateData[1]) - 1, day = parseInt(dateData[2]); // 1 is subtracted from the month because the UTC constructor takes values between 0 and 11

    let timeData = releaseDateData[1].split(':');
    let hour = parseInt(timeData[0]), minute = parseInt(timeData[1]), second = parseInt(timeData[2]);

    // Get EST release date string
    let monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

    let suffix = 'th';

    if (day % 10 === 1)
        suffix = 'st';
    else if (day % 10 === 2)
        suffix = 'nd';
    else if (day % 10 === 3)
        suffix = 'rd';

    let timeEnding = 'AM';

    if (hour >= 12)
        timeEnding = 'PM';


    let finalHour = hour % 12;

    if (finalHour === 0)
        finalHour = 12;

    let timeOfRelease = `${monthNames[month]} ${day}<sup>${suffix}</sup>, at ${finalHour}:${leadingZero(minute)} ${timeEnding}`;

    $('#schedule-release-time').html(timeOfRelease);

    // Adjust time from EST to UTC
    hour += 4;

    // Adjust day if needed
    if (hour > 23) {
        day++;
        hour %= 24;

        // Adjust month if needed
        if (day > daysInMonth(month + 1, year)) {
            month++;
            day = 1;

            // Adjust year i needed
            if (month > 11) {
                year++;
                month = 0;
            }
        }
    }

    let endDate = new Date(Date.UTC(year, month, day, hour, minute, second)); // Should be in UTC time
    countdown(endDate);
});


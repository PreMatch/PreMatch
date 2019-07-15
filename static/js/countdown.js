function countdown(endDate) {
    let days, hours, minutes, seconds;

    if (isNaN(endDate)) {
        return;
    }

    updateCountDown();
    let updateInterval = setInterval(updateCountDown, 1000);

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

            countdown.children('.countdown-days').html(days.toString());
            countdown.children('.countdown-hours').html(hours.toString());
            countdown.children('.countdown-minutes').html(minutes.toString());
            countdown.children('.countdown-seconds').html(seconds.toString());
        } else {
            clearInterval(updateInterval);
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
    let release_date = data.schedule_release;
    let release_time = data.release_time_est;

    let date_data = release_date.split('-');

    let year = parseInt(date_data[0]), month = parseInt(date_data[1]) - 1, day = parseInt(date_data[2]); // 1 is subtracted from the month because the UTC constructor takes values between 0 and 11

    let time_data = release_time.split(':');
    let hour = parseInt(time_data[0]), minute = parseInt(time_data[1]), second = parseInt(time_data[2]);

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


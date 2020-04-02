function decodeEscapes(str) {
    return str.replace(/&#(\d+);/g, function (match, dec) {
        return String.fromCharCode(dec);
    });
}

function adjustLinkHolderWidths() {
    let linkHolder = $(`#link-holder`);
    let input = $(`#teacherInput`);

    linkHolder.css({
        'width': `${input.outerWidth() + 2}px`,
        'min-width': `${input.outerWidth() + 2}px`,
    });
}

$(window).on('resize', () => {
    adjustLinkHolderWidths();
});

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
function debounce(func, wait, immediate) {
    let timeout;

    return function executedFunction() {
        let context = this;
        let args = arguments;

        let later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };

        let callNow = immediate && !timeout;

        clearTimeout(timeout);

        timeout = setTimeout(later, wait);

        if (callNow) func.apply(context, args);
    };
}

function getResults(query) {
    $.ajax({
            async: true,
            url: '/api/student/search',
            data: JSON.stringify({query: query}),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            type: 'POST',
            success: (response) => {
                let results = response.results;
                let returnArr = [];

                results.forEach((result) => {
                    let arr = [result.name, result.handle];
                    if (result.handle !== userHandle)
                        returnArr.push(arr);
                });

                if (returnArr.length === 0) {
                    $('#no-results').show();
                } else {
                    returnArr.reverse();
                    $('#no-results').hide();
                    returnArr.forEach((partner) => {
                        $('#link-holder').prepend(`<a class="partner-result" onclick="selectPartner(&quot;${partner[1]}&quot;, &quot;${partner[0]}&quot;)">${partner[0]}</a>`);
                    });
                }

                $('#loader').hide();
            },
            error: () => {
                $('#loader').hide();
                $('#no-results').show();
            }
        }
    )
}

let partnerSearch = debounce(() => {
    let input = $('#teacherInput');
    let query = input.val();

    if (query.length === 0) {
        $('#link-holder').hide();
    } else {
        $('.partner-result').remove();
        $('#no-results').hide();
        $('#link-holder').show();
        getResults(query);
    }
}, 500);

function selectPartner(handle, name) {
    $('#entry-section').css('top', '-100%');
    $('#loading-section').css('bottom', '0');

    showMatchRating(handle, name)
}

function showMatchRating(theirHandle, theirName) {
    $.ajax({
        async: true,
        url: '/match/rate',
        data: JSON.stringify({
            handle1: theirHandle,
            handle2: userHandle
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        type: 'POST',
        success: (response) => {
            let matchScore = response;

            $('#partner-name').html(theirName);
            $('#partner-handle').html(theirHandle);

            $('#match-score').html(`${Math.round(matchScore * 100)}%`);

            let classification;

            if (matchScore >= 0.9)
                classification = "Soul Mates!";
            else if (matchScore >= 0.75)
                classification = "Great Match!";
            else if (matchScore >= 0.6)
                classification = "Pretty Good!";
            else if (matchScore >= 0.4)
                classification = "Nothing Special";
            else if (matchScore >= 0.2)
                classification = "Permanent Friend Zone";
            else
                classification = "No Chance :(";

            $('#classification-box').text(classification);
            applyHeartColor(matchScore);

            setTimeout(() => {
                $('#loading-section').css('bottom', '100%');
                $('#score-section').css('bottom', '0');
            }, 1000);
        },
        error: () => {
            reset();
        }
    });
}

function reset() {
    $('#loading-section').css('bottom', '0%');
    $('#score-section').css('bottom', '-100%');

    $('#teacherInput').val("");
    $('.partner-result').remove();
    $('#no-results').hide();
    $('#link-holder').hide();

    $('#entry-section').css('top', '0');
    $('#loading-section').css('bottom', '-100%');
}

function presearch() {
    partnerSearch();
    adjustLinkHolderWidths();
    $('#loader').show();
    $('#no-results').hide();

    if ($('#teacherInput').val().length > 0)
        $('#link-holder').show();
    else
        $('#link-holder').hide();
}

function applyHeartColor(rating) {
    // max: #D32F2F (211, 47, 47)
    const multiplier = (1 - Math.cos(Math.PI * rating)) / 2;
    const rgb = [211, 47, 47].map(comp => comp * multiplier);
    const rgbCss = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;

    $('#heart-path').css('fill', rgbCss);
    // jQuery doesn't understand !important using .css(...)
    $('#classification-box').attr('style', 'display: inline-block; padding: 5px; background-color: ' + rgbCss + ' !important');
}
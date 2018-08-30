let originalMargin = 20;
let rows = [1, 2, 3];

function getPixelValue(element, property) {
    return parseInt($(element).css(property).replace("px", ""));
}

function getTableMargin(period) {
    return getPixelValue(document.getElementById(`card-table-${ period }`), 'margin-bottom');
}

function getTableHeight(period) {
    return $(`#card-table-${ period }`).innerHeight() + getTableMargin(period);
}

function findBiggestSet(sets) {
    let biggest = -1;
    let biggestIndex;

    for (let i = 0; i < sets.length; i++) {
        let val = sets[i][1];
        if (val > biggest) {
            biggest = val;
            biggestIndex = i;
        }
    }

    return biggestIndex;
}

function orderTableHeights(row) {
    let heights = [];

    $(`#row-${row}`).children('div').each((indx, card) => {
        let cardPeriod = card.id.slice(-1);
        let cardHeight = getTableHeight(cardPeriod);
        heights.push([cardPeriod, cardHeight]);
    });

    let numSorted = 0;
    let currentArr = heights;
    let finalArr = [];

    while (numSorted <= heights.length + 1) {
        let biggestIndx = findBiggestSet(currentArr);
        finalArr.push(currentArr[biggestIndx]);

        currentArr.splice(biggestIndx, 1);

        numSorted++;
    }

    return finalArr;

}

function getRowFromPeriod(period) {
    let periods = 'ABCDEFG'.split('');
    let index = periods.indexOf(period);

    if (index !== -1) {
        if (index <= 2) {
            return 1;
        } else if (index <= 5) {
            return 2;
        } else {
            return 3;
        }
    }
}

function adjustMargin(row) {
    if ($(window).width() >= 1400) {
        let heights = orderTableHeights(row);
        let biggestHeight = heights[0][1];

        $(`#row-${ row }`).children('div').each((idx, crd) => {

            let period = crd.id.slice(-1);

            let card = $(`#roster-card-${ period }`);

            let heightDiff = biggestHeight - getTableHeight(period);

            card.css('margin-bottom', originalMargin + heightDiff);

            $(`#table-container-${ period }`).css('height', getTableHeight(period));
        });

    } else {
        $(`#row-${ row }`).children('div').each((indx, card) => {
            $(card).css('margin-bottom', originalMargin);
        });
    }
}

function expandCard(period) {
    let expandBtn = $(`#expand-btn-${period}`);
    let rosterBtn = $(`#btm-container-${ period }`);
    let tableCont = $(`#table-container-${ period }`);

    let originalHeight = getTableHeight(period);

    tableCont.css('height', originalHeight);

    let tbody = $(`#card-table-${ period }`).children();

    tbody.children('tr').each((indx, row) => {
        $(row).show();
    });

    let newHeight = getTableHeight(period);

    tableCont.css('height', newHeight);

    if ($(window).width() >= 1400) {
        let row = getRowFromPeriod(period);

        let heights = orderTableHeights(row);
        let biggestHeight = heights[0][1];

        if (period === heights[0][0] || newHeight >= biggestHeight) {
            $(`#row-${ row }`).children('div').each((indx, card) => {
                let cardPeriod = card.id.slice(-1);

                if (cardPeriod === period) {
                    $(card).css('margin-bottom', originalMargin);
                } else {
                    $(card).css('margin-bottom', originalMargin + (newHeight - getTableHeight(cardPeriod)))
                }

            });
        } else {
            let card = $(`#roster-card-${ period }`);

            let heightDiff = biggestHeight - newHeight;

            card.css('margin-bottom', originalMargin + heightDiff);
        }
    }

    expandBtn.hide();
    rosterBtn.show();
}

function setOriginalMargin() {
    originalMargin = getPixelValue(document.getElementsByClassName('roster-card')[0], 'margin-bottom');
}


$(window).resize(() => {
    rows.forEach((row) => adjustMargin(row));
    $('.table-container').each((index, container) => {
        let period = container.id.slice(-1);
        $(container).addClass('notransition'); // Disable transitions
        $(container).css('height', getTableHeight(period));
        $(container)[0].offsetHeight; // Trigger a reflow, flushing the CSS changes
        $(container).removeClass('notransition'); // Re-enable transitions
    });
});

function collapseCard(period) {
    let expandBtn = $(`#expand-btn-${period}`);
    let rosterBtn = $(`#btm-container-${ period }`);
    let tableCont = $(`#table-container-${ period }`);

    let originalHeight = getTableHeight(period);

    tableCont.css('height', originalHeight);

    let tbody = $(`#card-table-${ period }`).children();

    tbody.children('tr').each((indx, row) => {
        if (indx > 9) {
            $(row).hide();
        }
    });

    let newHeight = getTableHeight(period);

    tableCont.css('height', newHeight);

    adjustMargin(getRowFromPeriod(period));

    expandBtn.show();
    rosterBtn.hide();
}
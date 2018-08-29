function expandCard(period) {

}

function cutTable(period) {
    let table = $(`#card-table-${period}`);

    table.children('tbody').children('tr').each((indx, row) => {
        if (indx > 9) {
            $(row).hide();
        }
    });
}
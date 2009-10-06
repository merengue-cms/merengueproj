function getLocalDate(date) {
    return date.getISODate();
}

function getISODateFromLocalDate(datestr) {
    var date_list = datestr.split('-');
    var year = date_list[0];
    var month = date_list[1]-1;
    var day = date_list[2];
    var date = new Date(year, month, day);
    return date.getISODate();
}

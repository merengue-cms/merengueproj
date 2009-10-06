function getLocalDate(date) {
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    return (day<10?'0':'') + day + '/' + (month<10?'0':'') + month + '/' + date.getFullYear();
}

function getISODateFromLocalDate(datestr) {
    var date_list = datestr.split('/');
    var year = date_list[2];
    var month = date_list[1]-1;
    var day = date_list[0];
    var date = new Date(year, month, day);
    if (date == 'Invalid Date')
        return ""
    return date.getISODate();
}

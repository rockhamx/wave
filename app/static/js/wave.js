//
function follow(elementid, username) {
    $.post('/follow', {
        'username': username
    }).done(function (response) {
        $(elementid).text(response['status']);
        $('#followers').text(function (index, text) {
            return parseInt(text) + 1
        })
        $(elementid).attr('onclick', `unfollow(this, "${username}")`)
        $(elementid).toggleClass('btn-default btn-primary')
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}
function unfollow(elementid, username) {
    $.post('/unfollow', {
        'username': username
    }).done(function (response) {
        $(elementid).text(response['status']);
        $('#followers').text(function (index, text) {
            return parseInt(text) - 1
        })
        $(elementid).attr('onclick', `follow(this, "${username}")`)
        $(elementid).toggleClass('btn-default btn-primary')
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}

//
function follow(org_username, dst_username) {
    $.post('/follow', {
        'username': dst_username
    }).done(function (response) {
        const elementclass = '.follow' + dst_username
        $(elementclass).text(response['status'])
        $(elementclass).attr('onclick', `unfollow("${org_username}", "${dst_username}")`)
        $(elementclass).toggleClass('btn-default btn-primary')
        $('#followers').text(function (index, text) {
            return parseInt(text) + 1
        })
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}
function unfollow(org_username, dst_username) {
    $.post('/unfollow', {
        'username': dst_username
    }).done(function (response) {
        const elementclass = '.follow' + dst_username
        $(elementclass).text(response['status'])
        $(elementclass).attr('onclick', `follow("${org_username}", "${dst_username}")`)
        $(elementclass).toggleClass('btn-default btn-primary')
        $('#followers').text(function (index, text) {
            return parseInt(text) - 1
        })
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}

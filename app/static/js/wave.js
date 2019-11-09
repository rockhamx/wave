//
$( document ).ready(function () {
    // navbar-brand fixed
    $(".navbar-brand")[0].childNodes[0].textContent = "";

    // progress bar
    let progressBar = $('#progress-bar');
    progressBar.css('display', 'none');

    // navbar activation
    var url = window.location["pathname"];
    // Will only work if string in href matches with location
    $('ul.nav a[href="'+ url +'"]').parent().addClass('active');

    // articles infiniteScroll
    let articles = $('.articles');
    if (articles.length) {
        articles.infiniteScroll({
            path: ".pagination__next",
            append: ".article-preview",
            history: false,
        });
    }

    // delete button
    $('.delete_post').click(function (event) {
        // const prompt = "{{_('Are you sure to delete this post?')}}"
        const prompt = "您确定要删除这篇文章吗？";
        if (!window.confirm(prompt)) {
            return;
        }
        const id = parseInt(event.target.id);
        // console.log(id);
        $.post('/delete_post', {
            'id': id
        }).done(function (response) {
            const result = response['status'];
            if (result === 'Success') {
                let e = $('.article-preview').has('#' + id);
                console.log(e);
                e.remove()
            }
            // alert(response["result"])
            event.target.remove()
        })
    })
});

function follow(org_username, dst_username) {
    $.post('/follow', {
        'username': dst_username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            let e = $('.f' + dst_username);
            e.text(response['status']);
            e.attr('onclick', `unfollow("${org_username}", "${dst_username}")`);
            // $(elementclass).click([org_username, dst_username], unfollow)
            e.toggleClass('btn-default btn-primary');
            $('#followers').text(function (index, text) {
                return parseInt(text) + 1
            })
        }
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}
function unfollow(org_username, dst_username) {
    $.post('/unfollow', {
        'username': dst_username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            let e = $('.f' + dst_username);
            e.text(response['status']);
            e.attr('onclick', `follow("${org_username}", "${dst_username}")`);
            e.toggleClass('btn-default btn-primary');
            $('#followers').text(function (index, text) {
                return parseInt(text) - 1
            })
        }
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}

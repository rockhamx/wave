'use strict';
$(document).ready(function () {
    // navbar-brand fixed
    $(".navbar-brand")[0].childNodes[0].textContent = "";

    // progress bar
    let progressBar = $('#progress-bar');
    progressBar.css('display', 'none');

    // navbar activation
    let url = window.location["pathname"];
    // Will only work if string in href matches with location
    $('ul.nav a[href="' + url + '"]').parent().addClass('active');
    // nav-tabs activation
    url = window.location["pathname"];
    let $nav_tabs = $('ul.nav-tabs a[href="' + url + '"]');
    if ($nav_tabs) {
        $nav_tabs.parent().addClass('active');
    }

    // articles infiniteScroll
    let $articles = $('div.articles');
    if ($articles.length) {
        $articles.infiniteScroll({
            path: ".pagination__next",
            append: ".article-preview",
            history: false,
        });
    }
    // users infiniteScroll
    let $users = $('div.users');
    if ($users.length) {
        $users.infiniteScroll({
            path: ".pagination__next",
            append: ".user-preview",
            history: false,
        });
    }
});

// Event listeners
// Search button
$('button#search').click(function (event) {
    const query = $(this).parent().siblings('.form-control').val();
    if (query !== "") {
        window.location = "/search?q=" + query
    }
});

// Confirm modal
$('#confirmModal').on('show.bs.modal', function (event) {
    let $modal = $(this);
    let $trigger = $(event.relatedTarget);
    $modal.find('button.btn-primary').click(function (event) {
        $.post('/delete_post', {
            'id': $trigger.data('id')
        }, function (data) {
            if (data['status'] === 'Success') {
                $modal.modal('hide');
                $trigger.parents('div.article-preview').fadeOut().remove()
                // TODO: flash a message here
            }
        })
    })
});

// React
const e = React.createElement;

class LikeButton extends React.Component {
    constructor(props) {
        super(props);
        this.state = {liked: false};
    }

    render() {
        if (this.state.liked) {
            return 'You liked this.';
        }

        return e(
            'button',
            {onClick: () => this.setState({liked: true})},
            'Like'
        );
    }
}

const domContainer = document.querySelector('#like_button_container');
ReactDOM.render(e(LikeButton), domContainer);


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
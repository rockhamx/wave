'use strict';

$(document).ready(function () {
    // navbar-brand fixed
    // $(".navbar-brand")[0].childNodes[0].textContent = "";

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

// Event listeners
// Follow buttons
    $('button.btn-follow').each(function () {
        let $button = $(this);
        if ($button.data('state') === 'following') {
            $button.click(function (event) {
                unfollow($button.data('author'))
            })
        } else {
            $button.click(function (event) {
                follow($button.data('author'))
            })
        }
    });

    // Hearts button
    // $('')

// Search button
    let search = function (event) {
        const query = $(this).parent().siblings('.form-control').val();
        if (query !== "") {
            window.location = "/search?q=" + query
        }
    };
    let $search = $('button#search');
    if ($search.length > 0) {
        $search.click(function (event) {
            const query = $(this).parent().siblings('.form-control').val();
            window.location = "/search?q=" + query
        });
        $search.parent().siblings().keypress(function (event) {
            if (event.which == 13) {
                const query = $(this).val();
                window.location = "/search?q=" + query
            }
        })
    }

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

});


window.follow = function (username) {
    $.post('/follow', {
        'username': username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            let $e = $('.' + username);
            $e.text(response['status']);
            $e.toggleClass('btn-default btn-primary');
            $e.click(function (event) {
                unfollow(username)
            });
            $('#followers').text(function (index, text) {
                return parseInt(text) + 1
            })
            // $e.attr('onclick', `unfollow("${username}")`);
            // $(elementclass).click([org_username, dst_username], unfollow)
        }
    }).fail(function () {
        alert('fail');
        //flash a message
    });
};

window.unfollow = function (username) {
    $.post('/unfollow', {
        'username': username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            let $e = $('.' + username);
            $e.text(response['status']);
            $e.toggleClass('btn-default btn-primary');
            $e.click(function (event) {
                follow(username)
            });
            $('#followers').text(function (index, text) {
                return parseInt(text) - 1
            })
        }
    }).fail(function () {
        alert('fail');
        //flash a message
    });
};
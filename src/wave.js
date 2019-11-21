'use strict';

$(document).ready(function () {
    // progress bar
    let progressBar = $('#progress-bar');
    progressBar.css('display', 'none');

    // nav-bar activation
    let href = window.location["pathname"];
    // Will only work if string in href matches with location
    $('ul.nav a[href="' + href + '"]').parent().addClass('active');

    // nav-tabs activation
    href = href + window.location['search'];
    $('ul.nav-tabs a[href="' + href + '"]').parent().addClass('active');

    // articles infiniteScroll
    let $articles = $('div.articles');
    if ($articles.children().length > 9) {
        $articles.infiniteScroll({
            path: ".pagination__next",
            responseType: "document",
            append: ".article-preview",
            history: false,
        });
    }
    // users infiniteScroll
    let $users = $('div.users');
    if ($users.children().length > 9) {
        $users.infiniteScroll({
            path: ".pagination__next",
            responseType: "document",
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
    $('.hearts').click(function (event) {
        event.preventDefault();
        let which = this;
        $.post('/api/v0/like/' + which.dataset.id, function (data) {
            if (data['status'] === 'success') {
                let val = parseInt(which.innerText);
                $(which).children().eq(1).text(val + 1)
            }
        })
    });

// Search bar and button
    let $search = $('button#search');
    if ($search.length > 0) {
        $search.click(function (event) {
            const query = $(this).parent().siblings('.form-control').val();
            if (query !== "") {
                pwindow.location.href = window.location.origin + '/search' + "?q=" + query
            }
        });
    }
    let $searchBars = $('div.search').find('input.form-control');
    $searchBars.keypress(function (event) {
        if (event.which == 13) {
            const query = $(this).val();
            if (query !== "") {
                window.location.href = window.location.origin + '/search' + "?q=" + query
            }
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
'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

$(document).ready(function () {
    // navbar-brand fixed
    $(".navbar-brand")[0].childNodes[0].textContent = "";

    // progress bar
    var progressBar = $('#progress-bar');
    progressBar.css('display', 'none');

    // navbar activation
    var url = window.location["pathname"];
    // Will only work if string in href matches with location
    $('ul.nav a[href="' + url + '"]').parent().addClass('active');
    // nav-tabs activation
    url = window.location["pathname"];
    var $nav_tabs = $('ul.nav-tabs a[href="' + url + '"]');
    if ($nav_tabs) {
        $nav_tabs.parent().addClass('active');
    }

    // articles infiniteScroll
    var $articles = $('div.articles');
    if ($articles.length) {
        $articles.infiniteScroll({
            path: ".pagination__next",
            append: ".article-preview",
            history: false
        });
    }
    // users infiniteScroll
    var $users = $('div.users');
    if ($users.length) {
        $users.infiniteScroll({
            path: ".pagination__next",
            append: ".user-preview",
            history: false
        });
    }
});

// Event listeners
// Search button
$('button#search').click(function (event) {
    var query = $(this).parent().siblings('.form-control').val();
    if (query !== "") {
        window.location = "/search?q=" + query;
    }
});

// Confirm modal
$('#confirmModal').on('show.bs.modal', function (event) {
    var $modal = $(this);
    var $trigger = $(event.relatedTarget);
    $modal.find('button.btn-primary').click(function (event) {
        $.post('/delete_post', {
            'id': $trigger.data('id')
        }, function (data) {
            if (data['status'] === 'Success') {
                $modal.modal('hide');
                $trigger.parents('div.article-preview').fadeOut().remove();
                // TODO: flash a message here
            }
        });
    });
});

// React
var e = React.createElement;

var LikeButton = function (_React$Component) {
    _inherits(LikeButton, _React$Component);

    function LikeButton(props) {
        _classCallCheck(this, LikeButton);

        var _this = _possibleConstructorReturn(this, (LikeButton.__proto__ || Object.getPrototypeOf(LikeButton)).call(this, props));

        _this.state = { liked: false };
        return _this;
    }

    _createClass(LikeButton, [{
        key: "render",
        value: function render() {
            var _this2 = this;

            if (this.state.liked) {
                return 'You liked this.';
            }

            return e('button', { onClick: function onClick() {
                    return _this2.setState({ liked: true });
                } }, 'Like');
        }
    }]);

    return LikeButton;
}(React.Component);

var domContainer = document.querySelector('#like_button_container');
ReactDOM.render(e(LikeButton), domContainer);

function follow(org_username, dst_username) {
    $.post('/follow', {
        'username': dst_username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            var _e = $('.f' + dst_username);
            _e.text(response['status']);
            _e.attr('onclick', "unfollow(\"" + org_username + "\", \"" + dst_username + "\")");
            // $(elementclass).click([org_username, dst_username], unfollow)
            _e.toggleClass('btn-default btn-primary');
            $('#followers').text(function (index, text) {
                return parseInt(text) + 1;
            });
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
            var _e2 = $('.f' + dst_username);
            _e2.text(response['status']);
            _e2.attr('onclick', "follow(\"" + org_username + "\", \"" + dst_username + "\")");
            _e2.toggleClass('btn-default btn-primary');
            $('#followers').text(function (index, text) {
                return parseInt(text) - 1;
            });
        }
    }).fail(function () {
        alert('fail');
        //flash a message
    });
}
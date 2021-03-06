"use strict";

import $ from "jquery"

$(document).ready(function () {
    // progress bar
    let progressBar = $("#progress-bar");
    progressBar.css("display", "none");

    // nav-bar activation
    let href = window.location["pathname"];
    // Will only work if string in href matches with location
    $("ul.nav a[href=\"" + href + "\"]").parent().addClass("active");

    // profile nav-tabs activation
    const profileNavTab = $("ul.nav-tabs a[href^=\"" + href + "?\"]");
    if (profileNavTab[0]) {
        profileNavTab.parent().addClass("active");
    } else {
        // search nav-tabs activation
        const searchHref = href + decodeURI(window.location["search"]);
        $("ul.nav-tabs a[href=\"" + searchHref + "\"]").parent().addClass("active");
    }

    // flash messages
    const messages = localStorage.getItem("messages");
    if (messages) {
        $(messages).appendTo(".alerts");
        localStorage.setItem("messages", "");
    }

    // articles infiniteScroll
    let $articles = $("div.articles");
    if ($articles.children().length > 9) {
        $articles.infiniteScroll({
            path: ".pagination__next",
            responseType: "document",
            append: ".article-preview",
            history: false,
        });
    }
    // user infiniteScroll
    let $users = $("div.user");
    if ($users.children().length > 9) {
        $users.infiniteScroll({
            path: ".pagination__next",
            responseType: "document",
            append: ".user-preview",
            history: false,
        });
    }

    // themes
    let themesSelect = $("select#theme");
    if (themesSelect) {
        themesSelect.change(function () {
            const css = $(this).val();
            $("link#bootstrap").attr("href", css);
        });
    }

    // Search bar keydown event
    let $searchBars = $("input#search");
    $searchBars.keypress(function (event) {
        if (event.which === 13) {
            const query = $(this).val();
            if (query !== "") {
                window.location.href = window.location.origin + window.location.pathname + "?q=" + query;
            }
        }
    });

    // newMessage button
    $("#newMessage").click(function (event) {
        location.href = "/send_message"
    })

    // Follow and Un_follow buttons click event
    $("button.btn-follow").each(function () {
        let $button = $(this);
        if ($button.data("state") === "following") {
            $button.click(function (event) {
                unfollow($button.data("author"));
            });
        } else {
            $button.click(function (event) {
                follow($button.data("author"));
            });
        }
    });

    // Follow publication buttons click event
    $("button.follow_publication").click(follow_publication);
    $("button.unfollow_publication").click(unfollow_publication);

    // Hearts button click event
    $(".hearts").click(function (event) {
        event.preventDefault();
        let which = this;
        const url = "/api/v0/hearts/" + this.dataset.id;
        const data = {
            amount: 1
        };
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: data => {
                if (data.status === "success") {
                    const val = parseInt($(which).find("span")[0].innerText);
                    const newVal = val + 1;
                    $(which).find(".material-icons")[0].innerText = "favorite";
                    $(which).find("span").eq(0).text(" " + newVal);
                }
                // if (data.message.text) {
                flash_message(data.message.text, data.message.type, data.next);
                // }
            }
        });
    });

    // Cancel hearts button click event
    $(".cancelHearts").click(function (event) {
        event.preventDefault();
        // let which = this;
        const post_id = this.dataset.id;
        const url = "/api/v0/hearts/" + parseInt(post_id);
        // Retrieve user hearts
        let jqXHR = $.ajax({
            url: url,
            type: "GET",
            dataType: "json"
        });

        const callback = data => {
            if (data.status !== "success") {
                console.log("failed");
                //TODO: flash message
                return;
            }
            const amount = data.amount;
            const $hearts = $(this).parents(".statusbar").find(".hearts");
            $.ajax({
                url: url,
                type: "DELETE",
                dataType: "json",
                success: data => {
                    if (data.status === "success") {
                        const valEl = $hearts.find("span")[0];
                        const newVal = parseInt(valEl.innerText) - parseInt(amount);
                        $hearts.find(".material-icons")[0].innerText = "favorite_border";
                        $hearts.find("span").text(" " + newVal);
                    }
                }
            });
        };

        jqXHR.done(
            callback
        );

    });

    // add bookmark button click event
    $(".addBookmark").click(add_bookmark);

    // remove bookmark button click event
    $(".removeBookmark").click(remove_bookmark);

    // messages badge update on navbar click event
    $("ul.navbar-nav.navbar-right").on("show.bs.dropdown", function (event) {
        const badge = $(this).find("li#messages").find("span.badge")[0];
        const url = "/api/v0/unread_messages/count";

        $.ajax({
            url: url,
            type: "GET",
            dataType: "json",
            success: (data) => {
                if (data.status === "success") {
                    // console.log("success");
                    if (data.count > 0)
                        badge.innerText = data.count;
                }
            }
        });
    });

    // messages marked read on click event
    $("div#receivedaccordion>.panel").on("show.bs.collapse", function (event) {
        const $which = $(this);
        const id = this.dataset.id;
        const url = "/api/v0/read/message/" + id;

        $.ajax({
            url: url,
            type: "POST",
            dataType: "json",
            success: (data) => {
                if (data.result === "success") {
                    $which.find(".panel-title").css({"color": "grey"})
                        .find("span#status").text(data.status);
                }
            }
        });
    });

    // Delete post confirmation modal
    $("#articleConfirmModal").on("show.bs.modal", function (event) {
        let $modal = $(this);
        let $btn = $(event.relatedTarget);
        $modal.find("button.btn-primary").click(function (event) {
            $modal.modal("hide");
            const url = "/api/v0/post/" + $btn.data("id");
            $.ajax({
                url: url,
                type: "DELETE",
                contentType: "application/x-www-form-urlencoded; charset=UTF-8",
                dataType: "json",
                success: data => {
                    if (data.status === "success") {
                        // TODO: flash a message here
                        if (data.next) {
                            window.location.href = data.next;
                        } else {
                            window.location.reload();
                        }
                        // const $article = $btn.parents("div.article-preview");
                        // $article.fadeOut().remove();
                        console.log(data.status);
                    }
                }
            });
        });
    });

    // Delete draft confirmation modal
    $("#draftConfirmModal").on("show.bs.modal", function (event) {
        let $modal = $(this);
        let $btn = $(event.relatedTarget);
        $modal.find("button.btn-primary").click(function (event) {
            $modal.modal("hide");
            const url = "/api/v0/draft/" + $btn.data("id");
            $.ajax({
                url: url,
                type: "DELETE",
                contentType: "application/x-www-form-urlencoded; charset=UTF-8",
                dataType: "json",
                success: data => {
                    if (data.result === "success") {
                        $btn.parents("div.article-preview").fadeOut().remove();
                        flash_message(data.message.text, data.message.type);
                    }
                }
            });
        });
    });

    // Delete comment confirmation modal
    $("#commentConfirmModal").on("show.bs.modal", function (event) {
        let $modal = $(this);
        let $btn = $(event.relatedTarget);
        $modal.find("button#confirmDelete").click(function (event) {
            $modal.modal("hide");
            const url = "/api/v0/comment/" + $btn.data("id");
            $.ajax({
                url: url,
                type: "DELETE",
                contentType: "application/x-www-form-urlencoded; charset=UTF-8",
                dataType: "json",
                success: data => {
                    if (data.result === "success") {
                        // TODO: flash a message here
                        $btn.parents("div.comment-preview").fadeOut().remove();
                        flash_message(data.message.text, data.message.type);
                        // window.location.reload();
                    }
                }
            });
        });
    });

    // publish button click event
    $("button#publishNow").click(function (event) {
        const $modal = $("#publishModalForRichText");
        const url = "/api/v0/posts/";
        const title = $modal.find("input#previewTitle").val();
        const subtitle = $modal.find("input#previewSubtitle").val();
        const description = $modal.find("textarea#description").val();
        const tags = $modal.find("input#addTags").val();
        const content = localStorage.getItem("draft_content");
        const isPublic = $modal.find("input#isPublic")[0].checked === "checked";
        const data = {
            title: title,
            subtitle: subtitle,
            description: description,
            tags: tags,
            content: content,
            isPublic: isPublic,
        };
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: data => {
                if (data.status === "success") {
                    localStorage.setItem("content", "");
                    window.location.pathname = "/article/" + data.id;
                }
            }
        });
    });

});

window.flash_message = function (message, type = "info", next = null) {
    if (!message && !next) return false;
    const $button = $("<button/>", {
        "type": "button",
        "class": "close",
        "data-dismiss": "alert",
        "aria-label": "Close"
    }).append($("<span/>", {
        "aria-hidden": "true",
        text: "x"
    }));
    const $div = $("<div/>", {
        "class": `alert alert-${type} fade in`,
        "role": "alert",
        text: message
    }).append($button);
    if (next) {
        localStorage.setItem("messages", $div.prop("outerHTML"));
        console.log($div.prop("outerHTML"));
        window.location.pathname = next;
    } else {
        $(".alerts").append($div);
    }
};

window.add_bookmark = function (event) {
    event.preventDefault();
    let which = this;
    const url = "/api/v0/bookmarks/" + this.dataset.id;
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        success: data => {
            if (data.status === "success") {
                $(which).toggleClass("addBookmark RemoveBookmark");
                $(which).find(".material-icons")[0].innerText = "bookmark";
                $(which).unbind("click");
                $(which).click(remove_bookmark);
                //TODO: flash message
                console.log(data.status);
            }
            // if (data.message.text) {
            flash_message(data.message.text, data.message.type, data.next);
            // }
        }
    });
};

window.remove_bookmark = function (event) {
    event.preventDefault();
    let which = this;
    const url = "/api/v0/bookmarks/" + this.dataset.id;
    $.ajax({
        url: url,
        type: "DELETE",
        dataType: "json",
        success: data => {
            if (data.status === "success") {
                $(which).toggleClass("addBookmark RemoveBookmark");
                $(which).find(".material-icons")[0].innerText = "bookmark_border";
                $(which).unbind("click");
                $(which).click(add_bookmark);
                //TODO: flash message
                console.log(data.status);
            }
        }
    });
};

window.follow_publication = function (event) {
    event.preventDefault();
    let which = this;
    const url = "/api/v0/follow/publication/" + this.dataset.id;
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        success: data => {
            if (data.result === "success") {
                $(which).toggleClass("follow_publication unfollow_publication");
                $(which).find("span.status")[0].innerText = data.status;
                $(which).find(".material-icons")[0].innerText = "keyboard_arrow_down";
                $(which).unbind("click");
                $(which).click(unfollow_publication);
                console.log(data.status);
            }
            flash_message(data.message.text, data.message.type, data.next);
        }
    });
};

window.unfollow_publication = function (event) {
    event.preventDefault();
    let which = this;
    const url = "/api/v0/unfollow/publication/" + this.dataset.id;
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        success: data => {
            if (data.result === "success") {
                $(which).toggleClass("follow_publication unfollow_publication");
                $(which).find("span.status")[0].innerText = data.status;
                $(which).find(".material-icons")[0].innerText = "";
                $(which).unbind("click");
                $(which).click(follow_publication);
                console.log(data.status);
            }
        }
    });

};

window.follow = (username) => {
    $.post("/follow", {
        "username": username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            let $e = $("." + username);
            $e.text(response["status"]);
            $e.toggleClass("btn-default btn-primary");
            $e.unbind("click");
            $e.click(function (event) {
                unfollow(username);
            });
            $("#followers").text(function (index, text) {
                return parseInt(text) + 1;
            });
            // flash_message(data.message.text, data.message.type, data.next);
            // $e.attr('onclick', `unfollow("${username}")`);
            // $(elementclass).click([org_username, dst_username], unfollow)
        }
    }).fail(function () {
        alert("fail");
        //flash a message
    });
};

window.unfollow = (username) => {
    $.post("/unfollow", {
        "username": username
    }).done(function (response) {
        if (!$.isEmptyObject(response)) {
            let $e = $("." + username);
            $e.text(response["status"]);
            $e.toggleClass("btn-default btn-primary");
            $e.unbind("click");
            $e.click(function (event) {
                follow(username);
            });
            $("#followers").text(function (index, text) {
                return parseInt(text) - 1;
            });
        }
    }).fail(function () {
        alert("fail");
        //flash a message
    });
};
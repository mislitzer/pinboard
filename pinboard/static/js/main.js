jq = jQuery.noConflict();

function setCookie(cookieName) {
    document.cookie.split(';').filter(item => {
        if (!item.trim().startsWith(`${cookieName}=`)) {
            document.cookie = `${cookieName}=${uuidv4()}`;
        }
    });
}

function getCookie(cookieName) {
    var foundCookie = "";
    document.cookie.split(';').filter(item => {
        if (item.trim().startsWith(`${cookieName}=`)) {
            foundCookie = item.replace(`${cookieName}=`, ``);
        }
        else {
            foundCookie = `cookie: ${cookieName} not found!`;
        }
    });
    return foundCookie;
}

function deleteCookie(cookieName) {
    document.cookie = `${cookieName}= ; expires = Thu, 01 Jan 1970 00:00:00 GMT`
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function likePost(button, postId, userSession) {
    jq.post("/like_post", {
        user_session: userSession,
        post_id: postId
    }, (data) => {
        if (data) {
            var posts = JSON.parse(data);
            var currentLikes = parseInt(button.attr("data-count"));
            var currentButtonHtml = button.html();
            var newLikes = currentLikes + 1;

            button.attr("data-count", newLikes);
            if (currentLikes > 0) {
                button.html(currentButtonHtml.replace(currentLikes, newLikes));
            }
            else {
                button.html(currentButtonHtml + ` (${newLikes})`);
            }

            button.attr("disabled", true);

            // sort posts
            if (posts) {
                posts.forEach((post, key) => {
                    var card = jq('.post-card[post-id="' + post.rowid + '"]');
                    card.css("order", key + 1);
                })
            }
        }
    });
}

jq(document).ready(function() {
    setCookie("pinboard_session");
    var userSession = getCookie("pinboard_session");
    var sessionBtnHtml = jq("#delete-session-btn").html();
    jq("#delete-session-btn").html(sessionBtnHtml.replace("()", "(" + userSession + ")"));

    jq(".like-button").click(function() {
        var parentCard = jq(this).parents(".post-card");
        var postId = parentCard.attr("post-id");

        likePost(jq(this), postId, userSession);
    });

    jq("#delete-session-btn").click(function() {
        window.location.reload();
        deleteCookie("pinboard_session");
    });
});